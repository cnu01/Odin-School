# ReferMore module - Referral System Enhancement
try:
	from .routes import router  # type: ignore
except Exception as _import_exc:  # Fallback to keep app booting even if routes has issues
	from fastapi import APIRouter

	router = APIRouter()
	_import_error_message = str(_import_exc)

	@router.get("/status")
	async def degraded_status():
		return {"status": "degraded", "error": _import_error_message}

__all__ = ["router"]
