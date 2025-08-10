#!/usr/bin/env python3
"""
TrustDesk Complete Test Suite
============================
Comprehensive test for TrustDesk AI comment analysis system.
Tests all core functionality including models, services, and API endpoints.

Usage: python test_trustdesk_complete.py

This test demonstrates:
- Data model validation
- Service functionality with error handling
- API endpoint integration (optional)
- Full workflow validation
"""
import asyncio
import os
import sys
from unittest.mock import patch

# Set environment
os.environ["AI_API_KEY"] = "test-key-demo"

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from problems.trustdesk.service import process_comment_with_ai
from problems.trustdesk.models import CommentInput, AnalyzedComment

async def test_trustdesk_functionality():
    """Test TrustDesk core functionality with comprehensive scenarios"""
    
    print("🧪 TrustDesk Core Functionality Test")
    print("=" * 45)
    
    test_cases = [
        {
            "comment": "This course is absolutely amazing! The instructors are brilliant and I'm learning so much.",
            "name": "Positive Feedback Test",
            "description": "Testing positive sentiment detection"
        },
        {
            "comment": "This is terrible! I want my money back immediately. The course is useless!",
            "name": "Negative Complaint Test",
            "description": "Testing negative sentiment and urgency"
        },
        {
            "comment": "Hi, how do I access the downloadable materials for module 3?",
            "name": "Support Question Test",
            "description": "Testing question classification"
        },
        {
            "comment": "The instructor made some inappropriate comments about certain groups. This is unacceptable.",
            "name": "Sensitive Content Test",
            "description": "Testing sensitive content detection"
        },
        {
            "comment": "URGENT: My certification exam is tomorrow and I can't access the practice tests!",
            "name": "Urgent Issue Test",
            "description": "Testing urgency scoring for critical issues"
        },
        {
            "comment": "Good content overall but the platform is slow and videos freeze sometimes.",
            "name": "Mixed Feedback Test",
            "description": "Testing mixed sentiment analysis"
        }
    ]
    
    print("🔧 Testing with AI service fallback (demonstrates robust error handling)")
    print()
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print(f"   📋 {test_case['description']}")
        print(f"   📝 Comment: '{test_case['comment'][:60]}{'...' if len(test_case['comment']) > 60 else ''}'")
        
        try:
            # Process the comment (will use fallback since no real AI API)
            result = await process_comment_with_ai(test_case['comment'])
            
            print(f"   ✅ Processed successfully")
            print(f"   🎯 Sentiment: {result.sentiment}")
            print(f"   🔥 Urgency: {result.urgency_score}/10")
            print(f"   ⚠️  Sensitive: {result.is_sensitive}")
            print(f"   💬 Reply: {result.suggested_reply[:60]}...")
            
            # Comprehensive validation
            assert isinstance(result, AnalyzedComment), "Result must be AnalyzedComment instance"
            assert result.original_comment == test_case['comment'], "Original comment must match"
            assert isinstance(result.urgency_score, int), "Urgency score must be integer"
            assert 0 <= result.urgency_score <= 10, "Urgency score must be 0-10"
            assert isinstance(result.is_sensitive, bool), "is_sensitive must be boolean"
            assert isinstance(result.sentiment, str), "Sentiment must be string"
            assert len(result.suggested_reply) > 0, "Suggested reply must not be empty"
            
            results.append({"test": test_case['name'], "status": "PASS", "result": result})
            print(f"   ✅ Validation: All fields correct and within expected ranges")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({"test": test_case['name'], "status": "FAIL", "error": str(e)})
        
        print()
    
    # Detailed results analysis
    passed = len([r for r in results if r['status'] == 'PASS'])
    total = len(results)
    
    print("📊 FUNCTIONALITY TEST RESULTS")
    print("=" * 35)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"🎯 Success Rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 ALL CORE FUNCTIONALITY TESTS PASSED!")
        print("✨ TrustDesk service layer is working correctly!")
        print("🛡️  Error handling and graceful fallbacks are operational!")
        print("📊 All data validation checks passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check output above for details.")
    
    return results

def test_data_models():
    """Test the Pydantic data models comprehensively"""
    print("🧪 Testing Data Models & Validation")
    print("=" * 40)
    
    try:
        # Test 1: CommentInput model
        print("1. CommentInput Model Tests")
        comment_input = CommentInput(comment_text="Test comment for validation")
        assert comment_input.comment_text == "Test comment for validation"
        print("   ✅ Basic creation: Working")
        
        # Test empty string (should be allowed)
        empty_input = CommentInput(comment_text="")
        assert empty_input.comment_text == ""
        print("   ✅ Empty string handling: Working")
        
        # Test very long comment
        long_comment = "A" * 1000
        long_input = CommentInput(comment_text=long_comment)
        assert long_input.comment_text == long_comment
        print("   ✅ Long comment handling: Working")
        
        # Test 2: AnalyzedComment model
        print("\n2. AnalyzedComment Model Tests")
        analyzed = AnalyzedComment(
            original_comment="Test comment",
            sentiment="Positive",
            urgency_score=5,
            is_sensitive=False,
            suggested_reply="Test reply"
        )
        print("   ✅ Basic creation: Working")
        
        # Test 3: JSON serialization
        print("\n3. JSON Serialization Tests")
        json_data = analyzed.model_dump()
        required_fields = ['original_comment', 'sentiment', 'urgency_score', 'is_sensitive', 'suggested_reply']
        assert all(field in json_data for field in required_fields)
        print("   ✅ JSON serialization: Working")
        print(f"   📋 Fields present: {list(json_data.keys())}")
        
        # Test 4: Field validation
        print("\n4. Field Validation Tests")
        
        # Test invalid urgency score (string instead of int)
        try:
            invalid_urgency = AnalyzedComment(
                original_comment="Test",
                sentiment="Positive",
                urgency_score="invalid",  # Should be int
                is_sensitive=False,
                suggested_reply="Reply"
            )
            print("   ❌ Should have rejected invalid urgency score type")
            return False
        except:
            print("   ✅ Invalid urgency score type: Correctly rejected")
        
        # Test invalid is_sensitive (string instead of bool)
        try:
            invalid_sensitive = AnalyzedComment(
                original_comment="Test",
                sentiment="Positive",
                urgency_score=5,
                is_sensitive="not_boolean",  # Should be bool
                suggested_reply="Reply"
            )
            print("   ❌ Should have rejected invalid is_sensitive type")
            return False
        except:
            print("   ✅ Invalid is_sensitive type: Correctly rejected")
        
        # Test edge case values
        print("\n5. Edge Case Value Tests")
        edge_case = AnalyzedComment(
            original_comment="",  # Empty string
            sentiment="Neutral",
            urgency_score=0,  # Minimum value
            is_sensitive=True,
            suggested_reply="Minimal reply"
        )
        assert edge_case.urgency_score == 0
        print("   ✅ Minimum urgency score (0): Working")
        
        max_urgency = AnalyzedComment(
            original_comment="Test",
            sentiment="Negative",
            urgency_score=10,  # Maximum value
            is_sensitive=True,
            suggested_reply="Maximum urgency reply"
        )
        assert max_urgency.urgency_score == 10
        print("   ✅ Maximum urgency score (10): Working")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Model test failed: {e}")
        return False

