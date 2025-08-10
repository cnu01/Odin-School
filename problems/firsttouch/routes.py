from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def firsttouch_home():
    """FirstTouch BOT - Sales Automation"""
    return {
        "problem": "FirstTouch BOT - Sales Automation",
        "description": "AI-powered first contact automation",
        "status": "Ready for development"
    }

# TODO: Add your routes here
