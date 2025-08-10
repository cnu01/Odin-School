from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, HTTPException

from .models import MessageRequest, MessageResponse, ScoreRequest, ScoreResponse, ReferralOutcomeEvent, ReferralDiagnosticsResponse
from .service import RefermoreService

router = APIRouter()


@router.get("/")
async def refermore_home():
    """
    WHY: Simple health/info endpoint for the feature.
    HOW LLM interprets: N/A.
    HOW to swap with ML later: N/A.
    """
    return {
        "problem": "ReferMore - Referral System Enhancement",
        "description": "AI-driven referral optimization and automation",
        "status": "Ready for development",
    }


@router.post("/score", response_model=ScoreResponse)
async def score_learners(req: ScoreRequest):
    """
    WHY: Rank learners by referral propensity for targeted nudges.
    HOW LLM interprets: Not used here; rule-based now, replaceable with ML later.
    HOW to swap with ML later: Replace service.score_learner with model.predict.
    """
    svc = RefermoreService(seed=req.seed)
    # Prefer request-provided learners; otherwise use DB only
    learners = req.learners or (await svc.fetch_learners_from_db(limit=500))
    if not learners:
        raise HTTPException(status_code=503, detail="No learners available in DB and none provided in request.")
    items = [svc.score_learner(l) for l in learners]
    items.sort(key=lambda x: x.score, reverse=True)
    # AI-assisted: enhance reasons and tiebreak for top subset (bounded)
    top_ai = max(20, req.top_k or 0)
    try:
        items = svc.rerank_and_enhance(items=items, learners=learners, top_k_ai=top_ai)
    except Exception as e:
        if getattr(RefermoreService, "AI_REQUIRED", True):
            raise HTTPException(status_code=503, detail=f"AI scoring failed: {e}")
        raise
    if req.top_k:
        items = items[: req.top_k]
    return ScoreResponse(items=items)


@router.post("/message", response_model=MessageResponse)
async def generate_referral_messages(req: MessageRequest):
    """
    WHY: Generate 3 short professional referral messages via OpenAI with fallback.
    HOW LLM interprets: The prompt includes learner context and a reward phrase.
    HOW to swap with ML later: Keep the interface and replace internals.
    """
    svc = RefermoreService()
    learner = await svc.fetch_learner_by_id(req.learner_id)
    if learner is None:
        raise HTTPException(status_code=404, detail="Learner not found in DB; seed data first.")
    try:
        msgs = await svc.generate_messages(learner=learner, variants=req.variants, tone=req.tone)
    except Exception as e:
        if getattr(RefermoreService, "AI_REQUIRED", False):
            raise HTTPException(status_code=503, detail=f"AI message generation failed: {e}")
        raise
    return MessageResponse(messages=msgs)


@router.post("/synthetic")
async def generate_synthetic(seed: Optional[int] = None, n: int = 100):
    """Seed MongoDB with synthetic learners, then return counts and a small sample.
    Note: Synthetic generators are deprecated for runtime; use DB-backed fetch in other endpoints.
    """
    svc = RefermoreService(seed=seed)
    result = await svc.seed_db(n=n, overwrite=True)
    sample = await svc.fetch_random_learners_from_db(n=1)
    return {"seed_result": result, "sample": [sample[0].model_dump()] if sample else []}


@router.post("/outcomes")
async def ingest_outcome(evt: ReferralOutcomeEvent):
    svc = RefermoreService()
    return await svc.ingest_outcome(evt)


@router.get("/diagnostics", response_model=ReferralDiagnosticsResponse)
async def diagnostics(baseline_days: int | None = None, narrate: bool = False):
    svc = RefermoreService()
    data = await svc.diagnostics(baseline_days=baseline_days, narrate=narrate)
    if not data.get("db_connected"):
        return ReferralDiagnosticsResponse(total_events=0, funnel={}, by_tier={})
    return ReferralDiagnosticsResponse(
        total_events=data["total_events"],
        funnel=data["funnel"],
        by_tier=data["by_tier"],
        baseline_funnel=data.get("baseline_funnel"),
        baseline_by_tier=data.get("baseline_by_tier"),
        deltas=data.get("deltas"),
        ai_summary=data.get("ai_summary"),
    )
