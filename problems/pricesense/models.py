from __future__ import annotations

from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field


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
