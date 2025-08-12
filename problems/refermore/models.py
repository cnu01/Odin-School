from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Literal
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


class ReferralProfile(BaseModel):
    # Match ml.refermore_model.FEATURES
    completion_rate: float = 0.7
    engagement_score: int = 60
    satisfaction_rating: int = 8
    invites_sent: int = 0
    link_clicks: int = 0
    signups_generated: int = 0
    forum_posts: int = 0
    social_shares: int = 0
    last_active_days: int = 7
    course_count: int = 1
    certificate_earned: bool = False
    cohort_rank_percentile: float = 50
    net_promoter_score: int = 20
    prior_referrals: int = 0
    has_reward_claimed: bool = False
    # Optional fields for messaging personalization
    name: Optional[str] = None
    course_completed: Optional[str] = None


class ScoreRequest(BaseModel):
    profiles: List[ReferralProfile]


class ScoreResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_processed: int
    avg_propensity: float


class TrainRequest(BaseModel):
    size: int = Field(default=2000, ge=100, le=100000)


class CandidatesResponse(BaseModel):
    candidates: List[Dict[str, Any]]
    total_candidates: int
    threshold: float


class MessageRequest(BaseModel):
    profile: ReferralProfile
    message_type: str = "referral_invite"


class MessageResponse(BaseModel):
    message: str
    insights: Dict[str, Any]
    confidence: float


class AnalyticsRequest(BaseModel):
    sample_size: int = 500


class AnalyticsResponse(BaseModel):
    avg_propensity: float
    high_bucket_ratio: float
    medium_bucket_ratio: float
    low_bucket_ratio: float
    sample_size: int


class EvaluationResponse(BaseModel):
    accuracy: float
    test_samples: int
    trained: bool
    model_name: str


# Additional schemas to mirror backend endpoints more closely
class TrackEvent(BaseModel):
    referrer_id: str
    event: Literal["invite", "click", "signup", "converted", "payout"]
    amount: Optional[float] = 0.0


class ProgressMessageRequest(BaseModel):
    referrer_id: str
    name: Optional[str] = None
    use_llm: bool = False


class AnalyticsInsightsRequest(BaseModel):
    sample_size: int = 500
    use_llm: bool = False
    horizon_days: int = 7
