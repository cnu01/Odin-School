#!/usr/bin/env python3
"""
OneTruth Data Seeding Script
Seeds the database with synthetic data and trains the ML model
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from problems.onetruth.service import OnetruthService


async def seed_onetruth_data():
    """Seed OneTruth with synthetic data and train the model"""
    try:
        print("🔄 Initializing OneTruth service...")
        service = OnetruthService()
        
        print("🔄 Seeding database with synthetic analytics data...")
        result = await service.seed_data(size=2000)
        
        print("✅ OneTruth data seeding completed successfully!")
        print(f"📊 Records created: {result['records_created']}")
        print(f"🤖 Model trained: {result['message']}")
        
        # Test the model
        print("🔄 Testing anomaly detection...")
        anomalies = await service.detect_anomalies(time_range="7d")
        print(f"✅ Anomaly detection working: Found {anomalies.total_anomalies} anomalies")
        
        # Test model evaluation
        print("🔄 Testing model evaluation...")
        evaluation = await service.evaluate_model(sample_size=10)
        print(f"✅ Model evaluation working: Accuracy {evaluation.evaluation_results['accuracy']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error seeding OneTruth data: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting OneTruth data seeding...")
    success = asyncio.run(seed_onetruth_data())
    
    if success:
        print("🎉 OneTruth is now ready with trained model and data!")
    else:
        print("💥 OneTruth seeding failed. Check the errors above.")
        sys.exit(1)
