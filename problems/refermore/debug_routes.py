print("DEBUG: Starting routes.py execution")

try:
    from fastapi import APIRouter, HTTPException
    print("DEBUG: ✅ FastAPI imports successful")
except Exception as e:
    print(f"DEBUG: ❌ FastAPI import failed: {e}")
    raise

try:
    from .models import ReferralProfile, ScoreRequest, ScoreResponse, MessageRequest, MessageResponse
    print("DEBUG: ✅ Models imports successful")
except Exception as e:
    print(f"DEBUG: ❌ Models import failed: {e}")
    raise

try:
    from .service import RefermoreService
    print("DEBUG: ✅ Service import successful")
except Exception as e:
    print(f"DEBUG: ❌ Service import failed: {e}")
    raise

print("DEBUG: Creating router...")
router = APIRouter()
print("DEBUG: ✅ Router created")

print("DEBUG: Creating service...")
refermore_service = RefermoreService()
print("DEBUG: ✅ Service instantiated")

@router.get("/")
async def refermore_home():
    """ReferMore - Referral System Enhancement"""
    return {
        "problem": "ReferMore - Referral System Enhancement",
        "description": "AI-driven referral optimization and automation",
        "status": "Production Ready"
    }

print("DEBUG: ✅ Route defined")
print("DEBUG: Routes.py execution completed successfully")
