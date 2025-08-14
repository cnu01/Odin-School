from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime
from .models import (
    UserSegment, OptimizationRequest, PricingMessageRequest, MessageResponse,
    TrainRequest, AnalyticsResponse, EvaluationResponse, RecommendationsResponse,
    ProblemAnalysisResponse
)
from .service import PricesenseService

router = APIRouter()

_service: Optional[PricesenseService] = None

def get_service() -> PricesenseService:
    global _service
    if _service is None:
        _service = PricesenseService()
    return _service


@router.get("/")
async def pricesense_home():
    return {
        "problem": "PriceSense - Pricing Optimization",
        "description": "AI-driven pricing and payment plan optimization using ML",
        "status": "Ready",
        "endpoints": [
            "GET /api/pricesense/status",
            "GET /api/pricesense/problem-analysis - Problem diagnosis for frontend",
            "GET /api/pricesense/dashboard-data - Complete dashboard data",
            "POST /api/pricesense/train?size=2000",
            "POST /api/pricesense/optimize",
            "GET /api/pricesense/recommendations",
            "POST /api/pricesense/message",
            "GET /api/pricesense/analytics",
            "GET /api/pricesense/evaluate",
        ],
    }


@router.get("/status")
async def pricesense_status():
    try:
        return await get_service().get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {e}")


@router.post("/train")
async def train_pricesense(size: int = 2000):
    try:
        return await get_service().train(size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {e}")


@router.post("/optimize")
async def optimize_plans(segments: List[UserSegment]):
    try:
        return await get_service().optimize_plan_selection(segments)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {e}")


@router.get("/recommendations")
async def get_recommendations(limit: int = 20, threshold: float = 70.0):
    try:
        return await get_service().get_recommendations(limit=limit, threshold=threshold)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations failed: {e}")


@router.post("/message", response_model=MessageResponse)
async def generate_pricing_message(request: PricingMessageRequest):
    try:
        return await get_service().generate_message(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Message generation failed: {e}")


@router.post("/messages/personalize")
async def personalize_pricing_message(segment: UserSegment):
    try:
        request = PricingMessageRequest(segment=segment)
        result = await get_service().generate_message(request)
        return {"message": result.messages[0] if result.messages else "", "insights": result.insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Message personalization failed: {e}")


@router.post("/performance/track")
async def track_performance(event: Dict[str, Any]):
    try:
        return await get_service().track_plan_performance(event)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance tracking failed: {e}")


@router.get("/analytics")
async def analytics(sample_size: int = 500):
    try:
        return await get_service().analytics(sample_size=sample_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {e}")


@router.get("/evaluate")
async def evaluate(sample_size: int = 100):
    try:
        return await get_service().evaluate(sample_size=sample_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {e}")


@router.get("/analytics/summary")
async def analytics_summary(sample_size: int = 500):
    try:
        return await get_service().analytics_summary(sample_size=sample_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics summary failed: {e}")


@router.post("/analytics/plan-performance")
async def get_plan_analytics(request: Dict[str, Any]):
    try:
        return await get_service().get_plan_analytics(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan analytics failed: {e}")


@router.post("/segments/insights")
async def segment_insights(request: Dict[str, Any]):
    try:
        sample_size = request.get("sample_size", 500)
        focus_segments = request.get("focus_segments", [])
        
        # Get basic analytics
        analytics = await get_service().analytics(sample_size=sample_size)
        
        # Generate insights narrative
        insights = []
        if analytics.high_value_segment_ratio > 0.3:
            insights.append("Strong high-value segment presence indicates premium pricing opportunities.")
        if analytics.avg_optimization_score < 60:
            insights.append("Average optimization scores suggest room for plan structure improvements.")
        
        narrative = " ".join(insights) if insights else "Segments show balanced distribution across value tiers."
        
        return {
            "insights": narrative,
            "analytics": analytics,
            "focus_segments": focus_segments,
            "sample_size": sample_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Segment insights failed: {e}")


@router.get("/problem-analysis", response_model=ProblemAnalysisResponse)
async def get_problem_analysis():
    """
    Get complete problem diagnosis and analysis for frontend display
    Shows identified issues, segment challenges, and implementation status
    """
    try:
        service = get_service()
        analysis = await service.get_problem_analysis()
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Problem analysis failed: {e}")


@router.get("/dashboard-data")
async def get_dashboard_data():
    """
    Get combined data for PriceSense dashboard including problems and metrics
    """
    try:
        service = get_service()
        
        # Get problem analysis
        problem_analysis = await service.get_problem_analysis()
        
        # Get current analytics
        analytics = await service.analytics()
        
        # Create dashboard summary
        dashboard_data = {
            "problems_identified": len(problem_analysis.diagnosed_problems),
            "segments_analyzed": len(problem_analysis.segment_challenges),
            "implementation_progress": len([status for status in problem_analysis.implementation_status.values() if "✅" in status]),
            "total_implementation_items": len(problem_analysis.implementation_status),
            "revenue_opportunity": problem_analysis.overall_impact.get("revenue_opportunity", "₹2.5M+ annually"),
            "conversion_improvement": problem_analysis.overall_impact.get("conversion_improvement", "15-25%"),
            "problem_analysis": problem_analysis,
            "current_analytics": analytics,
            "last_updated": datetime.now().isoformat()
        }
        
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard data failed: {e}")