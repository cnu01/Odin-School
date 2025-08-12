from fastapi import APIRouter, HTTPException
from typing import Optional

from .models import (
    TrainingRequest, DashboardRequest, ExecutiveBriefRequest, 
    DataVerificationRequest, BusinessAnalyticsRecord, 
    StatusResponse, AnomalyDetectionResponse, BusinessHealthResponse,
    ExecutiveDecisionResponse, ModelEvaluationResponse, SeedResponse,
    AnalyticsOutcome, AnalyticsDiagnosticsResponse
)
from .service import OnetruthService

router = APIRouter()

# Initialize service
onetruth_service = OnetruthService()

@router.get("/")
async def onetruth_home():
    """OneTruth - Marketing Analytics Dashboard"""
    return {
        "problem": "OneTruth - Marketing Analytics",
        "description": "Unified data analytics with AI-powered anomaly detection and executive insights",
        "status": "Production Ready - Real Data Analytics",
        "features": [
            "Multi-source data integration (CRM, GA4, Ads, Support, LMS)",
            "AI anomaly detection with severity scoring",
            "Executive decision recommendations",
            "Business health monitoring",
            "Real-time dashboard analytics"
        ],
        "capabilities": [
            "Unified analytics dashboard",
            "Anomaly detection (2-sigma threshold)", 
            "Executive decision recommendations",
            "Business health scoring",
            "AI-powered insights"
        ]
    }

@router.get("/status", response_model=StatusResponse)
async def onetruth_status():
    """OneTruth system status and model info"""
    from ml.onetruth_model import onetruth_model
    
    return StatusResponse(
        system="OneTruth",
        status="active",
        version="1.0.0",
        model=onetruth_model.get_model_info(),
        capabilities=[
            "Multi-source data integration",
            "Anomaly detection (2-sigma threshold)", 
            "Executive decision recommendations",
            "Business health scoring",
            "AI-powered insights"
        ]
    )

@router.post("/train")
async def train_onetruth_model(size: int = 2000):
    """Train the OneTruth anomaly detection model"""
    try:
        result = await onetruth_service.train_model(size)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {e}")

@router.get("/dashboard")
async def get_unified_dashboard(time_range: str = "7d", include_anomalies: bool = True):
    """Get unified analytics dashboard with business health metrics"""
    try:
        dashboard_data = await onetruth_service.get_dashboard_data(
            time_range=time_range,
            include_anomalies=include_anomalies
        )
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {e}")

@router.get("/anomalies", response_model=AnomalyDetectionResponse)
async def detect_anomalies(time_range: str = "7d"):
    """Detect business anomalies across all integrated systems"""
    try:
        anomalies = await onetruth_service.detect_anomalies(time_range)
        return anomalies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {e}")

@router.post("/executive-brief")
async def generate_executive_brief(use_llm: bool = False, horizon_days: int = 7):
    """Generate AI-powered executive brief with anomalies and decision recommendations"""
    try:
        brief = await onetruth_service.generate_executive_brief(
            use_llm=use_llm,
            horizon_days=horizon_days
        )
        return brief
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Executive brief generation failed: {e}")

@router.get("/decisions", response_model=ExecutiveDecisionResponse)
async def get_executive_decisions():
    """Get the 3 recurring executive decisions with AI recommendations"""
    try:
        decisions = await onetruth_service.get_executive_decisions()
        return decisions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Executive decisions generation failed: {e}")

@router.get("/evaluate", response_model=ModelEvaluationResponse)
async def evaluate_model(sample_size: int = 10):
    """Evaluate OneTruth model performance with test predictions"""
    try:
        evaluation = await onetruth_service.evaluate_model(sample_size)
        return evaluation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model evaluation failed: {e}")

@router.post("/seed", response_model=SeedResponse)
async def seed_onetruth(size: int = 2000):
    """Seed the database with synthetic analytics data and train the model"""
    try:
        result = await onetruth_service.seed_data(size)
        return SeedResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data seeding failed: {e}")

@router.post("/verify")
async def verify_data_consistency(systems: list = None, time_range_days: int = 7):
    """Verify data consistency and quality across integrated business systems"""
    try:
        if systems is None:
            systems = ["CRM", "GA4", "Ads", "Support", "Telephony", "LMS"]
        verification = await onetruth_service.verify_data_consistency(
            systems=systems,
            time_range_days=time_range_days
        )
        return verification
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data verification failed: {e}")

@router.post("/outcomes")
async def record_outcome(outcome: AnalyticsOutcome):
    """Record analytics prediction outcome for model improvement"""
    try:
        result = await onetruth_service.record_analytics_outcome(outcome)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record outcome: {e}")

@router.get("/analytics", response_model=AnalyticsDiagnosticsResponse)
async def get_analytics(sample_size: int = 500):
    """Get analytics performance and model insights"""
    try:
        analytics = await onetruth_service.get_analytics(sample_size)
        return AnalyticsDiagnosticsResponse(**analytics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics retrieval failed: {e}")

@router.post("/synthetic")
async def generate_synthetic_analytics(seed: Optional[int] = None, n: int = 100):
    """Generate synthetic analytics data for testing and development"""
    try:
        from ml.onetruth_model import generate_synthetic_analytics_data
        
        if seed:
            import numpy as np
            np.random.seed(seed)
        
        # Generate synthetic data
        data_df = generate_synthetic_analytics_data(num_samples=n)
        
        # Convert to list of dicts
        synthetic_data = data_df.to_dict('records')
        
        # Convert numpy types to Python types for JSON serialization
        for record in synthetic_data:
            for key, value in record.items():
                if hasattr(value, 'item'):
                    record[key] = value.item()
        
        return {
            "message": f"Generated {n} synthetic analytics records",
            "count": n,
            "sample_data": synthetic_data[:5],  # Return first 5 as sample
            "features": list(synthetic_data[0].keys()) if synthetic_data else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synthetic data generation failed: {e}")

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for OneTruth system"""
    try:
        from ml.onetruth_model import onetruth_model
        
        return {
            "status": "healthy",
            "system": "OneTruth",
            "model_trained": onetruth_model.model is not None,
            "database_connected": onetruth_service.db is not None,
            "timestamp": "2025-08-12T00:00:00Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-08-12T00:00:00Z"
        }
