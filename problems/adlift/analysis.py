"""
AdLift Marketing Optimization - 2-Hour Practical MVP
Phase 1: Problem Diagnosis

Analyzes ad performance data to identify root causes for weak creatives/keywords
Computes business-native KPIs: QPI and CPQL
"""

import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configuration
MIN_IMPRESSIONS = 500
FATIGUE_THRESHOLD = 0.80  # 80% of initial performance

def load_and_prepare_data(file_path):
    """Load CSV and compute business-native metrics"""
    print("📊 Loading and preparing data...")
    
    try:
        # Load data with robust CSV parsing
        df = pd.read_csv(
            file_path,
            encoding='utf-8',
            skipinitialspace=True,
            on_bad_lines='skip',  # Skip malformed lines
            engine='python'  # More flexible parser
        )
        print(f"Loaded {len(df)} rows of ad data")
        
        # Validate required columns
        required_columns = [
            'date', 'campaign', 'ad_group', 'headline', 'description', 
            'keywords', 'audience_segment', 'placement', 'impressions', 
            'clicks', 'spend', 'leads', 'qualified_leads', 'CTR', 'CPC', 
            'CVR', 'qualified_rate'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
            
        print(f"✅ All required columns present: {len(required_columns)} columns")
        
    except pd.errors.ParserError as e:
        print(f"❌ CSV parsing error: {e}")
        raise ValueError(f"CSV format error: {str(e)}. Please ensure proper CSV formatting with quoted fields containing commas.")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        raise ValueError(f"Failed to load CSV file: {str(e)}")
    
    # Validate and clean numeric columns
    numeric_columns = ['impressions', 'clicks', 'spend', 'leads', 'qualified_leads', 'CTR', 'CPC', 'CVR', 'qualified_rate']
    
    for col in numeric_columns:
        if col in df.columns:
            # Convert to numeric, coerce errors to NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Fill NaN with 0 for safety
            df[col] = df[col].fillna(0)
    
    print(f"✅ Numeric columns validated and cleaned")
    
    # Compute business-native KPIs with error handling
    try:
        df['QPI'] = df['CTR'] * df['CVR'] * df['qualified_rate']  # Quality per impression
        df['CPQL_computed'] = df['CPC'] / (df['CVR'] * df['qualified_rate'].clip(lower=0.001))  # Avoid div/0
        
        # Alternative CPQL calculation for validation
        df['CPQL_direct'] = df['spend'] / df['qualified_leads'].clip(lower=1)
        
        # Use direct calculation as primary (more reliable)
        df['CPQL'] = df['CPQL_direct']
        
        print(f"✅ Business metrics computed: QPI, CPQL")
        
    except Exception as e:
        print(f"⚠️ Warning: Error computing metrics: {e}")
        # Add default values if computation fails
        df['QPI'] = 0.001
        df['CPQL'] = 100
    
    # Convert date to datetime with error handling
    try:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])  # Remove rows with invalid dates
        print(f"✅ Date column converted to datetime")
    except Exception as e:
        print(f"⚠️ Warning: Date conversion error: {e}")
    
    # Filter stable samples
    df_filtered = df[df['impressions'] >= MIN_IMPRESSIONS].copy()
    print(f"After filtering (≥{MIN_IMPRESSIONS} impressions): {len(df_filtered)} rows")
    
    if len(df_filtered) == 0:
        print("⚠️ Warning: No data meets minimum impression threshold. Using all data.")
        df_filtered = df.copy()
    
    return df, df_filtered

def analyze_performance_variance(df):
    """Analyze CTR and CPQL variance patterns"""
    print("\n🔍 Analyzing Performance Variance...")
    
    # Overall statistics
    ctr_stats = df['CTR'].describe()
    cpql_stats = df['CPQL'].describe()
    qpi_stats = df['QPI'].describe()
    
    print(f"CTR Range: {ctr_stats['min']:.1%} to {ctr_stats['max']:.1%} (variance: {ctr_stats['max']/ctr_stats['min']:.1f}x)")
    print(f"CPQL Range: ₹{cpql_stats['min']:.0f} to ₹{cpql_stats['max']:.0f} (variance: {cpql_stats['max']/cpql_stats['min']:.1f}x)")
    print(f"QPI Range: {qpi_stats['min']:.4f} to {qpi_stats['max']:.4f}")
    
    # Segment-wise analysis
    print("\n📈 Segment-wise Performance:")
    segment_analysis = df.groupby(['audience_segment', 'placement']).agg({
        'CTR': ['mean', 'std', 'min', 'max'],
        'CPQL': ['mean', 'std', 'min', 'max'], 
        'QPI': ['mean', 'std', 'min', 'max'],
        'impressions': 'sum'
    }).round(4)
    
    print(segment_analysis)
    
    return segment_analysis

