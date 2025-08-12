from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Simple Enums for our core functionality
class ProgramType(str, Enum):
    DATA_SCIENCE = "data_science"
    WEB_DEVELOPMENT = "web_development"
    DIGITAL_MARKETING = "digital_marketing"
    AI_ML = "ai_ml"

class Recommendation(str, Enum):
    BOOK = "BOOK"
    REVIEW = "REVIEW"
    SKIP = "SKIP"

# Core Models for Analysis
class AnalysisRequest(BaseModel):
    """Request model for CSV analysis"""
    program_type: ProgramType = Field(default=ProgramType.DATA_SCIENCE, description="Program type for analysis")
    campaign_budget: float = Field(default=100000, ge=0, description="Campaign budget for CPL calculation")

class PredictionResult(BaseModel):
    """Individual creator prediction result"""
    rank: int
    creator_id: str
    predicted_qualified_leads: int
    fit_score: float = Field(..., ge=0, le=1)
    confidence_score: float = Field(..., ge=0, le=1)
    topic: str
    language: str
    views_90d: int
    creator_tier: str
    posting_cadence_days: int
    recommendation: Recommendation

class BusinessMetrics(BaseModel):
    """Business intelligence metrics"""
    total_predicted_leads: int
    estimated_cpl: float
    estimated_enrollments: int
    estimated_revenue: int
    estimated_roi_percent: float
    creator_distribution: Dict[str, int]
    avg_confidence: float
    campaign_budget: float

class DataQuality(BaseModel):
    """Data quality report"""
    total_creators: int
    issues_found: List[str]
    quality_score: float
    fixes_applied: List[str]

class ModelInfo(BaseModel):
    """Model information"""
    model_type: str
    accuracy_metrics: Dict[str, Any]
    features_used: int
    total_creators_analyzed: int

class Recommendations(BaseModel):
    """Strategic recommendations"""
    top_performers: List[PredictionResult]
    budget_allocation: str
    risk_mitigation: str

class PredictionResponse(BaseModel):
    """Complete prediction response"""
    success: bool
    program_type: str
    results: List[PredictionResult]
    summary: BusinessMetrics
    data_quality: DataQuality
    model_info: ModelInfo
    recommendations: Recommendations

# Error Models
class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    details: Optional[str] = None
