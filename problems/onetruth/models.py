from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

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
    model_info: Dict[str, Any]

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
