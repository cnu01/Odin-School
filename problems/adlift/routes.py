from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
try:
    from models import AnalysisResponse, AnalysisResults
    from service import AdliftService
except ImportError:
    from problems.adlift.models import AnalysisResponse, AnalysisResults
    from problems.adlift.service import AdliftService
import io

router = APIRouter()
adlift_service = AdliftService()

@router.get("/")
async def adlift_home():
    """AdLift - Marketing Campaign Optimization"""
    return {
        "problem": "AdLift - Marketing Campaign Optimization", 
        "description": "AI-driven ad optimization and creative generation",
        "status": "Ready for development"
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AdLift Marketing Optimizer",
        "version": "1.0.0"
    }

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_csv(file: UploadFile = File(...)):
    """Analyze uploaded CSV file and return comprehensive results"""
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Analyze CSV
        analysis_results = adlift_service.analyze_csv(csv_content)
        
        return AnalysisResponse(
            success=True,
            message="Analysis completed successfully",
            data=analysis_results
        )
        
    except Exception as e:
        return AnalysisResponse(
            success=False,
            message=f"Analysis failed: {str(e)}",
            data=None
        )
