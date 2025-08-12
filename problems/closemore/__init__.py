"""
CloseMore - AI-Powered Sales Conversation Analysis & Action Planning System

A comprehensive sales productivity solution that addresses the core challenges:
- 46% of opportunities have no clear next step within 24 hours  
- 24-28% no-show rate for first meetings
- 2-3x win rate variation by rep, even on similar leads

This system provides:
1. Real-time conversation analysis using Amazon Bedrock Claude-v2
2. Intelligent daily action planning with priority scoring
3. Performance analytics and coaching insights
4. Follow-up management and urgency detection

Expected Business Impact:
- +15% meeting booking rate
- -20% no-show rate reduction  
- +10-20% win rate improvement
- Standardized rep performance within 45 days

Technical Architecture:
- Amazon Bedrock for AI analysis (Claude-v2 + Titan Embeddings)
- Conversation management with local storage
- Comprehensive API with FastAPI
- Legacy compatibility for existing integrations
- Batch processing capabilities for scale

Author: AI Assistant
Created: 2025
"""

from .models import (
    # Core models
    ConversationInput,
    ConversationAnalysis,
    NextBestAction,
    DailyActionsRequest,
    DailyActionsSummary,
    
    # Enhanced models  
    ConversationBatch,
    SentimentScore,
    ObjectionAnalysis,
    PipelineMetrics,
    ConversationInsights,
    
    # RAG models
    RAGConversationInput,
    RAGConversationAnalysis,
    SalesKnowledgeInput,
    KnowledgeQuery,
    KnowledgeSearchResult,
    KnowledgeStats,
    KnowledgeReference,
    
    # Enums
    ConversationChannel,
    LeadIntent,
    ActionType,
    UrgencyLevel,
    
    # Legacy compatibility
    LegacyConversationInput,
    LegacyConversationAnalysis
)

from .service import ClosemoreService
from .bedrock_service import ClosemoreBedrockService  
from .conversation_manager import ConversationManager, MockDataGenerator
from .rag_service import ClosemoreRAGService
from .sales_knowledge import SalesKnowledgeManager
from .embeddings import ClosemoreEmbeddingService
from .routes import router

# Package metadata
__version__ = "1.0.0"
__author__ = "AI Assistant"
__description__ = "AI-Powered Sales Conversation Analysis & Action Planning System"

# Main service instance for easy importing
closemore_service = ClosemoreService()

# Export key components
__all__ = [
    # Models
    "ConversationInput",
    "ConversationAnalysis", 
    "NextBestAction",
    "DailyActionsRequest",
    "DailyActionsSummary",
    "ConversationBatch",
    "SentimentScore",
    "ObjectionAnalysis",
    "PipelineMetrics",
    "ConversationInsights",
    
    # RAG Models
    "RAGConversationInput",
    "RAGConversationAnalysis",
    "SalesKnowledgeInput",
    "KnowledgeQuery",
    "KnowledgeSearchResult", 
    "KnowledgeStats",
    "KnowledgeReference",
    
    # Enums
    "ConversationChannel",
    "LeadIntent", 
    "ActionType",
    "UrgencyLevel",
    
    # Services
    "ClosemoreService",
    "ClosemoreBedrockService",
    "ConversationManager",
    "MockDataGenerator",
    "ClosemoreRAGService",
    "SalesKnowledgeManager",
    "ClosemoreEmbeddingService",
    
    # Main instances
    "closemore_service",
    "router",
    
    # Legacy compatibility
    "LegacyConversationInput",
    "LegacyConversationAnalysis"
]

# System capabilities summary
SYSTEM_CAPABILITIES = {
    "conversation_analysis": {
        "ai_engine": "Amazon Bedrock Claude-v2",
        "features": [
            "Intent detection with confidence scoring",
            "Sentiment analysis and emotional indicators",
            "Objection categorization and response suggestions", 
            "Conversion probability estimation",
            "Personalized next steps and timing"
        ]
    },
    "rag_enhancement": {
        "ai_engine": "Amazon Bedrock Claude-v2 + Titan Embeddings",
        "features": [
            "Sales knowledge retrieval with vector search",
            "Objection handling scripts from knowledge base",
            "Contextual product information retrieval",
            "Competitive comparison data access",
            "Success stories and case study recommendations",
            "Proven sales strategy suggestions"
        ]
    },
    "knowledge_management": {
        "storage": "Local JSON with vector embeddings",
        "features": [
            "Sales playbook and script management",
            "Objection handling knowledge base",
            "Product information repository", 
            "Competitive comparison database",
            "Case studies and success stories",
            "Semantic search with similarity scoring"
        ]
    },
    "action_planning": {
        "ai_engine": "Amazon Bedrock Claude-v2", 
        "features": [
            "Priority-based action ranking (0-100 scale)",
            "Time estimation for task planning",
            "Personalized messaging suggestions",
            "Follow-up timing optimization",
            "Focus area filtering and categorization"
        ]
    },
    "analytics": {
        "features": [
            "Rep performance metrics and benchmarking",
            "Conversation insights for coaching",
            "Pipeline velocity and conversion tracking",
            "High-priority lead identification",
            "Overdue follow-up management"
        ]
    },
    "integration": {
        "features": [
            "RESTful API with comprehensive endpoints",
            "Legacy compatibility for existing systems", 
            "Batch processing for historical data",
            "Local storage with JSON persistence",
            "Mock data generation for development"
        ]
    }
}

# Business impact targets
BUSINESS_TARGETS = {
    "meeting_booking_rate": "+15%",
    "no_show_reduction": "-20%", 
    "win_rate_increase": "+10-20%",
    "timeline": "45 days",
    "rep_performance_standardization": "Within 2x variance"
}

def get_system_info() -> dict:
    """Get comprehensive system information"""
    return {
        "system": "CloseMore - Sales Productivity AI",
        "version": __version__,
        "description": __description__,
        "capabilities": SYSTEM_CAPABILITIES,
        "business_targets": BUSINESS_TARGETS,
        "status": "Operational",
        "components": {
            "ai_analysis": "Amazon Bedrock Claude-v2",
            "conversation_storage": "Local JSON with management layer",
            "api_framework": "FastAPI with comprehensive endpoints", 
            "compatibility": "Legacy API support included"
        }
    }
