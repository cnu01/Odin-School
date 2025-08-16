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

class DataQuality(BaseModel):
    """Data quality report"""
    total_creators: int
    issues_found: List[str]
    quality_score: float
    fixes_applied: List[str]

class ModelInfo(BaseModel):
    """Model information"""
    model_config = {'protected_namespaces': ()}
    
    model_type: str
    accuracy_metrics: Dict[str, Any]
    features_used: int
    total_creators_analyzed: int

class Recommendations(BaseModel):
    """Strategic recommendations"""
    top_performers: List[PredictionResult]
    risk_mitigation: str

class PredictionResponse(BaseModel):
    """Complete prediction response"""
    model_config = {'protected_namespaces': ()}
    
    success: bool
    program_type: str
    results: List[PredictionResult]
    data_quality: DataQuality
    model_info: ModelInfo
    recommendations: Recommendations

# Error Models
class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    details: Optional[str] = None
