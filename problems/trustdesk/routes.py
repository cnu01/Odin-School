from fastapi import APIRouter, HTTPException
from .models import CommentInput, AnalyzedComment
from .service import TrustdeskService

router = APIRouter()

# Initialize service
trustdesk_service = TrustdeskService()

@router.get("/")
async def trustdesk_home():
    """TrustDesk - Comment/Review Management"""
    return {
        "problem": "TrustDesk - Comment/Review Management",
        "description": "Brand safety and response automation with AI-powered sentiment analysis",
        "status": "Active - AI Analysis Ready",
        "endpoints": {
            "/analyze": "POST - Analyze customer comments with AI"
        }
    }

@router.post("/analyze", response_model=AnalyzedComment)
async def analyze_comment(comment_input: CommentInput):
    """
    Analyze a customer comment using AI for sentiment, urgency, and response generation
    
    Args:
        comment_input: CommentInput containing the comment text
        
    Returns:
        AnalyzedComment with AI analysis and suggested reply
    """
    try:
        # Process comment with AI analysis
        analyzed_comment = await trustdesk_service.analyze_comment(comment_input.comment_text)
        return analyzed_comment
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing comment: {str(e)}"
        )
