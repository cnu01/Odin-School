import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import io
import base64
import sys
import os

# Add current directory to path to import existing scripts
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class AdliftService:
    """Service class for Adlift operations - INTEGRATES EXISTING LOGIC"""
    
    def __init__(self):
        # Import existing logic modules
        try:
            from analysis import load_and_prepare_data, analyze_performance_variance, identify_root_causes, detect_fatigue_patterns
            from variant_generator import extract_winning_patterns, generate_template_variants, make_rotation_decisions
            
            self.analysis_module = {
                'load_and_prepare': load_and_prepare_data,
                'analyze_variance': analyze_performance_variance,
                'identify_causes': identify_root_causes,
                'detect_fatigue': detect_fatigue_patterns
            }
            
            self.variant_module = {
                'extract_patterns': extract_winning_patterns,
                'generate_variants': generate_template_variants,
                'make_decisions': make_rotation_decisions
            }
            
            print("✅ Successfully imported existing analysis and variant generation logic")
            
        except ImportError as e:
            print(f"❌ Error importing existing modules: {e}")
            raise Exception("Failed to import existing analysis logic")
        
    def analyze_csv(self, csv_content: str) -> Dict:
        """Analyze CSV content using EXISTING logic from analysis.py and variant_generator.py"""
        try:
            print("🔄 Starting analysis using existing logic...")
            
            # Save CSV content to temporary file for existing scripts
            temp_csv_path = "temp_upload.csv"
            with open(temp_csv_path, 'w', encoding='utf-8') as f:
                f.write(csv_content)
            
            # Use existing analysis logic from analysis.py
            print("📊 Running existing analysis logic...")
            df_raw, df_filtered = self.analysis_module['load_and_prepare'](temp_csv_path)
            
            # Get performance variance using existing logic
            segment_stats = self.analysis_module['analyze_variance'](df_filtered)
            
            # Get root causes using existing logic
            mismatch_evidence, qualification_issues = self.analysis_module['identify_causes'](df_filtered)
            
            # Get fatigue detection using existing logic
            fatigue_df = self.analysis_module['detect_fatigue'](df_filtered)
            
            # Use existing variant generation logic from variant_generator.py
            print("🎯 Running existing variant generation logic...")
            top_performers, winning_bigrams = self.variant_module['extract_patterns'](df_filtered)
            
            # Get dynamic segments from actual data
            available_segments = df_filtered['audience_segment'].unique().tolist()
            available_placements = df_filtered['placement'].unique().tolist()
            
            # Generate variants using existing logic with DYNAMIC segments
            all_variants = []
            for segment in available_segments:
                for placement in available_placements:
                    headlines, descriptions = self.variant_module['generate_variants'](top_performers, segment)
                    
                    # Get dynamic fallback description from top performers
                    fallback_description = self._get_dynamic_fallback_description(top_performers, segment)
                    
                    # Create variant combinations (simplified for API response)
                    for i, headline in enumerate(headlines[:5]):  # Limit for API
                        all_variants.append({
                            'headline': headline,
                            'description': descriptions[min(i, len(descriptions)-1)] if descriptions else fallback_description,
                            'segment': segment,
                            'placement': placement,
                            'type': "winner-like" if i < 3 else "explorer"
                        })
            
            # Get rotation decisions using existing logic
            decisions_df = self.variant_module['make_decisions'](df_filtered)
            
            # Clean up temp file
            if os.path.exists(temp_csv_path):
                os.remove(temp_csv_path)
            
            # Format results for API response
            root_causes = self._format_root_causes(mismatch_evidence, qualification_issues)
            campaign_decisions = self._format_campaign_decisions(decisions_df)
            
            print("✅ Analysis complete using existing logic!")
            
            return {
                "root_causes": root_causes,
                "variants_data": {
                    "variants_count": len(all_variants),
                    "variants": all_variants  # Include full variants for CSV download
                },
                "campaign_decisions": campaign_decisions,
                "expected_impact": self._generate_expected_impact(df_filtered, mismatch_evidence, qualification_issues, decisions_df)
            }
            
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
            raise Exception(f"Analysis failed: {str(e)}")
    

    
    def _format_root_causes(self, mismatch_evidence, qualification_issues) -> List[Dict]:
        """Format existing root cause analysis for API response"""
        root_causes = []
        
        # Format Copy-Intent Mismatch from existing analysis
        if len(mismatch_evidence) > 0:
            root_causes.append({
                "name": "Copy-Intent Mismatch",
                "description": "Low QPI performance on high-impression campaigns",
                "case_count": len(mismatch_evidence),
                "evidence": mismatch_evidence[['headline', 'audience_segment', 'placement', 'impressions', 'CTR', 'QPI', 'keywords']].head(3).to_dict('records') if hasattr(mismatch_evidence, 'to_dict') else []
            })
        
        # Format Qualification Gap from existing analysis
        if len(qualification_issues) > 0:
            root_causes.append({
                "name": "Qualification Gap",
                "description": "OK CTR but poor qualified lead conversion",
                "case_count": len(qualification_issues),
                "evidence": qualification_issues[['headline', 'description', 'audience_segment', 'CTR', 'CPQL', 'qualified_rate']].head(3).to_dict('records') if hasattr(qualification_issues, 'to_dict') else [],
                "avg_qualified_rate": f"{qualification_issues['qualified_rate'].mean():.1%}" if hasattr(qualification_issues, 'qualified_rate') else "60.0%"
            })
        
        return root_causes
    
    def _format_campaign_decisions(self, decisions_df) -> Dict:
        """Format existing rotation decisions for API response"""
        try:
            decision_counts = decisions_df['decision'].value_counts()
            return {
                "pause_count": int(decision_counts.get("PAUSE", 0)),
                "keep_count": int(decision_counts.get("KEEP", 0)),
                "monitor_count": int(decision_counts.get("MONITOR", 0))
            }
        except:
            return {
                "pause_count": 0,
                "keep_count": 0,
                "monitor_count": 0
            }
    
    def _get_dynamic_fallback_description(self, top_performers, segment) -> str:
        """Get dynamic fallback description from top performing campaigns"""
        try:
            # Filter top performers by segment
            segment_performers = top_performers[top_performers['audience_segment'] == segment]
            if len(segment_performers) > 0:
                # Get most common description pattern
                most_common_desc = segment_performers['description'].iloc[0] if 'description' in segment_performers.columns else None
                if most_common_desc:
                    return most_common_desc
            
            # Fallback to generic based on segment
            if 'graduate' in segment.lower():
                return "Advance your career with professional skills development"
            elif 'professional' in segment.lower():
                return "Enhance your expertise with industry-leading training"
            else:
                return "Transform your career with comprehensive skill building"
        except:
            return "Professional development program"
    

    
    def _generate_expected_impact(self, df_filtered, mismatch_evidence, qualification_issues, decisions_df) -> Dict:
        """Generate expected impact projections based on ACTUAL analysis data"""
        try:
            # Calculate actual potential improvements from data
            current_avg_ctr = df_filtered['CTR'].mean()
            current_avg_cpql = df_filtered['CPQL'].mean()
            current_qualified_rate = df_filtered['qualified_rate'].mean()
            
            # Calculate top performer benchmarks
            top_quartile_ctr = df_filtered['CTR'].quantile(0.75)
            top_quartile_cpql = df_filtered['CPQL'].quantile(0.25)  # Lower is better for CPQL
            top_quartile_qualified_rate = df_filtered['qualified_rate'].quantile(0.75)
            
            # Calculate realistic improvement percentages
            ctr_improvement_potential = ((top_quartile_ctr - current_avg_ctr) / current_avg_ctr) * 100
            cpql_improvement_potential = ((current_avg_cpql - top_quartile_cpql) / current_avg_cpql) * 100
            qualified_rate_improvement = ((top_quartile_qualified_rate - current_qualified_rate) / current_qualified_rate) * 100
            
            # Ensure realistic bounds (cap at reasonable maximums)
            ctr_improvement = min(max(ctr_improvement_potential, 5), 40)  # 5-40% range
            cpql_reduction = min(max(cpql_improvement_potential, 5), 35)  # 5-35% range
            qualified_improvement = min(max(qualified_rate_improvement, 5), 50)  # 5-50% range
            
            # Calculate timeline based on decision urgency
            pause_count = len(decisions_df[decisions_df['decision'] == 'PAUSE']) if 'decision' in decisions_df.columns else 0
            total_campaigns = len(decisions_df)
            urgency_ratio = pause_count / total_campaigns if total_campaigns > 0 else 0
            
            # Dynamic timeline based on urgency
            if urgency_ratio > 0.4:  # High urgency - many campaigns to pause
                main_timeline = "21-30 days"
                variant_timeline = "5-7 days"
            elif urgency_ratio > 0.2:  # Medium urgency
                main_timeline = "30-45 days"
                variant_timeline = "7-14 days"
            else:  # Low urgency
                main_timeline = "45-60 days"
                variant_timeline = "14-21 days"
            
            return {
                "ctr_improvement": f"{ctr_improvement:.0f}-{ctr_improvement + 5:.0f}%",
                "cpql_reduction": f"{cpql_reduction:.0f}-{cpql_reduction + 5:.0f}%",
                "timeline": main_timeline,
                "variant_timeline": variant_timeline,
                "rotation_timeline": "Immediate" if pause_count > 0 else "7 days",
                "qualified_leads_improvement": f"{qualified_improvement:.0f}-{qualified_improvement + 10:.0f}%",
                "cac_reduction": f"{min(ctr_improvement, cpql_reduction):.0f}-{max(ctr_improvement, cpql_reduction):.0f}%",
                "confidence_level": "High" if urgency_ratio > 0.3 else "Medium",
                "data_driven": True
            }
            
        except Exception as e:
            print(f"⚠️ Failed to calculate dynamic impact, using conservative estimates: {e}")
            # Conservative fallback with data-driven flag
            return {
                "ctr_improvement": "",
                "cpql_reduction": "",
                "timeline": "",
                "variant_timeline": "",
                "rotation_timeline": "",
                "qualified_leads_improvement": "",
                "cac_reduction": "",
                "confidence_level": "",
                "data_driven": False
            }
