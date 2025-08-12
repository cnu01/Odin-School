from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

class ReferralProfile(BaseModel):
    """Model for referral profile data"""
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

class ScoreRequest(BaseModel):
    """Request model for scoring referral propensity"""
    profiles: List[ReferralProfile]

class ScoreResponse(BaseModel):
    """Response model for referral scoring"""
    results: List[Dict[str, Any]]
    total_processed: int
    avg_propensity: float

class MessageRequest(BaseModel):
    """Request model for personalized message generation"""
    profile: ReferralProfile
    message_type: str = "referral_invite"

class MessageResponse(BaseModel):
    """Response model for generated messages"""
    message: str
    insights: Dict[str, Any]
    confidence: float

class ReferralOutcomeEvent(BaseModel):
    """Model for referral outcome tracking"""
    referrer_id: str
    predicted_propensity: float
    actual_referral_made: bool
    timestamp: datetime

class ReferralDiagnosticsResponse(BaseModel):
    """Response model for referral system diagnostics"""
    total_users: int
    avg_propensity: float
    high_propensity_count: int
    referral_conversion_rate: float
    recent_activity: List[Dict[str, Any]]
