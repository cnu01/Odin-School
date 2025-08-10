from pydantic import BaseModel

class CommentInput(BaseModel):
    """Request model for comment analysis"""
    comment_text: str

class AnalyzedComment(BaseModel):
    """Response model for analyzed comment with AI insights"""
    original_comment: str
    sentiment: str
    urgency_score: int
    is_sensitive: bool
    suggested_reply: str

class TrustdeskBase(BaseModel):
    """Base model for Trustdesk - define your models here"""
    pass
