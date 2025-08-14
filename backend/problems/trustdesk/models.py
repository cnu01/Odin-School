from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class CommentInput(BaseModel):
    """Request model for comment analysis"""
    comment_text: str
    customer_name: str = "Anonymous"
    platform: str = "Unknown"
    comment_type: str = "general"

# New Bedrock-compatible models
class CommentRequest(BaseModel):
    """Bedrock-compatible request model for incoming comments"""
    text: str

class AIAnalysisResponse(BaseModel):
    """Bedrock-compatible response model for AI analysis results"""
    urgency: str
    is_sensitive: bool
    summary: str
    draft_reply: str

# Legacy model for backward compatibility
class AnalyzedComment(BaseModel):
    """Legacy response model for analyzed comment with AI insights"""
    original_comment: str
    sentiment: str
    urgency_score: int
    is_sensitive: bool
    suggested_reply: str
    reasoning: str = ""

# RAG-specific models
class RAGCommentRequest(BaseModel):
    """RAG-enabled request model for comment analysis"""
    text: str
    use_rag: bool = True
    include_context: bool = True

class RAGAnalysisResponse(BaseModel):
    """RAG-enhanced response model with knowledge source information"""
    urgency: str
    is_sensitive: bool
    summary: str
    draft_reply: str
    knowledge_sources: List[str] = []  # Sources used from knowledge base
    confidence_score: float = 0.0  # Confidence in the response
    context_used: bool = False

class KnowledgeDocumentInput(BaseModel):
    """Input model for adding knowledge base documents"""
    title: str
    content: str
    category: str  # policy, faq, course_info, procedure
    department: str = "customer_service"
    priority: int = 1  # 1=low, 2=medium, 3=high
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

class FAQInput(BaseModel):
    """Input model for adding FAQ documents"""
    question: str
    answer: str
    category: str
    keywords: List[str] = []

class KnowledgeSearchRequest(BaseModel):
    """Request model for searching knowledge base"""
    query: str
    category: Optional[str] = None
    top_k: int = 5

class KnowledgeSearchResult(BaseModel):
    """Result model for knowledge base search"""
    id: str
    title: str
    content: str
    category: str
    similarity_score: float
    metadata: Dict[str, Any] = {}

class TrustdeskBase(BaseModel):
    """Base model for Trustdesk - define your models here"""
    pass
