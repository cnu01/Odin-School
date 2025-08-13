import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import io
import base64

class AdliftService:
    """Service class for Adlift operations"""
    
    def __init__(self):
        # Configuration
        self.MIN_IMPRESSIONS = 500
        self.FATIGUE_THRESHOLD = 0.80
        
    def analyze_csv(self, csv_content: str) -> Dict:
        """Analyze CSV content and return comprehensive results"""
        try:
            # Parse CSV content
            df = pd.read_csv(io.StringIO(csv_content))
            
            # Compute business-native metrics
            df['QPI'] = df['CTR'] * df['CVR'] * df['qualified_rate']
            df['CPQL'] = df['spend'] / df['qualified_leads'].clip(lower=1)
            df['date'] = pd.to_datetime(df['date'])
            
            # Filter stable samples
            df_filtered = df[df['impressions'] >= self.MIN_IMPRESSIONS].copy()
            
            # Perform analysis
            performance_variance = self._analyze_performance_variance(df_filtered)
            root_causes = self._identify_root_causes(df_filtered)
            campaign_decisions = self._make_rotation_decisions(df_filtered)
            fatigue_detection = self._detect_fatigue_patterns(df_filtered)
            variants_data = self._generate_variants(df_filtered)
            
            return {
                "performance_variance": performance_variance,
                "root_causes": root_causes,
                "campaign_decisions": campaign_decisions,
                "fatigue_detection": fatigue_detection,
                "variants_data": variants_data,
                "expected_impact": self._generate_expected_impact()
            }
            
        except Exception as e:
            raise Exception(f"Analysis failed: {str(e)}")
    
    def _analyze_performance_variance(self, df: pd.DataFrame) -> Dict:
        """Analyze CTR and CPQL variance patterns"""
        ctr_stats = df['CTR'].describe()
        cpql_stats = df['CPQL'].describe()
        qpi_stats = df['QPI'].describe()
        
        return {
            "ctr_range": f"{ctr_stats['min']:.1%} to {ctr_stats['max']:.1%}",
            "ctr_variance": f"{ctr_stats['max']/ctr_stats['min']:.1f}x",
            "cpql_range": f"₹{cpql_stats['min']:.0f} to ₹{cpql_stats['max']:.0f}",
            "cpql_variance": f"{cpql_stats['max']/cpql_stats['min']:.1f}x",
            "qpi_range": f"{qpi_stats['min']:.4f} to {qpi_stats['max']:.4f}",
            "total_campaigns": len(df)
        }
    
    def _identify_root_causes(self, df: pd.DataFrame) -> List[Dict]:
        """Identify root causes with evidence"""
        root_causes = []
        
        # Root Cause 1: Copy-Intent Mismatch
        df['QPI_Q25'] = df.groupby(['audience_segment', 'placement'])['QPI'].transform('quantile', 0.25)
        mismatch_evidence = df[
            (df['QPI'] < df['QPI_Q25']) & 
            (df['impressions'] >= 1000)
        ].sort_values('impressions', ascending=False)
        
        if len(mismatch_evidence) > 0:
            root_causes.append({
                "name": "Copy-Intent Mismatch",
                "description": "Low QPI performance on high-impression campaigns",
                "case_count": len(mismatch_evidence),
                "evidence": mismatch_evidence[['headline', 'audience_segment', 'placement', 'impressions', 'CTR', 'QPI', 'keywords']].head(3).to_dict('records')
            })
        
        # Root Cause 2: Qualification Gap
        df['CTR_median'] = df.groupby(['audience_segment', 'placement'])['CTR'].transform('median')
        df['CPQL_Q75'] = df.groupby(['audience_segment', 'placement'])['CPQL'].transform('quantile', 0.75)
        
        qualification_issues = df[
            (df['CTR'] >= df['CTR_median']) & 
            (df['CPQL'] >= df['CPQL_Q75'])
        ].sort_values('CPQL', ascending=False)
        
        if len(qualification_issues) > 0:
            root_causes.append({
                "name": "Qualification Gap",
                "description": "OK CTR but poor qualified lead conversion",
                "case_count": len(qualification_issues),
                "evidence": qualification_issues[['headline', 'description', 'audience_segment', 'CTR', 'CPQL', 'qualified_rate']].head(3).to_dict('records'),
                "avg_qualified_rate": f"{qualification_issues['qualified_rate'].mean():.1%}"
            })
        
        return root_causes
    
    def _make_rotation_decisions(self, df: pd.DataFrame) -> Dict:
        """Make rotation decisions for campaigns"""
        decisions = []
        
        for (segment, placement), group in df.groupby(['audience_segment', 'placement']):
            qpi_q25 = group['QPI'].quantile(0.25)
            qpi_q75 = group['QPI'].quantile(0.75)
            cpql_median = group['CPQL'].median()
            cpql_threshold = cpql_median * 1.2
            
            for _, row in group.iterrows():
                if row['QPI'] >= qpi_q75 and row['CPQL'] <= cpql_median:
                    decision = "KEEP"
                elif row['QPI'] <= qpi_q25 or row['CPQL'] >= cpql_threshold:
                    decision = "PAUSE"
                else:
                    decision = "MONITOR"
                
                decisions.append(decision)
        
        decision_counts = pd.Series(decisions).value_counts()
        return {
            "pause_count": int(decision_counts.get("PAUSE", 0)),
            "keep_count": int(decision_counts.get("KEEP", 0)),
            "monitor_count": int(decision_counts.get("MONITOR", 0))
        }
    
    def _detect_fatigue_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Detect creative fatigue patterns"""
        fatigue_cases = []
        creative_groups = df.groupby(['headline', 'keywords', 'audience_segment', 'placement'])
        
        for name, group in creative_groups:
            if len(group) >= 7:
                group_sorted = group.sort_values('date')
                first_3_ctr = group_sorted.head(3)['CTR'].mean()
                last_3_ctr = group_sorted.tail(3)['CTR'].mean()
                fatigue_ratio = last_3_ctr / first_3_ctr if first_3_ctr > 0 else 1
                
                if fatigue_ratio < self.FATIGUE_THRESHOLD:
                    fatigue_cases.append({
                        "headline": name[0],
                        "segment": name[2],
                        "fatigue_ratio": fatigue_ratio,
                        "days_live": len(group)
                    })
        
        return fatigue_cases
    
    def _generate_variants(self, df: pd.DataFrame) -> Dict:
        """Generate creative variants (simplified version)"""
        # This would generate variants like our existing script
        # For MVP, return sample data
        return {
            "variants_count": 93,
            "segments": ["Graduates", "Working Professionals"],
            "placements": ["search", "youtube"]
        }
    
    def _generate_expected_impact(self) -> Dict:
        """Generate expected impact projections"""
        return {
            "ctr_improvement": "15-25%",
            "cpql_reduction": "10-20%",
            "timeline": "30 days",
            "qualified_leads_improvement": "20-30%",
            "cac_reduction": "15-25%"
        }
