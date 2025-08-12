from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from .models import (
    ConversationInput, ConversationAnalysis, NextBestAction, 
    DailyActionsRequest, DailyActionsSummary, ConversationBatch,
    PipelineMetrics, ConversationInsights, LegacyConversationInput,
    LegacyConversationAnalysis, RAGConversationInput, RAGConversationAnalysis,
    SalesKnowledgeInput, KnowledgeQuery, KnowledgeSearchResult, KnowledgeStats
)
from .service import ClosemoreService

router = APIRouter()

# Initialize service
closemore_service = ClosemoreService()

@router.get("/")
async def closemore_home():
    """CloseMore - AI-Powered Sales Conversation Analysis & Action Planning System"""
    return {
        "problem": "CloseMore - Sales Conversation Analysis & Daily Action Planning",
        "description": "AI-powered sales productivity system using Amazon Bedrock for conversation analysis and intelligent action prioritization",
        "status": "Active - Full AI Analysis Suite Ready",
        "business_impact": {
            "target_improvements": {
                "meeting_booking_rate": "+15%",
                "no_show_reduction": "-20%", 
                "win_rate_increase": "+10-20%",
                "timeline": "45 days"
            },
            "key_metrics": [
                "46% of opportunities have no clear next step (BEFORE)",
                "24-28% no-show rate for first meetings (BEFORE)",
                "2-3x win rate variation by rep (BEFORE)"
            ]
        },
        "ai_capabilities": [
            "Amazon Bedrock Claude-v2 conversation analysis",
            "RAG-enhanced insights with sales knowledge retrieval",
            "Sentiment analysis and objection detection",
            "Intent classification and urgency scoring",
            "Personalized action recommendations with knowledge context",
            "Intelligent follow-up timing with proven strategies",
            "Rep performance analytics and coaching insights"
        ],
        "features": [
            "Real-time conversation analysis with comprehensive insights",
            "RAG-powered knowledge retrieval for enhanced recommendations",
            "Sales knowledge base management for playbooks and scripts",
            "Daily prioritized action planning for sales reps",
            "Pipeline performance metrics and analytics", 
            "Conversation coaching insights and training recommendations",
            "High-priority lead identification and follow-up management",
            "Legacy API compatibility for existing integrations"
        ],
        "endpoints": {
            "Core Analysis": {
                "/analyze": "POST - Analyze single sales conversation with AI insights",
                "/analyze-rag": "POST - RAG-enhanced conversation analysis with knowledge",
                "/analyze-batch": "POST - Analyze multiple conversations efficiently",
                "/analyze-legacy": "POST - Legacy compatibility endpoint"
            },
            "Knowledge Management": {
                "/knowledge/add": "POST - Add sales knowledge documents",
                "/knowledge/search": "POST - Search sales knowledge base",
                "/knowledge/stats": "GET - Get knowledge base statistics"
            },
            "Action Planning": {
                "/daily-actions": "POST - Generate prioritized daily action list",
                "/high-priority-leads": "GET - Get high-priority leads needing attention",
                "/pending-follow-ups": "GET - Get overdue follow-ups by rep"
            },
            "Analytics & Insights": {
                "/rep-metrics": "GET - Get comprehensive rep performance metrics",
                "/conversation-insights": "GET - Get coaching insights for rep improvement",
                "/lead-history": "GET - Get complete conversation history for a lead"
            }
        }
    }

# CORE CONVERSATION ANALYSIS ENDPOINTS

@router.post("/analyze", response_model=ConversationAnalysis)
async def analyze_conversation(conversation_input: ConversationInput):
    """
    Analyze a sales conversation with comprehensive AI insights using Amazon Bedrock
    
    Features:
    - Deep conversation analysis with sentiment scoring
    - Intent detection and confidence measurement  
    - Detailed objection analysis with response suggestions
    - Personalized next steps and follow-up timing
    - Conversion probability estimation
    
    Args:
        conversation_input: ConversationInput with lead_id, rep_id, channel, and conversation text
        
    Returns:
        ConversationAnalysis with comprehensive AI insights and recommendations
    """
    try:
        analysis = await closemore_service.analyze_conversation(conversation_input)
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing conversation: {str(e)}"
        )

