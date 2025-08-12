from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import json

from .service import CreatorFitService
from .models import AnalysisRequest, PredictionResponse, ErrorResponse, ProgramType

router = APIRouter()

def get_service():
    """Get CreatorFit service instance"""
    return CreatorFitService()



@router.post("/analyze", response_model=PredictionResponse)
async def analyze_creators_csv(
    file: UploadFile = File(..., description="CSV file with creator data"),
    program_type: ProgramType = Form(default=ProgramType.DATA_SCIENCE, description="Program type for analysis"),
    campaign_budget: float = Form(default=100000, ge=0, description="Campaign budget for CPL calculation")
):
    """
    Upload CSV file and get creator analysis with fit scores and lead predictions
    
    This is the main endpoint that:
    1. Takes uploaded CSV file
    2. Analyzes creators using our ML pipeline
    3. Returns JSON with rankings, fit scores, and recommendations
    """
    try:
        # Validate file
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read CSV content
        csv_content = await file.read()
        
        # Get service and analyze
        service = get_service()
        result = await service.analyze_csv(
            csv_content=csv_content,
            program_type=program_type.value,
            campaign_budget=campaign_budget
        )
        
        if result.get('success'):
            return JSONResponse(content=result)
        else:
            raise HTTPException(
                status_code=400, 
                detail=result.get('error', 'Analysis failed')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.post("/forecast")
async def forecast_creator_leads(
    creator_data: Dict[str, Any],
    program_type: ProgramType = ProgramType.DATA_SCIENCE
):
    """
    Forecast qualified leads for a specific creator
    
    Send creator data and get lead predictions before booking
    """
    try:
        # Validate required fields
        required_fields = ['creator_id', 'topic', 'recent_video_transcript', 
                          'posting_cadence_days', 'views_90d', 'language', 'category_tag']
        
        missing_fields = [field for field in required_fields if field not in creator_data]
        if missing_fields:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required fields: {missing_fields}"
            )
        
        # Get service and forecast
        service = get_service()
        result = await service.forecast_leads(
            creator_data=creator_data,
            program_type=program_type.value
        )
        
        if result.get('success'):
            return JSONResponse(content=result)
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get('error', 'Forecasting failed')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")



@router.get("/programs")
async def get_available_programs():
    """Get list of available program types"""
    return {
        "programs": [
            {"value": "data_science", "label": "Data Science"},
            {"value": "web_development", "label": "Web Development"}, 
            {"value": "digital_marketing", "label": "Digital Marketing"},
            {"value": "ai_ml", "label": "AI/ML"}
        ],
        "default": "data_science"
    }

@router.get("/health")
async def health_check():
    """Health check for CreatorFit service"""
    try:
        # Check if ML pipeline is available
        try:
            from pathlib import Path
            models_dir = Path("models")
            model_files = [
                "creatorfit_lgb_model.pkl",
                "creatorfit_preprocessor.pkl", 
                "creatorfit_metadata.pkl"
            ]
            
            ml_status = "available" if all((models_dir / f).exists() for f in model_files) else "models_missing"
        except Exception:
            ml_status = "error"
        
        return {
            "status": "healthy",
            "service": "CreatorFit",
            "ml_pipeline": ml_status,
            "models_location": "models/"
        }
        
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }
