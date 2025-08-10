from pydantic import BaseModel
from typing import List

class ConversationInput(BaseModel):
    """Request model for a new conversation to be analyzed"""
    lead_id: str
    channel: str  # e.g., "call_transcript", "whatsapp", "email"
    conversation_text: str

class ConversationAnalysis(BaseModel):
    """Response model for analyzed conversation with AI insights"""
    summary: str
    detected_intent: str  # e.g., "Ready to book", "Needs more info", "Price objection"
    objections: List[str]
    suggested_next_steps: List[str]

class NextBestAction(BaseModel):
    """Model for a single item in the daily action list for sales reps"""
    lead_id: str
    action_type: str  # e.g., "SEND_FOLLOW_UP", "SCHEDULE_NUDGE", "UPDATE_CRM"
    suggested_message: str
    reason: str

class DailyActionsRequest(BaseModel):
    """Request model for getting daily actions for a sales rep"""
    rep_id: str
