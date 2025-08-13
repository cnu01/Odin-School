from fastapi import APIRouter, HTTPException
from .service import FirsttouchService
from .models import (
    CallOptimizationRequest, CallOptimizationResponse,
    CallAnalyticsRequest, CallAnalyticsResponse,
    ProblemAnalysisResponse, ModelTrainingRequest,
    ModelTrainingResponse, ModelEvaluationResponse
)

router = APIRouter()

def get_service():
    """Get FirstTouch service instance"""
    return FirsttouchService()

@router.get("/")
async def firsttouch_home():
    """FirstTouch AI System - Call Timing and Script Optimization"""
    return {
        "problem": "FirstTouch AI - Call Timing & Script Optimization",
        "description": "AI-powered sales call optimization with timing predictions and script recommendations",
        "status": "Ready",
        "endpoints": [
            "GET /api/firsttouch/status",
            "POST /api/firsttouch/optimize-call-timing",
            "POST /api/firsttouch/call-analytics", 
            "GET /api/firsttouch/problem-analysis",
            "POST /api/firsttouch/train?size=2000",
            "GET /api/firsttouch/evaluate?sample_size=100"
        ],
        "model_info": "XGBoost classifier trained on 2000+ call scenarios"
    }

@router.get("/status")
async def get_status():
    """Get FirstTouch system status and model information"""
    try:
        service = get_service()
        return await service.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {e}")

@router.post("/optimize-call-timing", response_model=CallOptimizationResponse)
async def optimize_call_timing(request: CallOptimizationRequest):
    """
    Get optimal call timing and success probability for a lead
    Core feature for lead prioritization and agent guidance
    """
    try:
        service = get_service()
        return await service.optimize_call_timing(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Call optimization failed: {e}")

@router.post("/call-analytics", response_model=CallAnalyticsResponse) 
async def get_call_analytics(request: CallAnalyticsRequest):
    """
    Get call performance analytics and insights
    For performance metrics dashboard
    """
    try:
        service = get_service()
        return await service.get_call_analytics(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {e}")

@router.get("/problem-analysis", response_model=ProblemAnalysisResponse)
async def get_problem_analysis():
    """
    Get data-driven business problem analysis
    Shows speed-to-lead issues and optimization opportunities
    """
    try:
        service = get_service() 
        return await service.get_problem_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Problem analysis failed: {e}")

@router.post("/train", response_model=ModelTrainingResponse)
async def train_model(request: ModelTrainingRequest):
    """
    Train the FirstTouch ML model (admin function)
    Note: Model is already trained, this is for retraining
    """
    try:
        service = get_service()
        return await service.train_model(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model training failed: {e}")

@router.get("/evaluate", response_model=ModelEvaluationResponse)
async def evaluate_model(sample_size: int = 100):
    """
    Evaluate model performance (admin function)
    """
    try:
        service = get_service()
        return await service.evaluate_model(sample_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model evaluation failed: {e}")
