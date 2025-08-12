print("Starting routes.py execution")

from fastapi import APIRouter, HTTPException
print("✅ FastAPI imports successful")

from .models import ReferralProfile, ScoreRequest, ScoreResponse, MessageRequest, MessageResponse
print("✅ Models imports successful")

from .service import RefermoreService
print("✅ Service import successful")

router = APIRouter()
print("✅ Router created")

refermore_service = RefermoreService()
print("✅ Service instantiated")

@router.get("/")
async def refermore_home():
    return {"status": "ok"}

print("✅ Route defined")
print("✅ Routes.py execution completed successfully")
