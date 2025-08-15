from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import datetime
from .models import (
    LeadIngestRequest, LeadResponse,
    PriorityQueueRequest, PriorityQueueResponse, LeadAnalyticsResponse,
    ContactUpdate, OutreachRequest, WhyLeadRequest, ProblemAnalysisResponse,
    AISolutionsResponse
)
from .service import HotLeadService

router = APIRouter()

# Initialize service
hotlead_service = HotLeadService()

@router.get("/")
async def hotlead_home():
    """HotLead - Sales Lead Scoring & Prioritization"""
    return {
        "problem": "HotLead - Sales Lead Scoring & Prioritization",
        "description": "AI-driven lead scoring and prioritization system with intelligent routing",
        "status": "Production Ready - Real Data Integrated",
        "features": [
            "ML-powered lead conversion prediction",
            "Dynamic priority scoring with 80th percentile threshold",
            "Source intelligence weighting (5× variation)",
            "Behavioral intent amplification",
            "Real-time lead processing and routing",
            "AI-powered outreach message generation",
            "Comprehensive analytics dashboard"
        ],
        "endpoints": {
            "/ingest": "POST - Ingest new leads with ML scoring",
            "/priority-queue": "GET - Get prioritized leads for sales",
            "/train": "POST - Train ML model with synthetic data",
            "/analytics": "GET - Get lead scoring analytics",
            "/status": "GET - System status and model info",
            "/seed": "POST - Seed database with training data",
            "/problem-analysis": "GET - AI-powered problem diagnosis"
        },
        "ml_capabilities": [
            "Random Forest lead conversion prediction",
            "Dynamic threshold adjustment",
            "Multi-factor scoring (source, behavior, timing)",
            "Real-time inference"
        ]
    }

