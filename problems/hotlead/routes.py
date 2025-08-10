from fastapi import APIRouter, HTTPException
from .models import LeadInput, ScoredLead
from .service import HotLeadService

router = APIRouter()

# Initialize service
hotlead_service = HotLeadService()

@router.get("/")
async def hotlead_home():
    """HotLead - Sales Lead Scoring & Prioritization"""
    return {
        "problem": "HotLead - Sales Lead Scoring & Prioritization",
        "description": "AI-driven lead scoring and prioritization system with intelligent routing",
        "status": "Active - AI Analysis Ready",
        "features": [
            "AI-powered lead scoring (0-100)",
            "Priority routing recommendations",
            "Source-based conversion analysis",
            "Real-time lead processing"
        ],
        "endpoints": {
            "/score": "POST - Score leads with AI analysis and routing"
        }
    }

@router.post("/score", response_model=ScoredLead)
async def score_lead(lead_input: LeadInput):
    """
    Score a lead using AI analysis for priority and routing
    
    Args:
        lead_input: LeadInput containing lead data (source, pageviews, device, geography, form_fields)
        
    Returns:
        ScoredLead with AI-generated score, reason, and priority routing action
    """
    try:
        # Process lead with AI analysis
        scored_lead = await hotlead_service.score_lead(lead_input)
        return scored_lead
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing lead: {str(e)}"
        )
