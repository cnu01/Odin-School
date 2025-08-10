#!/usr/bin/env python3
"""
HotLead Quick Test
==================
Quick validation test for HotLead lead scoring functionality.
Run this for fast verification of core features.

Usage: python test_hotlead_quick.py
"""
import asyncio
import os
import sys

# Set environment
os.environ["TESTING"] = "1"

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from problems.hotlead.models import LeadInput, ScoredLead
from problems.hotlead.service import HotLeadService

async def quick_test():
    """Quick test of HotLead functionality"""
    print("🔥 HotLead Quick Test")
    print("=" * 30)
    
    try:
        # Initialize service
        service = HotLeadService()
        
        # Create test lead
        test_lead = LeadInput(
            source="google-ads",
            pageviews=5,
            device="desktop", 
            geography="US-CA-San Francisco",
            form_fields={
                "name": "Test User",
                "email": "test@example.com",
                "company": "Test Corp",
                "title": "CTO",
                "interest": "Enterprise solution"
            }
        )
        
        print("📝 Test Lead Created:")
        print(f"   Source: {test_lead.source}")
        print(f"   Pageviews: {test_lead.pageviews}")
        print(f"   Device: {test_lead.device}")
        print(f"   Geography: {test_lead.geography}")
        print(f"   Contact: {test_lead.form_fields['email']}")
        
        # Score the lead
        print("\n🧠 Scoring lead with AI...")
        scored_lead = await service.score_lead(test_lead)
        
        print("✅ Lead Scored Successfully!")
        print(f"   Score: {scored_lead.score}/100")
        print(f"   Priority: {scored_lead.priority}")
        print(f"   Action: {scored_lead.routing_action}")
        print(f"   Reason: {scored_lead.reason[:100]}...")
        
        print(f"\n🎯 HotLead Status: {'✅ WORKING' if scored_lead.score > 0 else '❌ ISSUE'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test Failed: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(quick_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
        sys.exit(1)
