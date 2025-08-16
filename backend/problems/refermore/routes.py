from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime
from .models import (
    ReferralProfile, CandidatesResponse, ProblemAnalysisResponse
)
from .service import RefermoreService

router = APIRouter()

_service: Optional[RefermoreService] = None

def get_service() -> RefermoreService:
    global _service
    if _service is None:
        _service = RefermoreService()
    return _service


@router.get("/status")
async def refermore_status():
    try:
        return await get_service().get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {e}")


@router.post("/score")
async def score_referral_profile(profile: ReferralProfile):
    try:
        # Backend expects single-profile scoring response with prediction and insights
        svc = get_service()
        resp = await svc.score_referral_propensity([profile])
        item = resp.results[0] if resp.results else {}
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {e}")


@router.get("/candidates")
async def get_candidates(limit: int = 20, threshold: float = 0.6):
    try:
        resp = await get_service().candidates(limit=limit, threshold=threshold)
        # Return the data in the format expected by frontend
        return {
            "total": resp.total,
            "items": resp.items,
            "threshold": resp.threshold
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Candidates retrieval failed: {e}")


@router.post("/messages/personalize")
async def personalize_message(candidate_data: Dict[str, Any]):
    try:
        # Handle both ReferralProfile and candidate object formats
        if "student_name" in candidate_data:
            # This is a candidate object from the frontend - use AI to generate truly personalized content
            from services.aws import get_bedrock_service
            
            name = candidate_data.get("student_name", "there")
            course = candidate_data.get("course_name", "your course")
            completion_rate = candidate_data.get("completion_rate", 0.7)
            engagement_score = candidate_data.get("engagement_score", 60)
            nps = candidate_data.get("net_promoter_score", 7)
            propensity_score = candidate_data.get("propensity_score", 70)
            likelihood = candidate_data.get("likelihood", "Medium")
            forum_posts = candidate_data.get("forum_posts", 0)
            social_shares = candidate_data.get("social_shares", 0)
            certificate_earned = candidate_data.get("certificate_earned", False)
            
            # Try to generate AI-powered message using Claude
            message = None
            try:
                bedrock = get_bedrock_service()
                if hasattr(bedrock, 'bedrock_runtime') and bedrock.bedrock_runtime is not None:
                    # Create detailed prompt for AI to generate truly personalized message
                    prompt = f"""Create a personalized referral message for OdinSchool student with these details:

Student Profile:
- Name: {name}
- Course: {course}
- Completion Rate: {completion_rate*100:.0f}%
- Engagement Score: {engagement_score}/100
- NPS Score: {nps}
- Propensity: {likelihood} ({propensity_score:.0f}%)
- Forum Posts: {forum_posts}
- Social Shares: {social_shares}
- Certificate: {"Earned" if certificate_earned else "In Progress"}

Requirements:
1. Address the student by name personally
2. Reference their specific course and achievements
3. Tailor tone based on their engagement level and propensity
4. Include specific referral rewards (₹2,000 enrollment bonus + ₹1,000 completion bonus)
5. Make it feel genuine and personal, not template-like
6. Keep it under 150 words
7. Use appropriate emojis but don't overdo it
8. End with "OdinSchool Team"

Create a unique message that reflects their specific learning journey and motivations. Don't mention NPS scores or technical metrics directly."""

                    message = await bedrock.generate_text(prompt, max_tokens=300)
                    
                    # Clean up the message
                    if message:
                        message = message.strip()
                        # Ensure it has proper greeting and closing
                        if not message.startswith(("Hi", "Hello", "Hey")):
                            message = f"Hi {name}! 👋\n\n" + message
                        if not "OdinSchool Team" in message:
                            message += "\n\nBest regards,\nOdinSchool Team"
                            
            except Exception as ai_error:
                print(f"AI generation failed: {ai_error}")
                message = None
            
            # Fallback to personalized templates if AI fails
            if not message:
                if likelihood == "High" and completion_rate > 0.8:
                    achievement_phrase = "certificate earned" if certificate_earned else "outstanding progress"
                    social_phrase = f"with {forum_posts} forum contributions" if forum_posts > 5 else "dedication to learning"
                    
                    message = f"""Hi {name}! 🌟

Congratulations on your {achievement_phrase} in {course}! Your {completion_rate*100:.0f}% completion rate and {social_phrase} show real commitment to excellence.

We'd love for you to share this transformative experience with others who could benefit. Our referral program offers:

🎁 ₹2,000 immediate bonus when your referral enrolls
💰 Additional ₹1,000 when they complete their course  
🏆 Recognition as a top community advocate

Your success story could be exactly what someone needs to take their next career step. Ready to help others while earning great rewards?

Best regards,
OdinSchool Team"""
                
                elif likelihood == "Medium" and engagement_score >= 70:
                    course_progress = "Nearly completed" if completion_rate > 0.8 else "Making great progress in"
                    engagement_note = f"Your {engagement_score}/100 engagement shows genuine interest"
                    
                    message = f"""Hello {name}! 👋

{course_progress} {course}! {engagement_note} in learning, and we truly appreciate students like you.

Since you're experiencing firsthand how valuable our programs are, you might know someone who could benefit too:

✅ ₹2,000 referral bonus for successful enrollments
✅ ₹1,000 additional reward for course completions
✅ Build your professional network while helping others

Your authentic recommendation could make all the difference for someone considering their next career move.

Interested in sharing the opportunity?

Warm regards,
OdinSchool Team"""
                
                else:
                    personal_touch = f"in {course}" if course != "your course" else "with us"
                    encouragement = "Every learning journey is valuable" if completion_rate < 0.5 else "Your commitment to learning is inspiring"
                    
                    message = f"""Hi {name}! 🚀

Thank you for being part of our learning community {personal_touch}! {encouragement}, and we believe in the power of shared knowledge.

Would you like to help others discover the same opportunities you're exploring?

🎯 Earn ₹2,000 for successful referrals
💡 Help friends/colleagues advance their careers  
🌟 Join our community of learning advocates

Even if you're still on your own journey, your perspective could be exactly what someone needs to get started.

Ready to make a positive impact?

Best wishes,
OdinSchool Team"""
            
            insights = {
                "propensity_score": propensity_score,
                "likelihood": likelihood,
                "personalization_factors": [
                    f"Completion rate: {completion_rate*100:.0f}%",
                    f"Engagement score: {engagement_score}",
                    f"NPS: {nps}",
                    f"Course: {course}",
                    f"Forum activity: {forum_posts} posts",
                    f"Social sharing: {social_shares} shares"
                ],
                "recommendation": f"Targeting {likelihood.lower()}-propensity referrer with {'AI-generated' if message else 'template-based'} personalized approach"
            }
            
        else:
            # This is a ReferralProfile format - use existing logic
            profile = ReferralProfile(**candidate_data)
            svc = get_service()
            scored = await svc.score_referral_propensity([profile])
            pred = scored.results[0] if scored.results else {}
            msg_resp = await svc.message(profile, "referral_invite")
            message = msg_resp.message
            insights = pred.get("insights", {})
        
        return {
            "message": message,
            "insights": insights,
            "generated_at": datetime.now().isoformat(),
            "message_type": "ai_personalized"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Message generation failed: {e}")


@router.get("/analytics")
async def analytics(sample_size: int = 500):
    try:
        # Return ROI summary like backend tests expect
        return await get_service().analytics_summary(sample_size=sample_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {e}")


@router.get("/problem-analysis", response_model=ProblemAnalysisResponse)
async def get_problem_analysis(force_refresh: bool = False):
    """
    Get complete problem diagnosis and analysis for ReferMore frontend display
    Shows identified issues, segment challenges, and implementation status
    
    Args:
        force_refresh: If True, bypasses cache and generates fresh analysis
    """
    try:
        service = get_service()
        analysis = await service.get_problem_analysis(force_refresh=force_refresh)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ReferMore problem analysis failed: {e}")


@router.get("/dashboard-data")
async def get_dashboard_data(force_refresh: bool = False):
    """
    Get combined data for ReferMore dashboard including problems and metrics
    
    Args:
        force_refresh: If True, bypasses cache and generates fresh analysis
    """
    try:
        service = get_service()
        
        # Get problem analysis with force refresh option
        problem_analysis = await service.get_problem_analysis(force_refresh=force_refresh)
        
        # Get current analytics
        status = await service.get_status()
        
        # Create dashboard summary
        dashboard_data = {
            "problems_identified": len(problem_analysis.diagnosed_problems),
            "segments_analyzed": len(problem_analysis.segment_challenges),
            "implementation_progress": len([status for status in problem_analysis.implementation_status.values() if "✅" in status]),
            "total_implementation_items": len(problem_analysis.implementation_status),
            "growth_opportunity": problem_analysis.overall_impact.get("growth_opportunity", "₹10L+ annually"),
            "participation_improvement": problem_analysis.overall_impact.get("participation_improvement", "40-60%"),
            "problem_analysis": problem_analysis,
            "system_status": status,
            "last_updated": datetime.now().isoformat(),
            "cache_refreshed": force_refresh
        }
        
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ReferMore dashboard data failed: {e}")

