from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enums for consistent categorization
class ConversationChannel(str, Enum):
    CALL_TRANSCRIPT = "call_transcript"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SMS = "sms"
    CHAT = "chat"

class LeadIntent(str, Enum):
    READY_TO_BOOK = "ready_to_book"
    NEEDS_MORE_INFO = "needs_more_info"
    PRICE_SENSITIVE = "price_sensitive"
    COMPARING_OPTIONS = "comparing_options"
    NOT_INTERESTED = "not_interested"
    SCHEDULING_CONFLICT = "scheduling_conflict"
    TECHNICAL_QUESTIONS = "technical_questions"
    JOB_SUPPORT_CONCERNS = "job_support_concerns"

class ActionType(str, Enum):
    SEND_FOLLOW_UP = "send_follow_up"
    SCHEDULE_NUDGE = "schedule_nudge"
    UPDATE_CRM = "update_crm"
    SEND_DEMO = "send_demo"
    PRICE_DISCUSSION = "price_discussion"
    COMPETITOR_COMPARISON = "competitor_comparison"
    BOOK_MEETING = "book_meeting"
    SEND_RESOURCES = "send_resources"
    ESCALATE_TO_MANAGER = "escalate_to_manager"

class UrgencyLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# Input Models
class ConversationInput(BaseModel):
    """Request model for a new conversation to be analyzed"""
    lead_id: str = Field(..., description="Unique identifier for the lead")
    channel: ConversationChannel = Field(..., description="Communication channel used")
    conversation_text: str = Field(..., description="Full conversation content")
    rep_id: str = Field(..., description="Sales representative ID")
    timestamp: Optional[datetime] = Field(default=None, description="When conversation occurred")
    lead_context: Optional[Dict[str, Any]] = Field(default=None, description="Additional lead context")

class ConversationBatch(BaseModel):
    """Request model for batch conversation analysis"""
    conversations: List[ConversationInput] = Field(..., description="List of conversations to analyze")
    rep_id: str = Field(..., description="Sales representative ID")

# Analysis Response Models
class SentimentScore(BaseModel):
    """Sentiment analysis results"""
    overall_sentiment: float = Field(..., ge=-1, le=1, description="Overall sentiment score (-1 to 1)")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in sentiment analysis")
    emotional_indicators: List[str] = Field(default=[], description="Detected emotional indicators")

class ObjectionAnalysis(BaseModel):
    """Detailed objection analysis"""
    objection_text: str = Field(..., description="The actual objection raised")
    objection_category: str = Field(..., description="Category of objection")
    severity: UrgencyLevel = Field(..., description="How critical this objection is")
    suggested_response: str = Field(..., description="Recommended response to objection")

class ConversationAnalysis(BaseModel):
    """Enhanced response model for analyzed conversation with comprehensive AI insights"""
    lead_id: str = Field(..., description="Lead identifier")
    summary: str = Field(..., description="Concise conversation summary")
    detailed_summary: str = Field(..., description="Detailed conversation analysis")
    detected_intent: LeadIntent = Field(..., description="Primary intent detected")
    intent_confidence: float = Field(..., ge=0, le=1, description="Confidence in intent detection")
    objections: List[ObjectionAnalysis] = Field(default=[], description="Detailed objection analysis")
    sentiment_analysis: SentimentScore = Field(..., description="Sentiment analysis results")
    key_topics: List[str] = Field(default=[], description="Main topics discussed")
    next_steps: List[str] = Field(..., description="Immediate next steps")
    recommended_follow_up_time: int = Field(..., description="Hours until follow-up")
    conversion_probability: float = Field(..., ge=0, le=1, description="Likelihood of conversion")
    urgency_level: UrgencyLevel = Field(..., description="Overall urgency level")
    personalization_notes: str = Field(..., description="Notes for personalizing future interactions")

# Action Planning Models
class NextBestAction(BaseModel):
    """Enhanced model for a single item in the daily action list"""
    lead_id: str = Field(..., description="Lead identifier")
    action_type: ActionType = Field(..., description="Type of action to take")
    suggested_message: str = Field(..., description="Personalized message or action")
    reason: str = Field(..., description="Justification for this action")
    priority_score: float = Field(..., ge=0, le=100, description="Priority score (0-100)")
    urgency_level: UrgencyLevel = Field(..., description="Action urgency")
    estimated_time_minutes: int = Field(..., description="Estimated time to complete action")
    expected_outcome: str = Field(..., description="Expected result of this action")
    follow_up_reminder: Optional[datetime] = Field(default=None, description="When to follow up")
    tags: List[str] = Field(default=[], description="Action tags for categorization")

class DailyActionsRequest(BaseModel):
    """Request model for getting daily actions for a sales rep"""
    rep_id: str = Field(..., description="Sales representative ID")
    include_low_priority: bool = Field(default=False, description="Include low priority actions")
    max_actions: int = Field(default=10, description="Maximum number of actions to return")
    focus_area: Optional[str] = Field(default=None, description="Specific focus area")

class DailyActionsSummary(BaseModel):
    """Summary of daily actions with metrics"""
    total_actions: int = Field(..., description="Total number of actions")
    high_priority_count: int = Field(..., description="Number of high priority actions")
    estimated_total_time: int = Field(..., description="Total estimated time in minutes")
    conversion_opportunities: int = Field(..., description="Number of high-conversion leads")
    actions: List[NextBestAction] = Field(..., description="Prioritized list of actions")

