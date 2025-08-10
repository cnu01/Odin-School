from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def onetruth_home():
    """OneTruth - Marketing Analytics"""
    return {
        "problem": "OneTruth - Marketing Analytics",
        "description": "Unified data analytics and reporting",
        "status": "Ready for development"
    }

# TODO: Add your routes here
