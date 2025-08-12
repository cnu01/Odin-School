from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def refermore_home():
    return {"status": "ok"}
