from pydantic import BaseModel
from typing import Optional, Dict, Any

class LeadInput(BaseModel):
    """Request model for a new lead to be analyzed"""
    source: str
    pageviews: int
    device: str
    geography: str
    form_fields: Dict[str, Any]

class ScoredLead(BaseModel):
    """Response model for a scored lead with AI analysis"""
    lead_input: LeadInput
    score: int
    reason: str
    priority: str
    routing_action: str
