from __future__ import annotations

from typing import List, Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ReferralHistory(BaseModel):
    """Historical referral stats for a learner."""
    invites_sent: int = 0
    clicks: int = 0
    signups: int = 0
    payouts_total: int = 0  # count of payouts


class Learner(BaseModel):
    """Learner profile used for referral propensity scoring and messaging."""
    id: str
    name: str
    email: str
    completion_pct: float = Field(ge=0, le=100)
    feedback_score: int = Field(description="NPS-like score -100..100", ge=-100, le=100)
    participation_count: int = Field(description="Activities in last 30 days", ge=0)
    last_activity_at: datetime
    referral_link: str
    referral_history: ReferralHistory
    last_nudged_at: Optional[datetime] = None


class ScoreComponents(BaseModel):
    completion: float
    feedback: float
    participation: float
    recency: float
    prior_referrals: float


class ScoreItem(BaseModel):
    learner_id: str
    score: float = Field(ge=0, le=1)
    tier: Literal["high", "medium", "low"]
    reasons: List[str]
    score_components: ScoreComponents
    suggested_next_nudge_time: Optional[datetime] = None


class ScoreRequest(BaseModel):
    learners: Optional[List[Learner]] = None
    top_k: Optional[int] = Field(default=None, gt=0)
    seed: Optional[int] = None


class ScoreResponse(BaseModel):
    items: List[ScoreItem]


class MessageRequest(BaseModel):
    learner_id: str
    tone: str = "professional"
    variants: int = Field(default=3, ge=1, le=5)


class MessageResponse(BaseModel):
    messages: List[str]


# ---- Outcomes ingestion and diagnostics ----
class ReferralOutcomeEvent(BaseModel):
    learner_id: str
    invited: bool = False
    clicked: bool = False
    signed_up: bool = False
    payout: bool = False
    ts: Optional[str] = None  # ISO timestamp


class ReferralDiagnosticsResponse(BaseModel):
    total_events: int
    funnel: dict
    by_tier: dict
    baseline_funnel: Optional[dict] = None
    baseline_by_tier: Optional[dict] = None
    deltas: Optional[dict] = None
    ai_summary: Optional[str] = None
