from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def closemore_home():
    """CloseMore - Sales Conversation Analysis"""
    return {
        "problem": "CloseMore - Sales Conversation Analysis",
        "description": "AI-powered conversation analysis and insights",
        "status": "Ready for development"
    }

# TODO: Add your routes here
