from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def trustdesk_home():
    """TrustDesk - Comment/Review Management"""
    return {
        "problem": "TrustDesk - Comment/Review Management",
        "description": "Brand safety and response automation",
        "status": "Ready for development"
    }

# TODO: Add your routes here
