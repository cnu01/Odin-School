from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def hotlead_home():
    """HotLead - Sales Lead Scoring & Prioritization"""
    return {
        "problem": "HotLead - Sales Lead Scoring",
        "description": "AI-driven lead scoring and prioritization system",
        "status": "Ready for development"
    }

# TODO: Add your routes here
# Example:
# @router.post("/leads")
# async def create_lead():
#     pass
