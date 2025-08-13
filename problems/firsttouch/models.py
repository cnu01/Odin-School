"""
FirstTouch models for API requests and responses
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class LeadProfile(BaseModel):
    """Lead profile for call optimization"""
    lead_id: str
    source: str
    intent_type: str
    urgency_level: str
    geography: str
    device: str
    lead_source_score: float = Field(ge=0.0, le=1.0)
    lead_intent_score: float = Field(ge=0.0, le=1.0)
    lead_urgency_score: float = Field(ge=0.0, le=1.0)
    geography_score: float = Field(ge=0.0, le=1.0)
    device_type_score: float = Field(ge=0.0, le=1.0)
    time_since_inquiry_minutes: int = Field(ge=0)
    lead_engagement_score: float = Field(ge=0.0, le=1.0)
    estimated_ltv: float = Field(ge=0)


class CallOptimizationRequest(BaseModel):
    """Request for call timing optimization"""
    lead_profile: LeadProfile
    preferred_time_windows: Optional[List[str]] = None
    agent_constraints: Optional[Dict[str, Any]] = None


class CallOptimizationResponse(BaseModel):
    """Response with optimized call timing and approach"""
    lead_id: str
    success_probability: float
    optimal_timing: Dict[str, Any]
    script_recommendations: Dict[str, Any]
    priority_score: float
    insights: Dict[str, Any]


class ScriptGenerationRequest(BaseModel):
    """Request for personalized script generation"""
    lead_profile: LeadProfile
    script_type: Optional[str] = "standardized_discovery"
    conversation_context: Optional[Dict[str, Any]] = None


class ScriptGenerationResponse(BaseModel):
    """Response with generated call script"""
    lead_id: str
    script_content: str
    key_talking_points: List[str]
    objection_handling: List[str]
    success_metrics: Dict[str, Any]


class CallOutcomeTracking(BaseModel):
    """Track call outcomes for model improvement"""
    lead_id: str
    call_timestamp: datetime
    outcome: str  # connected, qualified, booked, no_connect
    call_duration_seconds: int
    agent_id: str
    script_used: str
    notes: Optional[str] = None


class CallAnalyticsRequest(BaseModel):
    """Request for call performance analytics"""
    date_range: List[str]
    filters: Optional[Dict[str, Any]] = None
    metrics: Optional[List[str]] = None


class CallAnalyticsResponse(BaseModel):
    """Response with call performance analytics"""
    total_calls: int
    connect_rate: float
    qualification_rate: float
    booking_rate: float
    avg_time_to_contact: float
    performance_by_segment: Dict[str, Any]
    recommendations: List[str]


# Problem Analysis Models (same as other systems)
class ProblemDiagnosis(BaseModel):
    """Individual problem diagnosis with supporting data"""
    problem_id: str
    title: str
    symptom: str
    root_cause: str
    impact: str
    evidence: str
    supporting_data: Dict[str, Any]


class SegmentChallenge(BaseModel):
    """Segment-specific challenge analysis"""
    segment_type: str
    segment_name: str
    description: str
    characteristics: List[str]
    conversion_impact: str
    supporting_metrics: Dict[str, Any]


class ProblemAnalysisResponse(BaseModel):
    """Complete problem analysis for frontend display"""
    problems: List[ProblemDiagnosis]
    segment_challenges: List[SegmentChallenge]
    overall_impact: Dict[str, str]
    implementation_status: Dict[str, str]


# Training and Evaluation Models
class ModelTrainingRequest(BaseModel):
    """Request to train the FirstTouch model"""
    training_size: int = 2000
    validation_split: float = 0.2
    hyperparameters: Optional[Dict[str, Any]] = None


class ModelTrainingResponse(BaseModel):
    """Response from model training"""
    status: str
    metrics: Dict[str, Any]
    training_samples: int
    model_version: str


class ModelEvaluationResponse(BaseModel):
    """Model performance evaluation"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    feature_importance: Dict[str, float]
    test_samples: int


# Legacy compatibility
class FirsttouchBase(BaseModel):
    """Base model for Firsttouch - define your models here"""
    pass