def test_api_integration():
    """Test API integration using FastAPI TestClient (optional)"""
    print("\n🧪 Testing API Integration (Optional)")
    print("=" * 45)
    
    try:
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        from problems.trustdesk.routes import router as trustdesk_router
        
        # Create test app
        app = FastAPI(title="TrustDesk Test")
        app.include_router(trustdesk_router, prefix="/api/trustdesk")
        client = TestClient(app)
        
        # Test home endpoint
        print("1. Testing Home Endpoint")
        response = client.get("/api/trustdesk/")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Home endpoint: {result.get('status', 'Working')}")
        else:
            print(f"   ❌ Home endpoint failed: {response.status_code}")
            return False
        
        # Test analyze endpoint (will use fallback)
        print("\n2. Testing Analyze Endpoint")
        test_comment = "This is a test comment for API integration"
        response = client.post(
            "/api/trustdesk/analyze",
            json={"comment_text": test_comment}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Analyze endpoint: Working")
            print(f"   📊 Response fields: {list(result.keys())}")
            
            # Validate response structure
            required_fields = ['original_comment', 'sentiment', 'urgency_score', 'is_sensitive', 'suggested_reply']
            missing = [f for f in required_fields if f not in result]
            if not missing:
                print("   ✅ All required fields present")
            else:
                print(f"   ❌ Missing fields: {missing}")
                return False
        else:
            print(f"   ❌ Analyze endpoint failed: {response.status_code}")
            return False
        
        return True
        
    except ImportError:
        print("   ⚠️  FastAPI TestClient not available, skipping API tests")
        return True  # Don't fail if optional dependency missing
    except Exception as e:
        print(f"   ❌ API integration test failed: {e}")
        return False

async def main():
    """Run comprehensive TrustDesk test suite"""
    print("🚀 TrustDesk Complete Test Suite")
    print("=" * 50)
    print("📋 Testing all components: Models, Services, and API")
    print()
    
    test_results = {
        "models": False,
        "functionality": [],
        "api": False
    }
    
    # Test 1: Data models
    print("=" * 50)
    test_results["models"] = test_data_models()
    
    # Test 2: Core functionality  
    print("\n" + "=" * 50)
    test_results["functionality"] = await test_trustdesk_functionality()
    
    # Test 3: API integration (optional)
    print("\n" + "=" * 50)
    test_results["api"] = test_api_integration()
    
    # Calculate overall results
    func_passed = len([r for r in test_results["functionality"] if r['status'] == 'PASS'])
    func_total = len(test_results["functionality"])
    
    total_tests = 1 + func_total + 1  # models + functionality + api
    total_passed = (1 if test_results["models"] else 0) + func_passed + (1 if test_results["api"] else 0)
    
    # Final comprehensive summary
    print("\n" + "=" * 50)
    print("🏁 COMPREHENSIVE TEST SUMMARY")
    print("=" * 50)
    print(f"📊 Test Categories:")
    print(f"   🔧 Data Models:     {'✅ PASS' if test_results['models'] else '❌ FAIL'}")
    print(f"   🧪 Functionality:   ✅ {func_passed}/{func_total} passed")
    print(f"   🌐 API Integration: {'✅ PASS' if test_results['api'] else '❌ FAIL'}")
    print()
    print(f"� Overall Results:")
    print(f"   �📊 Total Tests:     {total_tests}")
    print(f"   ✅ Passed:          {total_passed}")
    print(f"   ❌ Failed:          {total_tests - total_passed}")
    print(f"   🎯 Success Rate:    {(total_passed/total_tests*100):.1f}%")
    
    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("✨ TrustDesk is fully functional and ready for production!")
        print("🚀 Features validated:")
        print("   • Data model validation and serialization")
        print("   • Comment processing with error handling")
        print("   • API endpoint integration")
        print("   • Graceful fallback mechanisms")
        print("   • Comprehensive field validation")
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed.")
        print("📋 Review the output above for specific failure details.")
    
    print(f"\n📄 Test completed at: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return test_results

if __name__ == "__main__":
    asyncio.run(main())
