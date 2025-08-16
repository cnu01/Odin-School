from __future__ import annotations

from typing import List, Literal, Optional, Union, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# Problem diagnosis models for frontend display
class ProblemDiagnosis(BaseModel):
    """Model for displaying diagnosed problems to frontend"""
    problem_id: str
    title: str
    symptom: str
    root_cause: str
    impact: str
    evidence: str
    supporting_data: Dict[str, Any]


class SegmentChallenge(BaseModel):
    """Model for segment-specific challenges"""
    segment_type: str  # "geographic", "traffic_source", "device"
    segment_name: str
    description: str
    characteristics: List[str]
    conversion_impact: str
    supporting_metrics: Dict[str, float]


class ProblemAnalysisResponse(BaseModel):
    """Complete problem analysis for frontend display"""
    diagnosed_problems: List[ProblemDiagnosis]
    segment_challenges: List[SegmentChallenge]
    overall_impact: Dict[str, str]
    implementation_status: Dict[str, str]


# Original models (keeping for backward compatibility)
class Plan(BaseModel):
    id: str
    name: Literal["FULL", "3M", "6M", "12M"]
    price_total: int = Field(ge=0, description="Total price in INR")
    installment_count: int = Field(ge=1)
    installment_amount: int = Field(ge=0)
    scholarship_pct: Optional[int] = Field(default=None, ge=0, le=100)
    fees: Optional[int] = Field(default=0, ge=0)


class Segment(BaseModel):
    source: str  # paid_search|organic|referral|social|...
    geography: str = "IN"
    device: Literal["mobile", "desktop"]
    prior_engagement: Literal["low", "med", "high"]


class UserProfile(BaseModel):
    id: str
    segment: Segment


class RecommendationResult(BaseModel):
    plan_id: str
    reasons: List[str]
    risk: dict
    alternatives: Optional[List[dict]] = None


class RecommendRequest(BaseModel):
    user: Optional[UserProfile] = None
    plans: Optional[List[Plan]] = None
    context: Optional[Segment] = None


class RecommendResponse(BaseModel):
    plan_id: str
    reasons: List[str]
    risk: dict
    alternatives: Optional[List[dict]] = None


class MessageRequest(BaseModel):
    user_or_segment: Union[UserProfile, Segment]
    plan_id: str
    tone: str = "professional"
    variants: int = Field(default=3, ge=1, le=5)


class MessageResponse(BaseModel):
    messages: List[str]
    insights: Dict[str, Any] = {}
    confidence: float = 0.8


# ---- Outcomes ingestion and diagnostics ----
class OutcomeEvent(BaseModel):
    plan_id: str
    segment: Segment
    converted: bool = False
    refunded: bool = False
    defaulted: bool = False
    ts: Optional[str] = None  # ISO timestamp (optional)


class DiagnosticsResponse(BaseModel):
    total_events: int
    by_plan: dict
    by_segment_key: dict
    # Optional baseline and deltas for comparisons
    baseline_by_plan: Optional[dict] = None
    baseline_by_segment_key: Optional[dict] = None
    deltas: Optional[dict] = None  # arbitrary shape describing changes
    ai_summary: Optional[str] = None


# New ML-based models
class UserSegment(BaseModel):
    # Match ml.pricesense_model.FEATURES
    source_score: float = 0.7
    geography_score: float = 0.7
    device_score: float = 0.8
    prior_engagement_score: float = 0.5
    plan_upfront_amount: float = 5000.0
    plan_total_amount: float = 25000.0
    plan_duration_months: int = 6
    plan_monthly_payment: float = 4000.0
    plan_interest_rate: float = 5.0
    scholarship_eligible: int = 0
    scholarship_discount_pct: float = 0.0
    competitor_price_ratio: float = 1.0
    seasonality_factor: float = 1.0
    demand_pressure: float = 1.0
    price_sensitivity_score: float = 0.5
    urgency_score: float = 0.5
    income_tier_score: float = 0.5
    similar_segment_success: float = 0.6
    churn_risk_score: float = 0.3
    
    # Optional context fields
    user_id: Optional[str] = None
    source: Optional[str] = None
    geography: Optional[str] = None
    device: Optional[str] = None


class OptimizationRequest(BaseModel):
    segments: List[UserSegment]


class OptimizationResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_processed: int
    avg_optimization_score: float


class TrainRequest(BaseModel):
    size: int = Field(default=2000, ge=100, le=100000)


class RecommendationsResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    total_recommendations: int
    optimization_threshold: float


class PricingMessageRequest(BaseModel):
    segment: UserSegment
    message_type: str = "pricing_offer"


class AnalyticsRequest(BaseModel):
    sample_size: int = 500


class AnalyticsResponse(BaseModel):
    avg_optimization_score: float
    high_value_segment_ratio: float
    medium_value_segment_ratio: float
    low_value_segment_ratio: float
    sample_size: int
    data_source: Optional[str] = "unknown"


class EvaluationResponse(BaseModel):
    model_config = {'protected_namespaces': ()}
    
    accuracy: float
    test_samples: int
    trained: bool
    model_name: str


# Plan performance tracking
class PlanPerformanceEvent(BaseModel):
    user_id: str
    plan_id: str
    event: Literal["view", "consider", "convert", "refund", "default"]
    amount: Optional[float] = 0.0
    segment_info: Optional[Dict[str, Any]] = None


class PlanAnalyticsRequest(BaseModel):
    plan_ids: Optional[List[str]] = None
    segment_filter: Optional[str] = None
    time_range_days: int = 30


class SegmentInsightsRequest(BaseModel):
    sample_size: int = 500
    use_llm: bool = False
    focus_segments: Optional[List[str]] = None