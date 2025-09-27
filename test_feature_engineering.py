#!/usr/bin/env python3
"""
Test Step 2: Feature Engineering with industry standard approach
"""
import sys
import os
sys.path.append('.')

from data_preprocessing import load_and_clean_data
from features import build_features

print("🔧 STEP 2: TESTING FEATURE ENGINEERING")
print("=" * 50)

# Step 1: Load preprocessed data (already done)
print("📁 Loading cleaned data from Step 1...")
df_clean, fix_report, cleaned_path = load_and_clean_data(
    raw_filename="creator_campaign_audience.csv",
    cleaned_filename="creator_campaign_audience.cleaned.csv"
)

print(f"📊 Cleaned data shape: {df_clean.shape}")
print(f"📋 Columns: {list(df_clean.columns)}")

# Step 2: Build features 
print("\n🏗️ Building features...")
X, y, meta = build_features(
    df_clean=df_clean,
    program_type="data_science",
)

print(f"\n✅ FEATURE ENGINEERING RESULTS:")
print(f"📊 Features (X) shape: {X.shape}")
print(f"📊 Target (y) shape: {y.shape}")
print(f"📋 Feature columns: {list(X.columns)}")
print(f"🎯 Target column: {meta['target']}")

# 🎯 CRITICAL: Check if target is scaled or not
print(f"\n🔍 TARGET ANALYSIS:")
print(f"Target min: {y.min():.3f}")
print(f"Target max: {y.max():.3f}")
print(f"Target mean: {y.mean():.3f}")
print(f"Target sample values: {y.head(10).tolist()}")

if y.max() > 10:
    print("✅ SUCCESS: Target values are in ORIGINAL scale (not 0-1)!")
    print("✅ Industry standard approach working!")
else:
    print("❌ ISSUE: Target values still seem scaled!")

print(f"\n📋 FEATURE ANALYSIS:")
print(f"Feature ranges:")
for col in X.columns[:5]:  # Show first 5 features
    print(f"  {col}: {X[col].min():.3f} to {X[col].max():.3f}")
