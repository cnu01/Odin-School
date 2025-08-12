#!/usr/bin/env python3
"""
Test OneTruth Dashboard Endpoint
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from problems.onetruth.service import OnetruthService


async def test_dashboard():
    """Test OneTruth dashboard endpoint"""
    try:
        print("🔄 Testing OneTruth dashboard service...")
        service = OnetruthService()
        
        print("🔄 Calling get_dashboard_data...")
        result = await service.get_dashboard_data(time_range="7d", include_anomalies=True)
        
        print("✅ Dashboard data retrieved successfully!")
        print(f"📊 Data points: {result.get('data_points', 'N/A')}")
        print(f"🎯 Business health: {result.get('business_health', {}).get('overall_health_score', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Testing OneTruth Dashboard...")
    success = asyncio.run(test_dashboard())
    
    if success:
        print("🎉 OneTruth dashboard test successful!")
    else:
        print("💥 OneTruth dashboard test failed.")
        sys.exit(1)
