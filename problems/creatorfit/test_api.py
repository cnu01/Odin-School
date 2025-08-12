#!/usr/bin/env python3
"""
Simple test script for CreatorFit FastAPI endpoints
"""

import requests
import json
from pathlib import Path

# API base URL (adjust if running on different port)
BASE_URL = "http://localhost:8000/api/creatorfit"

def test_health():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_programs():
    """Test available programs endpoint"""
    print("📋 Testing available programs...")
    response = requests.get(f"{BASE_URL}/programs")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_csv_analysis():
    """Test CSV analysis endpoint"""
    print("📊 Testing CSV analysis...")
    
    # Check if sample CSV exists
    sample_csv = Path("frontend/sample_creators.csv")
    if not sample_csv.exists():
        print("❌ Sample CSV not found. Please ensure sample_creators.csv exists in frontend/ directory")
        return
    
    # Upload CSV for analysis
    with open(sample_csv, 'rb') as f:
        files = {'file': ('sample_creators.csv', f, 'text/csv')}
        data = {
            'program_type': 'data_science',
            'campaign_budget': 100000
        }
        
        response = requests.post(f"{BASE_URL}/analyze", files=files, data=data)
        
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Analysis successful!")
        print(f"Total creators analyzed: {len(result.get('results', []))}")
        print(f"Total predicted leads: {result.get('summary', {}).get('total_predicted_leads', 0)}")
        print(f"Estimated CPL: ₹{result.get('summary', {}).get('estimated_cpl', 0):,.0f}")
        print(f"Data quality score: {result.get('data_quality', {}).get('quality_score', 0):.2%}")
        
        # Show top 3 creators
        top_creators = result.get('results', [])[:3]
        print("\n🏆 Top 3 Creators:")
        for creator in top_creators:
            print(f"  {creator['rank']}. {creator['creator_id']} - {creator['predicted_qualified_leads']} leads "
                  f"(Fit: {creator['fit_score']:.3f}, Confidence: {creator['confidence_score']:.3f}) - {creator['recommendation']}")
    else:
        print(f"❌ Analysis failed: {response.text}")
    print()

def test_lead_forecast():
    """Test lead forecasting endpoint"""
    print("🔮 Testing lead forecasting...")
    
    # Sample creator data
    creator_data = {
        "creator_id": "test_creator_001",
        "topic": "Python Programming; Data Science",
        "recent_video_transcript": "Welcome to my Python tutorial. Today we'll learn about data science and machine learning with pandas and scikit-learn.",
        "posting_cadence_days": 3,
        "views_90d": 150000,
        "language": "English",
        "category_tag": "Education"
    }
    
    response = requests.post(
        f"{BASE_URL}/forecast",
        json=creator_data,
        params={"program_type": "data_science"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Forecast successful!")
        if result.get('results'):
            forecast = result['results'][0]
            print(f"Creator: {forecast['creator_id']}")
            print(f"Predicted leads: {forecast['predicted_qualified_leads']}")
            print(f"Fit score: {forecast['fit_score']:.3f}")
            print(f"Confidence: {forecast['confidence_score']:.3f}")
            print(f"Recommendation: {forecast['recommendation']}")
    else:
        print(f"❌ Forecast failed: {response.text}")
    print()



if __name__ == "__main__":
    print("🚀 CreatorFit API Test Suite")
    print("=" * 40)
    
    try:
        test_health()
        test_programs()
        test_csv_analysis()
        test_lead_forecast()
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the FastAPI server is running:")
        print("   uvicorn main:app --reload")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
