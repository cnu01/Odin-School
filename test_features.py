#!/usr/bin/env python3
"""
Test Step 2: Feature Engineering with Industry Standard
"""
import sys
sys.path.append('.')

from data_preprocessing import load_and_clean_data
from features import build_features

def test_feature_engineering():
    print("🔧 STEP 2: TESTING FEATURE ENGINEERING")
    print("=" * 50)
    
    # Step 1: Load preprocessed data (already done)
    print("📊 Loading preprocessed data...")
    df_clean, fix_report, cleaned_path = load_and_clean_data(
        raw_filename="creator_campaign_audience.csv",
        cleaned_filename="creator_campaign_audience.cleaned.csv",
    )
    print(f"✅ Preprocessed data loaded: {df_clean.shape}")
    
    # Step 2: Build features
    print("\n🏗️ Building features...")
    X, y, meta = build_features(
        df_clean=df_clean,
        program_type="data_science",
    )
    
    print(f"✅ Features built successfully!")
    print(f"📊 X (features) shape: {X.shape}")
    print(f"🎯 y (target) shape: {y.shape}")
    print(f"📋 Feature columns: {list(X.columns)}")
    print(f"🎯 Target column: {meta['target']}")
    
    # Check target values (should be unscaled now!)
    print(f"\n📊 TARGET ANALYSIS (qualified_leads):")
    print(f"   Range: {y.min():.1f} to {y.max():.1f}")
    print(f"   Mean: {y.mean():.1f}")
    print(f"   Sample values: {y.head(10).tolist()}")
    
    # Check if features are scaled
    print(f"\n📊 FEATURE ANALYSIS:")
    for col in ['posting_cadence_days', 'views_90d', 'fit_score']:
        if col in X.columns:
            print(f"   {col}: {X[col].min():.3f} to {X[col].max():.3f}")
    
    if y.min() >= 1 and y.max() > 100:
        print("\n✅ SUCCESS: Target values are in ORIGINAL SCALE (industry standard)!")
        print("   Values like 7, 778, 216, etc. - NOT 0.001, 0.5, etc.")
    else:
        print("\n❌ ISSUE: Target values still seem scaled!")
        
    return X, y, meta

if __name__ == "__main__":
    X, y, meta = test_feature_engineering()
