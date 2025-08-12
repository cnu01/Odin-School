from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from .models import (
    ScoreRequest, ScoreResponse, MessageRequest, MessageResponse,
    TrainRequest, AnalyticsResponse, ReferralProfile, TrackEvent,
    ProgressMessageRequest, AnalyticsInsightsRequest
)
from .service import RefermoreService

router = APIRouter()

_service: Optional[RefermoreService] = None

def get_service() -> RefermoreService:
    global _service
    if _service is None:
        _service = RefermoreService()
    return _service


@router.get("/")
async def refermore_home():
    return {
        "problem": "ReferMore - Referral System Enhancement",
        "description": "AI-driven referral optimization and automation",
        "status": "Ready",
        "endpoints": [
            "GET /api/refermore/status",
            "POST /api/refermore/train?size=2000",
            "POST /api/refermore/score",
            "GET /api/refermore/candidates",
            "POST /api/refermore/message",
            "GET /api/refermore/analytics",
            "GET /api/refermore/evaluate",
        ],
    }


@router.get("/status")
async def refermore_status():
    try:
        return await get_service().get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {e}")


@router.post("/train")
async def train_refermore(size: int = 2000):
    try:
        return await get_service().train(size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {e}")


@router.post("/score")
async def score_referral_profile(profile: ReferralProfile):
    try:
        # Backend expects single-profile scoring response with prediction and insights
        svc = get_service()
        resp = await svc.score_referral_propensity([profile])
        item = resp.results[0] if resp.results else {}
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {e}")


@router.get("/candidates")
async def get_candidates(limit: int = 20, threshold: float = 0.6):
    try:
        resp = await get_service().candidates(limit=limit, threshold=threshold)
        # Shape to backend: { total, items: [...] }
        items: List[Dict[str, Any]] = []
        for c in resp.candidates:
            items.append({
                "student_id": c.get("profile", {}).get("student_id", None),
                "score": c.get("propensity_score"),
                "likelihood": c.get("insights", {}).get("likelihood_bucket"),
                "optimal_timing": c.get("insights", {}).get("recommendations", [None])[0] if c.get("insights") else None,
                "suggested_incentive": "standard_reward",
            })
        items.sort(key=lambda x: (x.get("score") or 0), reverse=True)
        return {"total": len(items), "items": items[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Candidates retrieval failed: {e}")


@router.post("/message", response_model=MessageResponse)
async def generate_message(request: MessageRequest):
    try:
        return await get_service().message(request.profile, request.message_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Message generation failed: {e}")


@router.post("/messages/personalize")
async def personalize_message(profile: ReferralProfile):
    try:
        # Reuse single score then message
        svc = get_service()
        scored = await svc.score_referral_propensity([profile])
        pred = scored.results[0] if scored.results else {}
        msg_resp = await svc.message(profile, "referral_invite")
        return {"message": msg_resp.message, "insights": pred.get("insights", {})}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Message generation failed: {e}")


@router.post("/referrals/track")
async def track_referral(event: TrackEvent):
    try:
        return await get_service().track_event(event)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tracking failed: {e}")


@router.get("/analytics")
async def analytics(sample_size: int = 500):
    try:
        # Return ROI summary like backend tests expect
        return await get_service().analytics_summary(sample_size=sample_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {e}")


@router.get("/evaluate")
async def evaluate(sample_size: int = 100):
    try:
        # Return detailed evaluation similar to backend tests
        return await get_service().evaluate_detailed(sample_size=sample_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {e}")


@router.get("/analytics/summary")
async def analytics_summary(sample_size: int = 500):
    try:
        return await get_service().analytics_summary(sample_size=sample_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics summary failed: {e}")


@router.post("/analytics/insights")
async def analytics_insights(req: AnalyticsInsightsRequest):
    try:
        base = await get_service().analytics_summary(sample_size=req.sample_size)
        # Simple rule-based narrative (LLM option exists in service but we keep simple here)
        roi = base.get("roi", {})
        dist = base.get("distribution", base)
        actions = []
        if roi.get("totals", {}).get("signups", 0) < 5:
            actions.append("Launch a limited-time reward to push first 5 signups.")
        if dist.get("high_share", 0) < 30:
            actions.append("Target medium bucket with tailored nudges to boost high-propensity share.")
        narrative = (
            f"Avg propensity {dist.get('avg_propensity', 0)} with {dist.get('high_share', 0)}% high. "
            f"Tracked {roi.get('totals', {}).get('invites', 0)} invites → {roi.get('totals', {}).get('signups', 0)} signups. "
            + ("Next: " + " ".join(actions) if actions else "Keep momentum with top referrers.")
        )
        return {"insight": narrative, "summary": base}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics insights failed: {e}")


@router.post("/messages/progress")
async def progress_message(req: ProgressMessageRequest):
    try:
        return await get_service().progress_message(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Progress message failed: {e}")



