from pydantic import BaseModel
from typing import Dict, Any, Optional, List


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


class CandidatesResponse(BaseModel):
    items: List[Dict[str, Any]]
    total: int
    threshold: float
