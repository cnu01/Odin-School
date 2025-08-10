import httpx
import os
import json
from dotenv import load_dotenv
from typing import List
from .models import ConversationInput, ConversationAnalysis, NextBestAction

# Load environment variables
load_dotenv()

async def analyze_conversation_with_ai(conversation_input: ConversationInput) -> ConversationAnalysis:
    """
    Analyze a sales conversation using AI to extract insights and next steps
    
    Args:
        conversation_input: ConversationInput containing lead_id, channel, and conversation text
        
    Returns:
        ConversationAnalysis with summary, intent, objections, and next steps
    """
    api_key = os.getenv("AI_API_KEY")
    
    if not api_key:
        raise ValueError("AI_API_KEY not found in environment variables")
    
    # Construct detailed prompt for sales conversation analysis
    prompt = f"""
You are an expert sales coach analyzing a conversation from Odin School, an EdTech company.

**Context from Playbooks:**
- Common objections include: price, course timing, job support uncertainty, and content quality.
- The goal is to book a meeting, get a clear commitment, or advance the lead through the funnel.
- Odin School offers professional courses for career advancement in tech.

**Conversation to Analyze:**
- Channel: {conversation_input.channel}
- Lead ID: {conversation_input.lead_id}
- Transcript: "{conversation_input.conversation_text}"

**Your Task:**
Based on the conversation, return ONLY a valid JSON object with four keys:
1. "summary": A very short, one-sentence summary of the conversation.
2. "detected_intent": The lead's primary intent (e.g., "Ready to book", "Price sensitive", "Needs more info", "Comparing options", "Not interested").
3. "objections": A list of strings of any objections raised by the lead.
4. "suggested_next_steps": A list of strings for the sales rep's next immediate actions.

Example format:
{{
  "summary": "Lead is interested but concerned about course price and time commitment",
  "detected_intent": "Price sensitive",
  "objections": ["Too expensive", "Not enough time"],
  "suggested_next_steps": ["Send pricing breakdown", "Offer flexible payment plan", "Schedule follow-up call"]
}}
"""
    
    # API request payload for OpenAI
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.1
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30.0
        )
        
        if response.status_code != 200:
            raise Exception(f"AI API error: {response.status_code} - {response.text}")
        
        result = response.json()
        ai_response = result["choices"][0]["message"]["content"].strip()
        
        # Parse JSON response
        try:
            analysis_data = json.loads(ai_response)
            return ConversationAnalysis(**analysis_data)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            raise Exception(f"Invalid JSON response from AI: {ai_response}")

async def get_daily_actions_for_rep(rep_id: str) -> List[NextBestAction]:
    """
    Generate a prioritized daily action list for a sales rep based on recent conversations
    
    Args:
        rep_id: Sales representative ID
        
    Returns:
        List of NextBestAction objects with prioritized tasks
    """
    api_key = os.getenv("AI_API_KEY")
    
    if not api_key:
        raise ValueError("AI_API_KEY not found in environment variables")
    
    # Mock recent conversation analyses for the rep (in real app, this would come from database)
    mock_conversations = [
        {
            "lead_id": f"lead_{rep_id}_001",
            "summary": "Lead expressed strong interest but wants to compare with competitors",
            "detected_intent": "Comparing options",
            "objections": ["Wants to see competitor comparison"],
            "channel": "call_transcript"
        },
        {
            "lead_id": f"lead_{rep_id}_002", 
            "summary": "Lead is price-sensitive but very interested in the course content",
            "detected_intent": "Price sensitive",
            "objections": ["Course is expensive", "Needs payment plan"],
            "channel": "whatsapp"
        },
        {
            "lead_id": f"lead_{rep_id}_003",
            "summary": "Lead ready to enroll but has questions about job support",
            "detected_intent": "Ready to book",
            "objections": ["Uncertain about job placement support"],
            "channel": "email"
        },
        {
            "lead_id": f"lead_{rep_id}_004",
            "summary": "Lead missed scheduled demo call, sent apology message",
            "detected_intent": "Needs more info",
            "objections": ["Scheduling conflicts"],
            "channel": "email"
        }
    ]
    
    # Convert mock data to string for prompt
    conversations_str = json.dumps(mock_conversations, indent=2)
    
    # Construct prompt for daily action planning
    prompt = f"""
You are a sales manager creating a prioritized to-do list for sales rep ID: {rep_id}. 
Here are the summaries of their recent conversations. Your goal is to increase win rates and reduce no-shows.

**Conversation Summaries:**
{conversations_str}

**Your Task:**
Based on the summaries, provide a JSON list of next-best-action objects for the rep. Each object should have:
- "lead_id": The lead identifier
- "action_type": One of ["SEND_FOLLOW_UP", "SCHEDULE_NUDGE", "UPDATE_CRM", "SEND_DEMO", "PRICE_DISCUSSION", "COMPETITOR_COMPARISON"]
- "suggested_message": Specific message or action to take
- "reason": Brief explanation why this action is recommended

Prioritize leads that are closest to conversion. Include 'SCHEDULE_NUDGE' actions for leads who missed meetings.

Example format:
[
  {{
    "lead_id": "lead_001",
    "action_type": "SEND_FOLLOW_UP",
    "suggested_message": "Hi [Name], I wanted to follow up on our conversation about the pricing options...",
    "reason": "Lead showed high interest but had price concerns"
  }}
]
"""
    
    # API request payload
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 800,
        "temperature": 0.2
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30.0
        )
        
        if response.status_code != 200:
            raise Exception(f"AI API error: {response.status_code} - {response.text}")
        
        result = response.json()
        ai_response = result["choices"][0]["message"]["content"].strip()
        
        # Parse JSON response
        try:
            actions_data = json.loads(ai_response)
            return [NextBestAction(**action) for action in actions_data]
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            raise Exception(f"Invalid JSON response from AI: {ai_response}")

class ClosemoreService:
    """Service class for Closemore operations"""
    
    def __init__(self):
        # Initialize any database connections, etc.
        pass
    
    async def analyze_conversation(self, conversation_input: ConversationInput) -> ConversationAnalysis:
        """
        Analyze a sales conversation and return structured insights
        
        Args:
            conversation_input: The conversation data to analyze
            
        Returns:
            ConversationAnalysis with AI-generated insights
        """
        try:
            return await analyze_conversation_with_ai(conversation_input)
        except Exception as e:
            # Fallback response if AI service fails
            return ConversationAnalysis(
                summary="Conversation analysis unavailable due to service issue",
                detected_intent="Needs manual review",
                objections=["Service unavailable"],
                suggested_next_steps=[f"Manual review required: {str(e)}"]
            )
    
    async def get_daily_actions(self, rep_id: str) -> List[NextBestAction]:
        """
        Get prioritized daily actions for a sales rep
        
        Args:
            rep_id: Sales representative ID
            
        Returns:
            List of NextBestAction objects
        """
        try:
            return await get_daily_actions_for_rep(rep_id)
        except Exception as e:
            # Fallback response if AI service fails
            return [
                NextBestAction(
                    lead_id="fallback_001",
                    action_type="UPDATE_CRM",
                    suggested_message="Review and update lead statuses manually",
                    reason=f"AI service unavailable: {str(e)}"
                )
            ]
