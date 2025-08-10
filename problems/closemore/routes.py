from fastapi import APIRouter, HTTPException
from typing import List
from .models import ConversationInput, ConversationAnalysis, NextBestAction, DailyActionsRequest
from .service import ClosemoreService

router = APIRouter()

# Initialize service
closemore_service = ClosemoreService()

@router.get("/")
async def closemore_home():
    """CloseMore - Sales Conversation Analysis & Daily Action Planning"""
    return {
        "problem": "CloseMore - Sales Conversation Analysis & Daily Action Planning",
        "description": "AI-powered two-part sales system for conversation analysis and action prioritization",
        "status": "Active - AI Analysis Ready",
        "features": [
            "Sales conversation analysis with AI insights",
            "Objection detection and intent classification", 
            "Daily action planning for sales reps",
            "Prioritized next-best-action recommendations"
        ],
        "endpoints": {
            "/analyze": "POST - Analyze sales conversations for insights and next steps",
            "/daily-actions": "POST - Generate prioritized daily action list for sales reps"
        }
    }

@router.post("/analyze", response_model=ConversationAnalysis)
async def analyze_conversation(conversation_input: ConversationInput):
    """
    Analyze a sales conversation to extract insights and next steps
    
    Args:
        conversation_input: ConversationInput containing lead_id, channel, and conversation text
        
    Returns:
        ConversationAnalysis with AI-generated summary, intent, objections, and next steps
    """
    try:
        # Analyze conversation with AI
        analysis = await closemore_service.analyze_conversation(conversation_input)
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing conversation: {str(e)}"
        )

@router.post("/daily-actions", response_model=List[NextBestAction])
async def get_daily_actions(request: DailyActionsRequest):
    """
    Generate a prioritized daily action list for a sales rep
    
    Args:
        request: DailyActionsRequest containing rep_id
        
    Returns:
        List of NextBestAction objects with prioritized tasks and recommendations
    """
    try:
        # Get daily actions with AI prioritization
        actions = await closemore_service.get_daily_actions(request.rep_id)
        return actions
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating daily actions: {str(e)}"
        )
