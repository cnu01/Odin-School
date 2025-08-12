#!/usr/bin/env python3
"""
OneTruth Training Script
Trains the OneTruth model without requiring database connection
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ml.onetruth_model import onetruth_model, generate_synthetic_analytics_data


async def train_onetruth_model():
    """Train OneTruth model with synthetic data"""
    try:
        print("🔄 Generating synthetic training data...")
        data = generate_synthetic_analytics_data(num_samples=2000)
        
        print("🔄 Training OneTruth ML model...")
        metrics = await onetruth_model.train(data, target_column="business_health_anomaly")
        
        print("✅ OneTruth model training completed successfully!")
        print(f"📊 Training metrics: {metrics}")
        print(f"🔧 Feature count: {len(onetruth_model.feature_names)}")
        
        # Test the model
        print("🔄 Testing model predictions...")
        test_data = generate_synthetic_analytics_data(num_samples=10)
        anomalies = onetruth_model.detect_anomalies(test_data)
        print(f"✅ Model test successful: Found {anomalies['total_anomalies']} anomalies in test data")
        
        return True
        
    except Exception as e:
        print(f"❌ Error training OneTruth model: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting OneTruth model training...")
    success = asyncio.run(train_onetruth_model())
    
    if success:
        print("🎉 OneTruth model is now trained and ready!")
    else:
        print("💥 OneTruth model training failed. Check the errors above.")
        sys.exit(1)
