from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
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


# AI Solutions Models
class AISolution(BaseModel):
    """Model for individual AI solution recommendations"""
    solution_id: str
    title: str
    description: str
    problem_addressed: str
    implementation_complexity: str  # "Low", "Medium", "High"
    expected_impact: str
    technical_requirements: List[str]
    timeline_weeks: int
    success_metrics: List[str]
    current_status: str  # "Not Started", "In Progress", "Completed"
    confidence_score: float  # 0.0 to 1.0


class AIEnhancement(BaseModel):
    """Model for AI enhancement capabilities"""
    enhancement_id: str
    category: str  # "Predictive", "Automation", "Optimization", "Personalization"
    name: str
    description: str
    current_capability: str
    enhanced_capability: str
    improvement_metrics: Dict[str, Any]
    implementation_effort: str


class AISolutionsResponse(BaseModel):
    """Complete AI solutions response for frontend display"""
    solutions: List[AISolution] 
    enhancements: List[AIEnhancement]
    implementation_roadmap: Dict[str, Any]
    roi_projection: Dict[str, Any]
    technical_architecture: Dict[str, Any]
    prioritization_analysis: Optional[Dict[str, Any]] = None


class LeadIngestRequest(BaseModel):
    """Request model for ingesting a new lead"""
    email: EmailStr
    phone: Optional[str] = None
    source: str
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    page_views: Optional[int] = 1
    time_on_site: Optional[float] = 30.0
    course_pages_viewed: Optional[int] = 0
    downloads_count: Optional[int] = 0
    form_submissions: Optional[int] = 1
    demo_requests: Optional[int] = 0
    location: Optional[str] = None
    device: Optional[str] = "desktop"
    referrer_url: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    experience_level: Optional[str] = None
    is_return_visitor: Optional[bool] = False
    session_id: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = {}

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

class LeadResponse(BaseModel):
    """Response model for lead ingestion"""
    lead_id: str
    email: str
    source: str
    priority_score: int
    is_priority: bool
    lead_temperature: str
    conversion_probability: float
    recommended_action: str
    assigned_rep: Optional[str] = None
    status: str
    created_at: datetime
    insights: Dict[str, Any]

class PriorityQueueRequest(BaseModel):
    """Request model for priority queue"""
    limit: Optional[int] = 20
    min_score: Optional[int] = 70
    status_filter: Optional[str] = None
    source_filter: Optional[str] = None

class PriorityQueueResponse(BaseModel):
    """Response model for priority queue"""
    total_priority_leads: int
    leads: List[Dict[str, Any]]
    queue_summary: Dict[str, Any]

class LeadAnalyticsResponse(BaseModel):
    """Response model for lead analytics"""
    analytics_summary: str
    current_metrics: Dict[str, Any]
    source_performance: List[Dict[str, Any]]
    solutions_ranked_by_impact: List[Dict[str, Any]]
    success_metrics_tracking: Dict[str, Any]

class ContactUpdate(BaseModel):
    """Request model for updating lead contact status"""
    lead_id: str
    contacted_by: str
    contact_method: str
    notes: Optional[str] = None
    outcome: Optional[str] = None
    next_action: Optional[str] = None

class OutreachRequest(BaseModel):
    """Request model for generating outreach messages"""
    lead_id: str
    rep_name: str
    contact_method: str = "email"
    personalization_data: Optional[Dict[str, Any]] = {}

class WhyLeadRequest(BaseModel):
    """Request model for lead prioritization explanation"""
    lead_id: str
