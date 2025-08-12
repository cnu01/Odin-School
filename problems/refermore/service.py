from typing import Dict, List, Any, Optional
from database import get_database
from .models import (
    ReferralProfile, ScoreResponse, MessageResponse, 
    ReferralOutcomeEvent, ReferralDiagnosticsResponse
)

class RefermoreService:
    """Service class for ReferMore referral system operations"""
    
    def __init__(self):
        self.db = get_database()
        
    async def score_referral_propensity(self, profiles: List[ReferralProfile]) -> ScoreResponse:
        """Score referral propensity for multiple profiles"""
        try:
            results = []
            total_propensity = 0
            
            for profile in profiles:
                # Simple scoring algorithm for demo
                score = (
                    profile.completion_rate * 0.3 +
                    profile.engagement_score / 100 * 0.2 +
                    profile.satisfaction_rating / 10 * 0.2 +
                    min(profile.prior_referrals / 5, 1) * 0.15 +
                    (1 - profile.last_active_days / 30) * 0.15
                )
                
                result = {
                    "profile": profile.model_dump(),
                    "propensity_score": round(score, 3),
                    "confidence": 0.85,
                    "insights": {"key_factor": "high_engagement"},
                    "recommendation": "high_priority" if score > 0.6 else "standard"
                }
                
                results.append(result)
                total_propensity += score
            
            avg_propensity = total_propensity / len(profiles) if profiles else 0
            
            return ScoreResponse(
                results=results,
                total_processed=len(profiles),
                avg_propensity=round(avg_propensity, 3)
            )
        except Exception as e:
            raise Exception(f"Scoring failed: {e}")
    
    async def generate_referral_message(self, profile: ReferralProfile, message_type: str = "referral_invite") -> MessageResponse:
        """Generate personalized referral message"""
        try:
            # Simple message generation for demo
            if profile.satisfaction_rating >= 8:
                message = f"Hi! Since you loved our course (rating: {profile.satisfaction_rating}/10), would you recommend it to friends?"
            else:
                message = "Hi! Would you like to refer our course to friends and earn rewards?"
            
            return MessageResponse(
                message=message,
                insights={"personalization": "satisfaction_based"},
                confidence=0.80
            )
        except Exception as e:
            raise Exception(f"Message generation failed: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get ReferMore system status"""
        return {
            "system": "ReferMore", 
            "status": "active", 
            "version": "1.0.0",
            "database_connected": self.db is not None
        }