@router.post("/ingest", response_model=LeadResponse)
async def ingest_lead(lead_request: LeadIngestRequest):
    """
    Ingest a new lead with ML-powered scoring and prioritization
    
    This endpoint implements the full HotLead AI system:
    - ML conversion prediction
    - Dynamic priority scoring
    - Source intelligence weighting
    - Behavioral intent analysis
    - Automatic sales rep assignment
    """
    try:
        return await hotlead_service.ingest_lead(lead_request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/priority-queue", response_model=PriorityQueueResponse)
async def get_priority_queue(
    limit: Optional[int] = Query(20, description="Number of leads to return"),
    min_score: Optional[int] = Query(0, description="Minimum priority score"),
    status_filter: Optional[str] = Query(None, description="Filter by lead status"),
    source_filter: Optional[str] = Query(None, description="Filter by lead source")
):
    """
    Get prioritized leads queue for sales team
    
    Returns leads sorted by AI priority score with intelligent filtering.
    Implements PRD requirement for sub-5-minute response to priority leads.
    """
    try:
        request = PriorityQueueRequest(
            limit=limit,
            min_score=min_score,
            status_filter=status_filter,
            source_filter=source_filter
        )
        return await hotlead_service.get_priority_queue(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train")
async def train_hotlead_model(size: int = Query(2000, description="Training data size")):
    """
    Train the HotLead ML model with synthetic EdTech data
    
    Generates comprehensive synthetic leads covering:
    - Multi-source traffic (organic, paid, referral, social)
    - Behavioral patterns (high/medium/low intent)
    - Geographic distribution (Indian cities)
    - Device and timing factors
    - Realistic conversion patterns
    """
    try:
        return await hotlead_service.train_model(size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_prioritization_analytics():
    """
    Get comprehensive HotLead analytics and performance metrics
    
    Provides insights into:
    - Priority queue performance
    - Source conversion analysis
    - Response time tracking
    - ML model effectiveness
    """
    try:
        analytics_data = await hotlead_service.get_analytics()
        return analytics_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def hotlead_status():
    """Get HotLead system status and model information"""
    try:
        model_info = await hotlead_service.get_model_info()
        return {
            "system": "HotLead",
            "status": "active",
            "version": "2.0.0",
            "database": "MongoDB",
            "ml_model": model_info,
            "endpoints": [
                "POST /api/hotlead/ingest - Ingest new leads with ML scoring",
                "GET /api/hotlead/priority-queue - Get prioritized leads",
                "POST /api/hotlead/train - Train ML model",
                "GET /api/hotlead/analytics - Get performance analytics",
                "GET /api/hotlead/status - System status",
                "GET /api/hotlead/problem-analysis - AI problem diagnosis"
            ],
            "capabilities": [
                "Lead conversion prediction",
                "Dynamic priority scoring",
                "Source intelligence weighting",
                "Behavioral analysis",
                "Real-time ML inference",
                "MongoDB data persistence",
                "AI-powered insights"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-info")
async def get_model_info():
    """Get detailed information about the HotLead ML model"""
    try:
        return await hotlead_service.get_model_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contact/update")
async def update_contact_status(update: ContactUpdate):
    """Update lead contact status and notes"""
    try:
        return await hotlead_service.update_contact_status(update)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/messages/outreach")
async def generate_outreach_message(request: OutreachRequest):
    """
    Generate AI-powered personalized outreach messages
    
    Uses AWS Bedrock (Claude) for intelligent message generation
    based on lead profile and behavior patterns.
    """
    try:
        return await hotlead_service.generate_outreach_message(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insights/why-this-lead")
async def explain_lead_priority(request: WhyLeadRequest):
    """
    Explain why a specific lead is prioritized
    
    Provides transparent AI decision-making with factor analysis
    for sales team understanding and trust.
    """
    try:
        return await hotlead_service.explain_lead_priority(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/seed")
async def seed_hotlead_database(size: int = Query(2000, description="Number of leads to generate")):
    """
    Seed MongoDB with synthetic HotLead data and train model
    
    This endpoint:
    1. Generates realistic EdTech lead data
    2. Saves to MongoDB leads collection
    3. Trains the ML model
    4. Returns statistics
    """
    try:
        return await hotlead_service.seed_database(size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-prediction")
async def test_lead_prediction(
    source: str = Query("organic", description="Lead source"),
    page_views: int = Query(5, description="Number of page views"),
    time_on_site: int = Query(300, description="Time on site in seconds"),
    demo_requests: int = Query(0, description="Number of demo requests")
):
    """
    Test lead prediction with sample data for demo purposes
    """
    try:
        from ml.hotlead_model import predict_lead_conversion
        
        sample_lead = {
            "source": source,
            "page_views": page_views,
            "time_on_site": time_on_site,
            "demo_requests": demo_requests,
            "course_pages_viewed": 2,
            "downloads_count": 1,
            "location": "Bangalore, India",
            "device": "desktop",
            "hour": 14,
            "day_of_week": 3,
            "is_return_visitor": True
        }
        
        result = await predict_lead_conversion(sample_lead)
        return {
            "test_data": sample_lead,
            "prediction_result": result,
            "message": "This is a test prediction for demo purposes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/problem-analysis", response_model=ProblemAnalysisResponse)
async def get_problem_analysis(
    force_refresh: Optional[bool] = Query(False, description="Force refresh analysis (bypass cache)")
):
    """
    Get complete problem diagnosis and analysis for HotLead frontend display
    Shows identified issues, segment challenges, and implementation status
    
    Parameters:
    - force_refresh: If True, generates new analysis instead of using cached version
    """
    try:
        analysis = await hotlead_service.get_problem_analysis(force_refresh=force_refresh)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HotLead problem analysis failed: {e}")


@router.get("/ai-solutions", response_model=AISolutionsResponse)
async def get_ai_solutions():
    """
    Get AI-powered solutions and enhancement recommendations for HotLead
    
    Provides:
    - Claude-generated AI solutions for identified problems
    - Enhancement recommendations for existing capabilities  
    - Implementation roadmap with timelines and phases
    - ROI projections and financial impact analysis
    - Technical architecture requirements
    """
    try:
        solutions = await hotlead_service.get_ai_solutions()
        return solutions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Solutions generation failed: {e}")


@router.get("/dashboard-data")
async def get_dashboard_data():
    """
    Get combined data for HotLead dashboard including problems and metrics
    """
    try:
        # Get problem analysis
        problem_analysis = await hotlead_service.get_problem_analysis()
        
        # Get current analytics
        analytics = await hotlead_service.get_analytics()
        
        # Create dashboard summary
        dashboard_data = {
            "problems_identified": len(problem_analysis.diagnosed_problems),
            "segments_analyzed": len(problem_analysis.segment_challenges),
            "implementation_progress": len([status for status in problem_analysis.implementation_status.values() if "✅" in status]),
            "total_implementation_items": len(problem_analysis.implementation_status),
            "conversion_opportunity": problem_analysis.overall_impact.get("conversion_optimization", "₹21L+ annually"),
            "efficiency_improvement": problem_analysis.overall_impact.get("efficiency_improvement", "3x improvement"),
            "problem_analysis": problem_analysis,
            "current_analytics": analytics,
            "last_updated": datetime.now().isoformat()
        }
        
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HotLead dashboard data failed: {e}")

