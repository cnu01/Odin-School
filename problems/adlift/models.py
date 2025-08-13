from pydantic import BaseModel
from typing import List, Optional
import pandas as pd

class AdliftBase(BaseModel):
    """Base model for Adlift - define your models here"""
    pass

class AnalysisRequest(BaseModel):
    """Request model for CSV analysis"""
    filename: str

class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    success: bool
    message: str
    data: Optional[dict] = None

class RootCause(BaseModel):
    """Model for root cause analysis"""
    name: str
    description: str
    case_count: int
    evidence: List[dict]

class CampaignDecision(BaseModel):
    """Model for campaign decisions"""
    pause_count: int
    keep_count: int
    monitor_count: int

class ExpectedImpact(BaseModel):
    """Model for expected impact projections"""
    ctr_improvement: str
    cpql_reduction: str
    timeline: str
    qualified_leads_improvement: str
    cac_reduction: str

class AnalysisResults(BaseModel):
    """Complete analysis results"""
    performance_variance: dict
    root_causes: List[RootCause]
    campaign_decisions: CampaignDecision
    fatigue_detection: List[dict]
    expected_impact: ExpectedImpact
    variants_count: int
    decisions_count: int
