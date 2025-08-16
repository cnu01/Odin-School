from pydantic import BaseModel
from typing import List, Dict, Any, Optional
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
    segment_type: str
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


# AI Solution Models for OneTruth
class DataUnificationSolution(BaseModel):
    """Model for data unification solution"""
    solution_id: str
    title: str
    description: str
    technical_approach: str
    benefits: List[str]
    implementation_effort: str
    expected_roi: str
    success_metrics: List[str]


class ExecutiveBriefingSolution(BaseModel):
    """Model for executive briefing solution"""
    solution_id: str
    title: str
    description: str
    ai_capabilities: List[str]
    automation_features: List[str]
    decision_support: List[str]
    implementation_effort: str
    expected_roi: str


class SolutionPrioritization(BaseModel):
    """Model for solution prioritization"""
    solution_id: str
    impact_score: float
    effort_score: float
    roi_potential: str
    timeline: str
    risk_level: str
    business_priority: str


class OneTruthSolutionsResponse(BaseModel):
    """Complete solutions response for OneTruth"""
    data_unification: DataUnificationSolution
    executive_briefing: ExecutiveBriefingSolution
    prioritization: List[SolutionPrioritization]
    combined_impact: Dict[str, str]


class BusinessAnalyticsRecord(BaseModel):
    """Model for business analytics data"""
    # CRM Metrics
    crm_lead_volume: int
    crm_qualified_rate: float
    crm_enrollment_rate: float
    crm_refund_rate: float
    
    # GA4 Metrics
    ga4_sessions: int
    ga4_bounce_rate: float
    ga4_conversion_rate: float
    ga4_avg_session_duration: float
    
    # Ad Metrics
    ad_spend_total: float
    ad_cpl: float
    ad_ctr: float
    ad_conversion_rate: float
    
    # Support Metrics
    support_ticket_volume: int
    support_csat_score: float
    support_resolution_time: float
    
    # Telephony Metrics
    telephony_connect_rate: float
    telephony_call_volume: int
    telephony_booking_rate: float
    
    # LMS Metrics
    lms_active_users: int
    lms_completion_rate: float
    lms_engagement_score: float
    
    # Additional fields
    week_date: str
    business_health_anomaly: Optional[bool] = None

class TrainingRequest(BaseModel):
    """Request model for training the OneTruth model"""
    size: int = 2000

class DashboardRequest(BaseModel):
    """Request model for dashboard data"""
    time_range: str = "7d"  # 7d, 30d, 90d
    include_anomalies: bool = True

class ExecutiveBriefRequest(BaseModel):
    """Request model for executive brief"""
    use_llm: bool = False
    horizon_days: int = 7
    include_decisions: bool = True

class DataVerificationRequest(BaseModel):
    """Request model for data verification"""
    systems: List[str] = ["CRM", "GA4", "Ads", "Support", "Telephony", "LMS"]
    time_range_days: int = 7

class AnomalyDetectionResponse(BaseModel):
    """Response model for anomaly detection"""
    anomaly_flags: List[bool]
    anomaly_scores: List[float]
    severity_levels: List[str]
    total_anomalies: int
    avg_anomaly_score: float

class BusinessHealthResponse(BaseModel):
    """Response model for business health analysis"""
    overall_health_score: float
    component_scores: Dict[str, float]
    health_grade: str
    key_insights: List[str]

class ExecutiveDecisionResponse(BaseModel):
    """Response model for executive decisions"""
    decisions: List[Dict[str, Any]]
    decision_urgency: str
    estimated_weekly_impact: str

class ModelEvaluationResponse(BaseModel):
    """Response model for model evaluation"""
    evaluation_results: Dict[str, Any]
    predictions: List[Dict[str, Any]]
    top_features: List[Dict[str, Any]]
    ml_model_info: Dict[str, Any]  # Renamed to avoid conflict with protected namespace

class StatusResponse(BaseModel):
    """Response model for system status"""
    system: str
    status: str
    version: str
    model: Dict[str, Any]
    capabilities: List[str]

class SeedResponse(BaseModel):
    """Response model for data seeding"""
    message: str
    records_created: int
    sample_data: List[Dict[str, Any]]

class AnalyticsOutcome(BaseModel):
    """Model for analytics outcome tracking"""
    metric_name: str
    predicted_value: float
    actual_value: float
    timestamp: datetime
    
class AnalyticsDiagnosticsResponse(BaseModel):
    """Response model for analytics diagnostics"""
    total_records: int
    avg_health_score: float
    anomaly_rate: float
    data_quality_score: float
    recent_predictions: List[Dict[str, Any]]
