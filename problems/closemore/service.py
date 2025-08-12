"""
CloseMore Service - Comprehensive sales conversation analysis and action planning
Integrates Amazon Bedrock AI, conversation management, and intelligent action planning
"""

import asyncio
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .models import (
    ConversationInput, ConversationAnalysis, NextBestAction, 
    DailyActionsRequest, DailyActionsSummary, PipelineMetrics,
    ConversationInsights, LegacyConversationInput, LegacyConversationAnalysis,
    RAGConversationInput, RAGConversationAnalysis, SalesKnowledgeInput,
    KnowledgeQuery, KnowledgeSearchResult, KnowledgeStats, KnowledgeReference
)
from .bedrock_service import ClosemoreBedrockService
from .conversation_manager import ConversationManager, MockDataGenerator
from .rag_service import ClosemoreRAGService
from .sales_knowledge import SalesKnowledgeManager

class ClosemoreService:
    """
    Main service class for CloseMore sales conversation analysis and action planning
    
    Provides comprehensive AI-powered features:
    - Conversation analysis with Amazon Bedrock
    - Intelligent action planning
    - Pipeline analytics and insights
    - Rep performance tracking
    """
    
    def __init__(self):
        """Initialize CloseMore service with all components"""
        self.bedrock_service = ClosemoreBedrockService()
        self.conversation_manager = ConversationManager()
        self.mock_generator = MockDataGenerator()
        self.rag_service = ClosemoreRAGService()
        self.knowledge_manager = SalesKnowledgeManager()
        
        print("ClosemoreService initialized successfully with RAG capabilities")
    
    # CORE CONVERSATION ANALYSIS
    
    async def analyze_conversation(self, conversation_input: ConversationInput) -> ConversationAnalysis:
        """
        Analyze a sales conversation with comprehensive AI insights
        
        Args:
            conversation_input: The conversation data to analyze
            
        Returns:
            ConversationAnalysis with detailed insights and recommendations
        """
        try:
            # Analyze with Bedrock AI
            analysis = await self.bedrock_service.analyze_conversation_with_bedrock(conversation_input)
            
            # Store conversation and analysis
            conversation_id = self.conversation_manager.store_conversation_analysis(
                conversation_input, analysis
            )
            
            print(f"Conversation {conversation_id} analyzed and stored successfully")
            return analysis
            
        except Exception as e:
            print(f"Error in conversation analysis: {e}")
            
            # Fallback analysis
            return ConversationAnalysis(
                lead_id=conversation_input.lead_id,
                summary="Analysis service temporarily unavailable",
                detailed_summary="Manual review recommended for this conversation",
                detected_intent="needs_more_info",
                intent_confidence=0.5,
                objections=[],
                sentiment_analysis={
                    "overall_sentiment": 0.0,
                    "confidence": 0.0,
                    "emotional_indicators": []
                },
                key_topics=[],
                next_steps=["Manual review required", "Follow up within 24 hours"],
                recommended_follow_up_time=24,
                conversion_probability=0.5,
                urgency_level="medium",
                personalization_notes=f"Service error: {str(e)}"
            )
    
    async def analyze_conversation_with_rag(self, conversation_input: RAGConversationInput) -> RAGConversationAnalysis:
        """
        Analyze conversation with RAG-enhanced insights using sales knowledge
        
        Args:
            conversation_input: RAG conversation input with knowledge preferences
            
        Returns:
            RAGConversationAnalysis with knowledge-enhanced recommendations
        """
        try:
            if conversation_input.use_rag:
                # Use RAG service for enhanced analysis
                base_conversation = ConversationInput(
                    lead_id=conversation_input.lead_id,
                    channel=conversation_input.channel,
                    conversation_text=conversation_input.conversation_text,
                    rep_id=conversation_input.rep_id,
                    timestamp=conversation_input.timestamp,
                    lead_context=conversation_input.lead_context
                )
                
                # Get RAG-enhanced analysis
                rag_analysis = await self.rag_service.analyze_conversation_with_rag(base_conversation)
                
                # Convert to RAG format with knowledge references
                rag_enhanced_analysis = self._convert_to_rag_analysis(rag_analysis, True)
                
                # Store conversation and analysis
                conversation_id = self.conversation_manager.store_conversation_analysis(
                    base_conversation, rag_analysis
                )
                
                print(f"RAG-enhanced conversation {conversation_id} analyzed successfully")
                return rag_enhanced_analysis
            else:
                # Use standard analysis
                base_conversation = ConversationInput(
                    lead_id=conversation_input.lead_id,
                    channel=conversation_input.channel,
                    conversation_text=conversation_input.conversation_text,
                    rep_id=conversation_input.rep_id,
                    timestamp=conversation_input.timestamp,
                    lead_context=conversation_input.lead_context
                )
                
                analysis = await self.analyze_conversation(base_conversation)
                return self._convert_to_rag_analysis(analysis, False)
                
        except Exception as e:
            print(f"Error in RAG conversation analysis: {e}")
            
            # Fallback to standard analysis
            base_conversation = ConversationInput(
                lead_id=conversation_input.lead_id,
                channel=conversation_input.channel,
                conversation_text=conversation_input.conversation_text,
                rep_id=conversation_input.rep_id,
                timestamp=conversation_input.timestamp or datetime.now(),
                lead_context=conversation_input.lead_context
            )
            
            fallback_analysis = await self.analyze_conversation(base_conversation)
            return self._convert_to_rag_analysis(fallback_analysis, False)
    
    async def analyze_conversation_batch(
        self, 
        conversations: List[ConversationInput]
    ) -> List[ConversationAnalysis]:
        """
        Analyze multiple conversations in batch for efficiency
        
        Args:
            conversations: List of conversations to analyze
            
        Returns:
            List of ConversationAnalysis results
        """
        tasks = [self.analyze_conversation(conv) for conv in conversations]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful analyses
        successful_results = [r for r in results if isinstance(r, ConversationAnalysis)]
        
        print(f"Batch analysis completed: {len(successful_results)}/{len(conversations)} successful")
        return successful_results
    
    # DAILY ACTION PLANNING
    
    async def get_daily_actions(
        self, 
        rep_id: str,
        include_low_priority: bool = False,
        max_actions: int = 10,
        focus_area: Optional[str] = None
    ) -> DailyActionsSummary:
        """
        Generate prioritized daily action list for a sales rep
        
        Args:
            rep_id: Sales representative ID
            include_low_priority: Whether to include low priority actions
            max_actions: Maximum number of actions to return
            focus_area: Specific focus area for actions
            
        Returns:
            DailyActionsSummary with prioritized actions and metrics
        """
        try:
            # Get recent conversations for the rep
            conversations_data = self.conversation_manager.get_conversations_for_rep(
                rep_id, days_back=7, limit=20
            )
            
            if not conversations_data:
                # Generate mock data for development/demo
                print(f"No conversation data found for rep {rep_id}, generating mock data")
                mock_conversations = self.mock_generator.generate_sample_conversations(rep_id, 5)
                
                # Analyze mock conversations
                for conv in mock_conversations:
                    await self.analyze_conversation(conv)
                
                # Reload conversation data
                conversations_data = self.conversation_manager.get_conversations_for_rep(
                    rep_id, days_back=7
                )
            
            # Generate actions with Bedrock AI
            actions_summary = await self.bedrock_service.generate_daily_actions_with_bedrock(
                rep_id, conversations_data, max_actions
            )
            
            # Filter by focus area if specified
            if focus_area:
                filtered_actions = [
                    action for action in actions_summary.actions 
                    if focus_area.lower() in [tag.lower() for tag in action.tags]
                ]
                actions_summary.actions = filtered_actions[:max_actions]
            
            # Filter out low priority if requested
            if not include_low_priority:
                filtered_actions = [
                    action for action in actions_summary.actions
                    if action.urgency_level != "low"
                ]
                actions_summary.actions = filtered_actions[:max_actions]
            
            return actions_summary
            
        except Exception as e:
            print(f"Error generating daily actions: {e}")
            
            # Return fallback actions
            return DailyActionsSummary(
                total_actions=1,
                high_priority_count=0,
                estimated_total_time=30,
                conversion_opportunities=0,
                actions=[
                    NextBestAction(
                        lead_id=f"fallback_{rep_id}",
                        action_type="update_crm",
                        suggested_message="Review recent conversations and update lead statuses",
                        reason=f"Service temporarily unavailable: {str(e)}",
                        priority_score=50,
                        urgency_level="medium",
                        estimated_time_minutes=30,
                        expected_outcome="Updated CRM data",
                        follow_up_reminder=None,
                        tags=["fallback", "manual"]
                    )
                ]
            )
    
    # ANALYTICS AND INSIGHTS
    
    def get_rep_performance_metrics(self, rep_id: str) -> PipelineMetrics:
        """
        Get comprehensive performance metrics for a sales rep
        
        Args:
            rep_id: Sales representative ID
            
        Returns:
            PipelineMetrics with performance data
        """
        try:
            # Get conversation data and analytics
            conversations = self.conversation_manager.get_conversations_for_rep(rep_id, days_back=30)
            analytics = self.conversation_manager.get_rep_analytics(rep_id)
            
            if not conversations:
                return PipelineMetrics(
                    rep_id=rep_id,
                    total_conversations=0,
                    meeting_booking_rate=0.0,
                    no_show_rate=0.0,
                    conversion_rate=0.0,
                    average_response_time=0.0,
                    objection_resolution_rate=0.0
                )
            
            # Calculate metrics from conversation data
            total_conversations = len(conversations)
            
            # Mock calculations (in real system, would integrate with CRM data)
            booking_rate = analytics.get('avg_conversion_probability', 0.5) * 0.8  # Estimate
            no_show_rate = max(0.1, 0.3 - (analytics.get('avg_sentiment', 0) * 0.2))  # Estimate
            conversion_rate = analytics.get('avg_conversion_probability', 0.5) * 0.6  # Estimate
            
            # Calculate average response time (mock)
            avg_response_time = 6.0  # hours - would calculate from actual data
            
            # Calculate objection resolution rate
            objection_resolution = min(0.9, 0.6 + (analytics.get('avg_sentiment', 0) * 0.3))
            
            return PipelineMetrics(
                rep_id=rep_id,
                total_conversations=total_conversations,
                meeting_booking_rate=booking_rate,
                no_show_rate=no_show_rate,
                conversion_rate=conversion_rate,
                average_response_time=avg_response_time,
                objection_resolution_rate=objection_resolution
            )
            
        except Exception as e:
            print(f"Error calculating rep metrics: {e}")
            return PipelineMetrics(
                rep_id=rep_id,
                total_conversations=0,
                meeting_booking_rate=0.0,
                no_show_rate=0.0,
                conversion_rate=0.0,
                average_response_time=0.0,
                objection_resolution_rate=0.0
            )
    
    def get_conversation_insights(self, rep_id: str) -> ConversationInsights:
        """
        Get coaching insights for a sales rep based on conversation analysis
        
        Args:
            rep_id: Sales representative ID
            
        Returns:
            ConversationInsights with coaching recommendations
        """
        try:
            analytics = self.conversation_manager.get_rep_analytics(rep_id)
            conversations = self.conversation_manager.get_conversations_for_rep(rep_id, days_back=14)
            
            # Analyze strengths and weaknesses
            strengths = []
            improvement_areas = []
            training_suggestions = []
            
            # Analyze intent distribution
            intent_dist = analytics.get('intent_distribution', {})
            
            if intent_dist.get('ready_to_book', 0) > intent_dist.get('not_interested', 0):
                strengths.append("Good at building interest and moving leads towards booking")
            
            if intent_dist.get('price_sensitive', 0) > len(conversations) * 0.3:
                improvement_areas.append("High number of price objections - work on value communication")
                training_suggestions.append("Value-based selling techniques")
            
            if analytics.get('avg_sentiment', 0) > 0.3:
                strengths.append("Maintains positive conversation tone")
            elif analytics.get('avg_sentiment', 0) < -0.1:
                improvement_areas.append("Conversation sentiment tends to be negative")
                training_suggestions.append("Positive communication and rapport building")
            
            # Analyze urgency patterns
            urgency_dist = analytics.get('urgency_distribution', {})
            if urgency_dist.get('high', 0) < urgency_dist.get('low', 0):
                improvement_areas.append("Low urgency creation - work on creating time-sensitive value")
                training_suggestions.append("Urgency and scarcity techniques")
            
            # Best performing strategies (mock analysis)
            best_strategies = [
                "Asking discovery questions about career goals",
                "Sharing success stories and testimonials",
                "Addressing concerns directly and thoroughly"
            ]
            
            return ConversationInsights(
                rep_id=rep_id,
                strengths=strengths if strengths else ["Maintains professional communication"],
                improvement_areas=improvement_areas if improvement_areas else ["Continue current approach"],
                suggested_training=training_suggestions if training_suggestions else ["Advanced objection handling"],
                best_performing_strategies=best_strategies
            )
            
        except Exception as e:
            print(f"Error generating conversation insights: {e}")
            return ConversationInsights(
                rep_id=rep_id,
                strengths=["Manual analysis required"],
                improvement_areas=["Data collection needed"],
                suggested_training=["System training"],
                best_performing_strategies=["Standard sales process"]
            )
    
    # KNOWLEDGE MANAGEMENT
    
    def add_sales_knowledge(self, knowledge_input: SalesKnowledgeInput) -> str:
        """
        Add new sales knowledge document to the knowledge base
        
        Args:
            knowledge_input: Sales knowledge document to add
            
        Returns:
            Document ID of the added knowledge
        """
        try:
            doc_id = self.knowledge_manager.add_document(
                title=knowledge_input.title,
                content=knowledge_input.content,
                doc_type=knowledge_input.doc_type,
                category=knowledge_input.category,
                tags=knowledge_input.tags,
                priority=knowledge_input.priority
            )
            
            print(f"Sales knowledge added successfully: {doc_id}")
            return doc_id
            
        except Exception as e:
            print(f"Error adding sales knowledge: {e}")
            raise Exception(f"Failed to add knowledge: {str(e)}")
    
    def search_sales_knowledge(self, query: KnowledgeQuery) -> List[KnowledgeSearchResult]:
        """
        Search sales knowledge base for relevant information
        
        Args:
            query: Knowledge query with search parameters
            
        Returns:
            List of relevant knowledge search results
        """
        try:
            # Retrieve knowledge using the manager
            retrieval_results = self.knowledge_manager.retrieve_relevant_knowledge(
                query=query.query,
                doc_types=query.doc_types,
                categories=query.categories,
                top_k=query.top_k,
                min_similarity=query.min_similarity
            )
            
            # Convert to search result format
            search_results = []
            for result in retrieval_results:
                doc = result.document
                search_result = KnowledgeSearchResult(
                    doc_id=doc.doc_id,
                    title=doc.title,
                    content=doc.content,
                    doc_type=doc.doc_type,
                    category=doc.category,
                    tags=doc.tags,
                    similarity_score=result.similarity_score,
                    relevance_reason=result.relevance_reason,
                    priority=doc.priority
                )
                search_results.append(search_result)
            
            return search_results
            
        except Exception as e:
            print(f"Error searching sales knowledge: {e}")
            return []
    
    def get_knowledge_base_stats(self) -> KnowledgeStats:
        """Get statistics about the sales knowledge base"""
        try:
            stats_data = self.knowledge_manager.get_knowledge_stats()
            return KnowledgeStats(**stats_data)
        except Exception as e:
            print(f"Error getting knowledge stats: {e}")
            return KnowledgeStats(
                total_documents=0,
                document_types={},
                categories={},
                last_updated=datetime.now().isoformat()
            )
    
    # UTILITY METHODS
    
    def _convert_to_rag_analysis(self, analysis: ConversationAnalysis, rag_enhanced: bool) -> RAGConversationAnalysis:
        """Convert standard analysis to RAG analysis format"""
        
        # Mock knowledge references for demonstration
        # In production, this would come from actual RAG processing
        knowledge_used = []
        knowledge_confidence = 0.0
        
        if rag_enhanced:
            knowledge_used = [
                KnowledgeReference(
                    doc_id="sales_demo_001",
                    title="Sample Sales Knowledge",
                    relevance_score=0.8,
                    doc_type="objection_script",
                    category="price_objections"
                )
            ]
            knowledge_confidence = 0.85
        
        return RAGConversationAnalysis(
            lead_id=analysis.lead_id,
            summary=analysis.summary,
            detailed_summary=analysis.detailed_summary,
            detected_intent=analysis.detected_intent,
            intent_confidence=analysis.intent_confidence,
            objections=analysis.objections,
            sentiment_analysis=analysis.sentiment_analysis,
            key_topics=analysis.key_topics,
            next_steps=analysis.next_steps,
            recommended_follow_up_time=analysis.recommended_follow_up_time,
            conversion_probability=analysis.conversion_probability,
            urgency_level=analysis.urgency_level,
            personalization_notes=analysis.personalization_notes,
            knowledge_used=knowledge_used,
            rag_enhanced=rag_enhanced,
            knowledge_confidence=knowledge_confidence
        )
    
    def get_high_priority_leads(self, rep_id: str) -> List[Dict[str, Any]]:
        """Get high priority leads requiring immediate attention"""
        return self.conversation_manager.get_high_priority_leads(rep_id)
    
    def get_pending_follow_ups(self, rep_id: str) -> List[Dict[str, Any]]:
        """Get leads that need follow-up based on timing"""
        return self.conversation_manager.get_pending_follow_ups(rep_id)
    
    def get_lead_conversation_history(self, lead_id: str) -> List[Dict[str, Any]]:
        """Get complete conversation history for a specific lead"""
        return self.conversation_manager.get_lead_history(lead_id)
    
    # LEGACY COMPATIBILITY
    
    async def analyze_legacy_conversation(
        self, 
        conversation_input: LegacyConversationInput
    ) -> LegacyConversationAnalysis:
        """
        Legacy compatibility method for existing integrations
        
        Args:
            conversation_input: Legacy conversation input format
            
        Returns:
            LegacyConversationAnalysis in old format
        """
        try:
            # Convert to new format
            new_input = ConversationInput(
                lead_id=conversation_input.lead_id,
                channel=conversation_input.channel,
                conversation_text=conversation_input.conversation_text,
                rep_id="legacy_rep",  # Default rep ID for legacy calls
                timestamp=datetime.now()
            )
            
            # Analyze with new system
            analysis = await self.analyze_conversation(new_input)
            
            # Convert back to legacy format
            return LegacyConversationAnalysis(
                summary=analysis.summary,
                detected_intent=analysis.detected_intent.value,
                objections=[obj.objection_text for obj in analysis.objections],
                suggested_next_steps=analysis.next_steps
            )
            
        except Exception as e:
            print(f"Legacy analysis error: {e}")
            return LegacyConversationAnalysis(
                summary="Legacy analysis failed",
                detected_intent="needs_more_info",
                objections=[],
                suggested_next_steps=["Manual review required"]
            )