# Pipeline Analytics Models
class PipelineMetrics(BaseModel):
    """Pipeline performance metrics"""
    rep_id: str = Field(..., description="Sales representative ID")
    total_conversations: int = Field(..., description="Total conversations this period")
    meeting_booking_rate: float = Field(..., ge=0, le=1, description="Rate of meetings booked")
    no_show_rate: float = Field(..., ge=0, le=1, description="Rate of meeting no-shows")
    conversion_rate: float = Field(..., ge=0, le=1, description="Overall conversion rate")
    average_response_time: float = Field(..., description="Average response time in hours")
    objection_resolution_rate: float = Field(..., ge=0, le=1, description="Rate of objections resolved")

class ConversationInsights(BaseModel):
    """Insights from conversation analysis for coaching"""
    rep_id: str = Field(..., description="Sales representative ID")
    strengths: List[str] = Field(..., description="Rep's conversation strengths")
    improvement_areas: List[str] = Field(..., description="Areas needing improvement")
    suggested_training: List[str] = Field(..., description="Recommended training topics")
    best_performing_strategies: List[str] = Field(..., description="Most effective strategies used")

# Legacy compatibility models (for integration with existing systems)
class LegacyConversationInput(BaseModel):
    """Legacy format for backward compatibility"""
    lead_id: str
    channel: str
    conversation_text: str

class LegacyConversationAnalysis(BaseModel):
    """Legacy format for backward compatibility"""
    summary: str
    detected_intent: str
    objections: List[str]
    suggested_next_steps: List[str]

# RAG-Enhanced Models
class RAGConversationInput(BaseModel):
    """Enhanced conversation input for RAG analysis"""
    lead_id: str = Field(..., description="Unique identifier for the lead")
    channel: ConversationChannel = Field(..., description="Communication channel used")
    conversation_text: str = Field(..., description="Full conversation content")
    rep_id: str = Field(..., description="Sales representative ID")
    timestamp: Optional[datetime] = Field(default=None, description="When conversation occurred")
    lead_context: Optional[Dict[str, Any]] = Field(default=None, description="Additional lead context")
    use_rag: bool = Field(default=True, description="Whether to use RAG for enhanced analysis")
    knowledge_categories: Optional[List[str]] = Field(default=None, description="Specific knowledge categories to focus on")

class KnowledgeReference(BaseModel):
    """Reference to knowledge used in analysis"""
    doc_id: str = Field(..., description="Knowledge document ID")
    title: str = Field(..., description="Document title")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score")
    doc_type: str = Field(..., description="Type of knowledge document")
    category: str = Field(..., description="Knowledge category")

class RAGConversationAnalysis(BaseModel):
    """Enhanced conversation analysis with RAG knowledge integration"""
    lead_id: str = Field(..., description="Lead identifier")
    summary: str = Field(..., description="Concise conversation summary")
    detailed_summary: str = Field(..., description="Detailed conversation analysis")
    detected_intent: LeadIntent = Field(..., description="Primary intent detected")
    intent_confidence: float = Field(..., ge=0, le=1, description="Confidence in intent detection")
    objections: List[ObjectionAnalysis] = Field(default=[], description="Detailed objection analysis")
    sentiment_analysis: SentimentScore = Field(..., description="Sentiment analysis results")
    key_topics: List[str] = Field(default=[], description="Main topics discussed")
    next_steps: List[str] = Field(..., description="Enhanced next steps with knowledge")
    recommended_follow_up_time: int = Field(..., description="Hours until follow-up")
    conversion_probability: float = Field(..., ge=0, le=1, description="Likelihood of conversion")
    urgency_level: UrgencyLevel = Field(..., description="Overall urgency level")
    personalization_notes: str = Field(..., description="Enhanced personalization with knowledge insights")
    
    # RAG-specific fields
    knowledge_used: List[KnowledgeReference] = Field(default=[], description="Knowledge documents referenced")
    rag_enhanced: bool = Field(default=False, description="Whether RAG enhancement was applied")
    knowledge_confidence: float = Field(default=0.0, ge=0, le=1, description="Confidence in knowledge application")

class SalesKnowledgeInput(BaseModel):
    """Input for adding sales knowledge documents"""
    title: str = Field(..., description="Knowledge document title")
    content: str = Field(..., description="Document content")
    doc_type: str = Field(..., description="Document type")
    category: str = Field(..., description="Document category")
    tags: List[str] = Field(default=[], description="Document tags")
    priority: int = Field(default=5, ge=1, le=10, description="Priority level (1-10)")

class KnowledgeQuery(BaseModel):
    """Query for knowledge retrieval"""
    query: str = Field(..., description="Search query")
    doc_types: Optional[List[str]] = Field(default=None, description="Filter by document types")
    categories: Optional[List[str]] = Field(default=None, description="Filter by categories")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")
    min_similarity: float = Field(default=0.3, ge=0, le=1, description="Minimum similarity threshold")

class KnowledgeSearchResult(BaseModel):
    """Result from knowledge search"""
    doc_id: str = Field(..., description="Document identifier")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    doc_type: str = Field(..., description="Document type")
    category: str = Field(..., description="Document category")
    tags: List[str] = Field(..., description="Document tags")
    similarity_score: float = Field(..., ge=0, le=1, description="Similarity to query")
    relevance_reason: str = Field(..., description="Why this document is relevant")
    priority: int = Field(..., description="Document priority")

class KnowledgeStats(BaseModel):
    """Knowledge base statistics"""
    total_documents: int = Field(..., description="Total number of documents")
    document_types: Dict[str, int] = Field(..., description="Count by document type")
    categories: Dict[str, int] = Field(..., description="Count by category")
    last_updated: str = Field(..., description="Last update timestamp")
