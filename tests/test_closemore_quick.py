#!/usr/bin/env python3
"""
CloseMore Quick Test
====================
Quick validation test for CloseMore sales conversation analysis functionality.
Run this for fast verification of core features.

Usage: python tests/test_closemore_quick.py
"""
import asyncio
import os
import sys

# Set environment
os.environ["TESTING"] = "1"

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from problems.closemore.models import ConversationInput, DailyActionsRequest
from problems.closemore.service import ClosemoreService

async def quick_test():
    """Quick test of CloseMore functionality"""
    print("💼 CloseMore Quick Test")
    print("=" * 30)
    
    try:
        # Initialize service
        service = ClosemoreService()
        
        # Test 1: Conversation Analysis
        print("📞 Testing Conversation Analysis...")
        test_conversation = ConversationInput(
            lead_id="test_lead_001",
            channel="call_transcript",
            conversation_text="Hi, I'm interested in your Python course but I'm worried about the price. It's quite expensive for me. Do you offer payment plans?"
        )
        
        print("📝 Test Conversation:")
        print(f"   Lead ID: {test_conversation.lead_id}")
        print(f"   Channel: {test_conversation.channel}")
        print(f"   Text: {test_conversation.conversation_text[:80]}...")
        
        # Analyze the conversation
        print("\n🧠 Analyzing conversation with AI...")
        analysis = await service.analyze_conversation(test_conversation)
        
        print("✅ Conversation Analyzed Successfully!")
        print(f"   Summary: {analysis.summary}")
        print(f"   Intent: {analysis.detected_intent}")
        print(f"   Objections: {len(analysis.objections)} found")
        print(f"   Next Steps: {len(analysis.suggested_next_steps)} suggested")
        
        # Test 2: Daily Actions
        print("\n📋 Testing Daily Actions Generation...")
        test_rep = DailyActionsRequest(rep_id="rep_test_123")
        
        print(f"📝 Getting daily actions for rep: {test_rep.rep_id}")
        
        # Get daily actions
        print("\n🎯 Generating daily action plan...")
        actions = await service.get_daily_actions(test_rep.rep_id)
        
        print("✅ Daily Actions Generated Successfully!")
        print(f"   Total Actions: {len(actions)}")
        
        if actions:
            print("   Sample Actions:")
            for i, action in enumerate(actions[:3]):  # Show first 3 actions
                print(f"   {i+1}. Lead {action.lead_id}: {action.action_type}")
                print(f"      Message: {action.suggested_message[:60]}...")
                print(f"      Reason: {action.reason}")
        
        # Success summary
        conversation_success = analysis and len(analysis.summary) > 0
        actions_success = actions and len(actions) > 0
        
        overall_success = conversation_success and actions_success
        
        print(f"\n🎯 CloseMore Status: {'✅ WORKING' if overall_success else '❌ ISSUE'}")
        print(f"   Conversation Analysis: {'✅' if conversation_success else '❌'}")
        print(f"   Daily Actions: {'✅' if actions_success else '❌'}")
        
        return overall_success
        
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
