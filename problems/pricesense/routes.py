from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, HTTPException

from .models import (
    MessageRequest,
    MessageResponse,
    RecommendRequest,
    RecommendResponse,
    OutcomeEvent,
    DiagnosticsResponse,
)
from .service import PricesenseService

router = APIRouter()


@router.get("/")
async def pricesense_home():
    return {
        "problem": "PriceSense - Pricing Optimization",
        "description": "AI-driven pricing and payment plan optimization",
        "status": "Ready for development",
    }


@router.post("/recommend", response_model=RecommendResponse)
async def recommend(req: RecommendRequest):
    svc = PricesenseService()
    # Prefer DB plans; fall back to provided or synthetic only if DB empty/unavailable
    db_plans = await svc.fetch_plans_from_db()
    plans = req.plans or db_plans
    if not plans:
        raise HTTPException(status_code=503, detail="No plans available in DB and none provided in request.")

    seg = req.context or (req.user.segment if req.user else None)
    if seg is None:
        # Try fetching a random user segment from DB only
        users = await svc.fetch_random_users_from_db(n=1)
        if not users:
            raise HTTPException(status_code=503, detail="No users available in DB and no context/user provided.")
        seg = users[0].segment
    try:
        best_id, reasons, risk, alts = svc.recommend(seg=seg, plans=plans)
    except Exception as e:
        if getattr(PricesenseService, "AI_REQUIRED", True):
            raise HTTPException(status_code=503, detail=f"AI recommend failed: {e}")
        raise
    return RecommendResponse(plan_id=best_id, reasons=reasons, risk=risk, alternatives=alts)


@router.post("/message", response_model=MessageResponse)
async def generate_plan_messages(req: MessageRequest):
    svc = PricesenseService()
    try:
        msgs = await svc.generate_messages(req)
    except Exception as e:
        if getattr(PricesenseService, "AI_REQUIRED", True):
            raise HTTPException(status_code=503, detail=f"AI message generation failed: {e}")
        raise
    return MessageResponse(messages=msgs)


@router.post("/synthetic")
async def synthetic(seed: Optional[int] = None, n: int = 100):
    """Seed MongoDB with synthetic plans/users, then return counts and small samples.
    Note: Synthetic generators are deprecated for runtime; this endpoint is for seeding only.
    """
    svc = PricesenseService(seed=seed)
    result = await svc.seed_db(n=n, overwrite=True)
    # Provide samples for quick verification
    plans = await svc.fetch_plans_from_db()
    users = await svc.fetch_random_users_from_db(n=3)
    return {
        "seed_result": result,
        "plans_sample": [p.model_dump() for p in plans],
        "users_sample": [u.model_dump() for u in users],
    }


@router.post("/outcomes")
async def ingest_outcome(evt: OutcomeEvent):
    svc = PricesenseService()
    return await svc.ingest_outcome(evt)


@router.get("/diagnostics", response_model=DiagnosticsResponse)
async def diagnostics(baseline_days: int | None = None, narrate: bool = False):
    svc = PricesenseService()
    data = await svc.diagnostics(baseline_days=baseline_days, narrate=narrate)
    if not data.get("db_connected"):
        # Return empty shape if DB not connected
        return DiagnosticsResponse(total_events=0, by_plan={}, by_segment_key={})
    return DiagnosticsResponse(
        total_events=data["total_events"],
        by_plan=data["by_plan"],
        by_segment_key=data["by_segment_key"],
        baseline_by_plan=data.get("baseline_by_plan"),
        baseline_by_segment_key=data.get("baseline_by_segment_key"),
        deltas=data.get("deltas"),
        ai_summary=data.get("ai_summary"),
    )