@router.post("/analyze-rag", response_model=RAGConversationAnalysis)
async def analyze_conversation_with_rag(conversation_input: RAGConversationInput):
    """
    Analyze a sales conversation with RAG-enhanced insights using sales knowledge retrieval
    
    Features:
    - All standard conversation analysis capabilities
    - Enhanced objection responses from knowledge base
    - Contextual next steps with proven sales strategies
    - Relevant case studies and success stories
    - Competitor comparison information when needed
    - Personalized recommendations based on similar scenarios
    
    Args:
        conversation_input: RAGConversationInput with conversation data and RAG preferences
        
    Returns:
        RAGConversationAnalysis with knowledge-enhanced insights and recommendations
    """
    try:
        rag_analysis = await closemore_service.analyze_conversation_with_rag(conversation_input)
        return rag_analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in RAG conversation analysis: {str(e)}"
        )

@router.post("/analyze-batch", response_model=List[ConversationAnalysis])
async def analyze_conversation_batch(batch_input: ConversationBatch):
    """
    Analyze multiple sales conversations in batch for efficiency
    
    Useful for:
    - Processing historical conversation data
    - Bulk analysis for new rep onboarding
    - Daily batch processing of recorded calls
    
    Args:
        batch_input: ConversationBatch with list of conversations and rep_id
        
    Returns:
        List of ConversationAnalysis results for each conversation
    """
    try:
        analyses = await closemore_service.analyze_conversation_batch(batch_input.conversations)
        return analyses
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in batch analysis: {str(e)}"
        )

@router.post("/analyze-legacy", response_model=LegacyConversationAnalysis)
async def analyze_conversation_legacy(conversation_input: LegacyConversationInput):
    """
    Legacy compatibility endpoint for existing integrations
    
    Maintains backward compatibility with simpler input/output format
    while leveraging new AI analysis capabilities internally
    
    Args:
        conversation_input: LegacyConversationInput with basic conversation data
        
    Returns:
        LegacyConversationAnalysis in original format
    """
    try:
        analysis = await closemore_service.analyze_legacy_conversation(conversation_input)
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in legacy analysis: {str(e)}"
        )

# KNOWLEDGE MANAGEMENT ENDPOINTS

@router.post("/knowledge/add")
async def add_sales_knowledge(knowledge_input: SalesKnowledgeInput):
    """
    Add new sales knowledge document to the knowledge base
    
    Enables the system to learn from:
    - New objection handling scripts
    - Updated product information
    - Successful case studies and stories
    - Competitive comparison data
    - Sales playbooks and best practices
    
    Args:
        knowledge_input: SalesKnowledgeInput with document details
        
    Returns:
        Document ID and confirmation of successful addition
    """
    try:
        doc_id = closemore_service.add_sales_knowledge(knowledge_input)
        return {
            "success": True,
            "doc_id": doc_id,
            "message": f"Sales knowledge '{knowledge_input.title}' added successfully",
            "doc_type": knowledge_input.doc_type,
            "category": knowledge_input.category
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error adding sales knowledge: {str(e)}"
        )

@router.post("/knowledge/search", response_model=List[KnowledgeSearchResult])
async def search_sales_knowledge(query: KnowledgeQuery):
    """
    Search the sales knowledge base for relevant information
    
    Useful for:
    - Finding objection handling scripts for specific concerns
    - Retrieving product information for prospect questions
    - Getting competitive comparison data
    - Accessing relevant case studies and success stories
    - Finding proven sales strategies for specific scenarios
    
    Args:
        query: KnowledgeQuery with search parameters and filters
        
    Returns:
        List of relevant knowledge documents with similarity scores
    """
    try:
        search_results = closemore_service.search_sales_knowledge(query)
        return search_results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching sales knowledge: {str(e)}"
        )

@router.get("/knowledge/stats", response_model=KnowledgeStats)
async def get_knowledge_base_stats():
    """
    Get comprehensive statistics about the sales knowledge base
    
    Provides insights on:
    - Total number of knowledge documents
    - Distribution by document types (playbooks, scripts, case studies)
    - Category breakdown (objections, product info, competitors)
    - Knowledge base growth and update patterns
    
    Returns:
        KnowledgeStats with comprehensive knowledge base metrics
    """
    try:
        stats = closemore_service.get_knowledge_base_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving knowledge stats: {str(e)}"
        )

# DAILY ACTION PLANNING ENDPOINTS

@router.post("/daily-actions", response_model=DailyActionsSummary)
async def get_daily_actions(request: DailyActionsRequest):
    """
    Generate a prioritized daily action list for a sales rep with intelligent recommendations
    
    Features:
    - AI-powered action prioritization based on conversion probability
    - Personalized messages and timing recommendations
    - Estimated time requirements for task planning
    - Focus area filtering and priority-based sorting
    
    Args:
        request: DailyActionsRequest with rep_id and filtering options
        
    Returns:
        DailyActionsSummary with prioritized actions and productivity metrics
    """
    try:
        actions_summary = await closemore_service.get_daily_actions(
            rep_id=request.rep_id,
            include_low_priority=request.include_low_priority,
            max_actions=request.max_actions,
            focus_area=request.focus_area
        )
        return actions_summary
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating daily actions: {str(e)}"
        )