def identify_root_causes(df):
    """Identify 1-2 root causes with concrete evidence"""
    print("\n🎯 Root Cause Analysis...")
    
    # Root Cause 1: Copy-Intent Mismatch (Low QPI with High Impressions)
    print("\n1️⃣ COPY-INTENT MISMATCH ANALYSIS:")
    
    # Calculate segment-wise quartiles for QPI
    df['QPI_Q25'] = df.groupby(['audience_segment', 'placement'])['QPI'].transform('quantile', 0.25)
    
    # Find high-impression, low-QPI cases
    mismatch_evidence = df[
        (df['QPI'] < df['QPI_Q25']) & 
        (df['impressions'] >= 1000)
    ].sort_values('impressions', ascending=False)
    
    if len(mismatch_evidence) > 0:
        print(f"Found {len(mismatch_evidence)} high-impression, low-QPI cases:")
        evidence_cols = ['headline', 'audience_segment', 'placement', 'impressions', 'CTR', 'QPI', 'keywords']
        print(mismatch_evidence[evidence_cols].head(3).to_string(index=False))
        
        # Pattern analysis
        low_qpi_keywords = mismatch_evidence['keywords'].str.split(', ').explode().value_counts().head(5)
        print(f"\nMost common keywords in low-QPI ads: {low_qpi_keywords.to_dict()}")
    
    # Root Cause 2: Qualification Gap (OK CTR but High CPQL)
    print("\n2️⃣ QUALIFICATION GAP ANALYSIS:")
    
    # Calculate segment-wise medians
    df['CTR_median'] = df.groupby(['audience_segment', 'placement'])['CTR'].transform('median')
    df['CPQL_Q75'] = df.groupby(['audience_segment', 'placement'])['CPQL'].transform('quantile', 0.75)
    
    # Find OK CTR but high CPQL cases
    qualification_issues = df[
        (df['CTR'] >= df['CTR_median']) & 
        (df['CPQL'] >= df['CPQL_Q75'])
    ].sort_values('CPQL', ascending=False)
    
    if len(qualification_issues) > 0:
        print(f"Found {len(qualification_issues)} OK-CTR, high-CPQL cases:")
        evidence_cols = ['headline', 'description', 'audience_segment', 'CTR', 'CPQL', 'qualified_rate']
        print(qualification_issues[evidence_cols].head(3).to_string(index=False))
        
        # Qualification rate analysis
        avg_qual_rate = qualification_issues['qualified_rate'].mean()
        print(f"\nAverage qualification rate in these cases: {avg_qual_rate:.1%}")
    
    return mismatch_evidence, qualification_issues

def detect_fatigue_patterns(df):
    """Optional: Detect creative fatigue patterns"""
    print("\n⏰ Fatigue Detection Analysis...")
    
    # Group by creative combination and analyze time patterns
    creative_groups = df.groupby(['headline', 'keywords', 'audience_segment', 'placement'])
    
    fatigue_cases = []
    
    for name, group in creative_groups:
        if len(group) >= 7:  # At least 7 days of data
            group_sorted = group.sort_values('date')
            
            # First 3 days average CTR
            first_3_ctr = group_sorted.head(3)['CTR'].mean()
            
            # Last 3 days average CTR  
            last_3_ctr = group_sorted.tail(3)['CTR'].mean()
            
            # Calculate fatigue ratio
            fatigue_ratio = last_3_ctr / first_3_ctr if first_3_ctr > 0 else 1
            
            if fatigue_ratio < FATIGUE_THRESHOLD:
                fatigue_cases.append({
                    'headline': name[0],
                    'keywords': name[1],
                    'segment': name[2],
                    'placement': name[3],
                    'first_3_ctr': first_3_ctr,
                    'last_3_ctr': last_3_ctr,
                    'fatigue_ratio': fatigue_ratio,
                    'days_live': len(group)
                })
    
    if fatigue_cases:
        fatigue_df = pd.DataFrame(fatigue_cases)
        print(f"Found {len(fatigue_cases)} fatigued creatives:")
        print(fatigue_df[['headline', 'segment', 'fatigue_ratio', 'days_live']].head(3).to_string(index=False))
        return fatigue_df
    else:
        print("No significant fatigue patterns detected in current timeframe")
        return pd.DataFrame()

def main():
    """Main analysis pipeline"""
    print("🚀 AdLift Marketing Optimization - Phase 1: Problem Diagnosis")
    print("=" * 60)
    
    # Load and prepare data
    df_raw, df_filtered = load_and_prepare_data('dataset/adlift_ads.csv')
    
    # Analyze performance variance
    segment_stats = analyze_performance_variance(df_filtered)
    
    # Identify root causes
    mismatch_evidence, qualification_issues = identify_root_causes(df_filtered)
    
    # Detect fatigue patterns
    fatigue_df = detect_fatigue_patterns(df_filtered)
    
    print("\n✅ Phase 1 Complete - Problem Diagnosis")
    print("Next: Generate diagnosis.md report")
    
    return df_filtered, mismatch_evidence, qualification_issues, fatigue_df

if __name__ == "__main__":
    main()