@router.get("/high-priority-leads")
async def get_high_priority_leads(
    rep_id: str = Query(..., description="Sales representative ID")
):
    """
    Get high-priority leads requiring immediate attention
    
    Identifies leads with:
    - High conversion probability (>70%)
    - High urgency level
    - Recent positive engagement
    - Time-sensitive opportunities
    
    Args:
        rep_id: Sales representative ID
        
    Returns:
        List of high-priority leads with context and recommendations
    """
    try:
        high_priority_leads = closemore_service.get_high_priority_leads(rep_id)
        return {
            "rep_id": rep_id,
            "high_priority_count": len(high_priority_leads),
            "leads": high_priority_leads,
            "recommendation": "Focus on these leads for maximum conversion impact"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving high priority leads: {str(e)}"
        )

@router.get("/pending-follow-ups")
async def get_pending_follow_ups(
    rep_id: str = Query(..., description="Sales representative ID")
):
    """
    Get leads that need follow-up based on AI-recommended timing
    
    Identifies:
    - Overdue follow-ups based on conversation analysis
    - Leads approaching optimal follow-up windows
    - Missed meeting follow-ups requiring immediate attention
    
    Args:
        rep_id: Sales representative ID
        
    Returns:
        List of pending follow-ups sorted by urgency and overdue time
    """
    try:
        pending_follow_ups = closemore_service.get_pending_follow_ups(rep_id)
        return {
            "rep_id": rep_id,
            "pending_count": len(pending_follow_ups),
            "overdue_count": len([f for f in pending_follow_ups if f.get('hours_overdue', 0) > 0]),
            "follow_ups": pending_follow_ups,
            "recommendation": "Prioritize overdue follow-ups to maintain engagement momentum"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving pending follow-ups: {str(e)}"
        )

# ANALYTICS AND INSIGHTS ENDPOINTS

@router.get("/rep-metrics", response_model=PipelineMetrics)
async def get_rep_performance_metrics(
    rep_id: str = Query(..., description="Sales representative ID")
):
    """
    Get comprehensive performance metrics for a sales rep
    
    Provides insights on:
    - Conversation volume and quality metrics
    - Meeting booking and no-show rates
    - Conversion rates and pipeline velocity
    - Response time and objection resolution effectiveness
    
    Args:
        rep_id: Sales representative ID
        
    Returns:
        PipelineMetrics with comprehensive performance data for coaching and improvement
    """
    try:
        metrics = closemore_service.get_rep_performance_metrics(rep_id)
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving rep metrics: {str(e)}"
        )

@router.get("/conversation-insights", response_model=ConversationInsights)
async def get_conversation_insights(
    rep_id: str = Query(..., description="Sales representative ID")
):
    """
    Get AI-powered coaching insights for sales rep improvement
    
    Analyzes conversation patterns to identify:
    - Rep strengths and successful strategies
    - Areas needing improvement and skill gaps
    - Recommended training topics and focus areas
    - Best-performing conversation techniques
    
    Args:
        rep_id: Sales representative ID
        
    Returns:
        ConversationInsights with actionable coaching recommendations
    """
    try:
        insights = closemore_service.get_conversation_insights(rep_id)
        return insights
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating conversation insights: {str(e)}"
        )

@router.get("/lead-history")
async def get_lead_conversation_history(
    lead_id: str = Query(..., description="Lead identifier")
):
    """
    Get complete conversation history and progression for a specific lead
    
    Provides:
    - Chronological conversation timeline
    - Evolution of lead intent and sentiment
    - Historical objections and responses
    - Conversion progression tracking
    
    Args:
        lead_id: Lead identifier
        
    Returns:
        Complete conversation history with analysis progression
    """
    try:
        history = closemore_service.get_lead_conversation_history(lead_id)
        return {
            "lead_id": lead_id,
            "total_conversations": len(history),
            "conversation_span_days": (
                (max(h['timestamp'] for h in history) - min(h['timestamp'] for h in history)).days 
                if len(history) > 1 else 0
            ),
            "conversations": history,
            "progression_summary": "Detailed conversation timeline with AI analysis evolution"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving lead history: {str(e)}"
        )
