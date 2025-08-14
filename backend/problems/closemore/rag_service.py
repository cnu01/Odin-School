"""
CloseMore RAG Service - Retrieval-Augmented Generation for Sales Conversations
Combines conversation analysis with sales knowledge retrieval for enhanced recommendations
"""

import asyncio
from typing import List, Dict, Any, Optional
from .models import ConversationInput, ConversationAnalysis, NextBestAction, ObjectionAnalysis
from .bedrock_service import ClosemoreBedrockService
from .sales_knowledge import SalesKnowledgeManager, RetrievalResult
from .embeddings import ClosemoreEmbeddingService

class ClosemoreRAGService:
    """RAG service that enhances conversation analysis with sales knowledge retrieval"""
    
    def __init__(self):
        """Initialize RAG service with all components"""
        self.bedrock_service = ClosemoreBedrockService()
        self.knowledge_manager = SalesKnowledgeManager()
        self.embedding_service = ClosemoreEmbeddingService()
        
        print("ClosemoreRAGService initialized successfully")
    
    async def analyze_conversation_with_rag(self, conversation: ConversationInput) -> ConversationAnalysis:
        """
        Analyze conversation with RAG-enhanced insights
        
        Args:
            conversation: Conversation input to analyze
            
        Returns:
            Enhanced ConversationAnalysis with knowledge-backed recommendations
        """
        try:
            # Step 1: Get basic conversation analysis
            base_analysis = await self.bedrock_service.analyze_conversation_with_bedrock(conversation)
            
            # Step 2: Retrieve relevant knowledge based on conversation content
            relevant_knowledge = await self._retrieve_contextual_knowledge(
                conversation.conversation_text, 
                base_analysis
            )
            
            # Step 3: Enhance analysis with RAG insights
            enhanced_analysis = await self._enhance_analysis_with_knowledge(
                base_analysis, 
                relevant_knowledge,
                conversation
            )
            
            return enhanced_analysis
            
        except Exception as e:
            print(f"RAG analysis error: {e}")
            # Fallback to base analysis
            return await self.bedrock_service.analyze_conversation_with_bedrock(conversation)
    
    async def get_enhanced_objection_responses(self, objection_analysis: ObjectionAnalysis) -> List[str]:
        """
        Get enhanced objection responses using RAG knowledge retrieval
        
        Args:
            objection_analysis: Detected objection from conversation analysis
            
        Returns:
            List of enhanced response suggestions
        """
        try:
            # Retrieve specific objection handling knowledge
            objection_knowledge = self.knowledge_manager.get_objection_responses(
                objection_analysis.objection_text
            )
            
            if objection_knowledge:
                # Extract response suggestions from retrieved knowledge
                responses = []
                for result in objection_knowledge:
                    # Parse structured response from knowledge content
                    response_text = self._extract_response_suggestions(result.document.content)
                    responses.extend(response_text)
                
                return responses[:3]  # Return top 3 responses
            
            # Fallback to original suggestion
            return [objection_analysis.suggested_response]
            
        except Exception as e:
            print(f"Enhanced objection response error: {e}")
            return [objection_analysis.suggested_response]
    
    async def get_contextual_next_steps(
        self, 
        conversation: ConversationInput, 
        analysis: ConversationAnalysis
    ) -> List[str]:
        """
        Get contextual next steps enhanced with relevant sales knowledge
        
        Args:
            conversation: Original conversation input
            analysis: Conversation analysis results
            
        Returns:
            Enhanced list of next steps with specific knowledge
        """
        try:
            # Determine what type of knowledge to retrieve based on analysis
            knowledge_queries = []
            
            # Add query based on detected intent
            if analysis.detected_intent.value == "price_sensitive":
                knowledge_queries.append("pricing objection payment plans ROI")
            elif analysis.detected_intent.value == "comparing_options":
                knowledge_queries.append("competitor comparison advantages")
            elif analysis.detected_intent.value == "job_support_concerns":
                knowledge_queries.append("job placement guarantee support")
            elif analysis.detected_intent.value == "ready_to_book":
                knowledge_queries.append("enrollment process next steps")
            
            # Add queries based on objections
            for objection in analysis.objections:
                knowledge_queries.append(objection.objection_text)
            
            # Retrieve relevant knowledge
            all_knowledge = []
            for query in knowledge_queries:
                knowledge_results = self.knowledge_manager.retrieve_relevant_knowledge(
                    query=query,
                    top_k=2,
                    min_similarity=0.4
                )
                all_knowledge.extend(knowledge_results)
            
            # Generate enhanced next steps
            enhanced_steps = await self._generate_knowledge_enhanced_steps(
                analysis.next_steps,
                all_knowledge,
                conversation,
                analysis
            )
            
            return enhanced_steps
            
        except Exception as e:
            print(f"Contextual next steps error: {e}")
            return analysis.next_steps
    
    async def _retrieve_contextual_knowledge(
        self, 
        conversation_text: str, 
        analysis: ConversationAnalysis
    ) -> List[RetrievalResult]:
        """Retrieve relevant knowledge based on conversation content and analysis"""
        
        knowledge_results = []
        
        try:
            # 1. Retrieve based on conversation content
            general_knowledge = self.knowledge_manager.retrieve_relevant_knowledge(
                query=conversation_text,
                top_k=3,
                min_similarity=0.3
            )
            knowledge_results.extend(general_knowledge)
            
            # 2. Retrieve based on detected objections
            for objection in analysis.objections:
                objection_knowledge = self.knowledge_manager.get_objection_responses(
                    objection.objection_text
                )
                knowledge_results.extend(objection_knowledge)
            
            # 3. Retrieve based on intent
            intent_keywords = {
                "price_sensitive": "pricing payment plans cost ROI",
                "comparing_options": "competitor comparison advantages",
                "job_support_concerns": "job placement guarantee",
                "technical_questions": "curriculum technical details",
                "ready_to_book": "enrollment process success stories"
            }
            
            intent_query = intent_keywords.get(analysis.detected_intent.value, "")
            if intent_query:
                intent_knowledge = self.knowledge_manager.retrieve_relevant_knowledge(
                    query=intent_query,
                    top_k=2,
                    min_similarity=0.4
                )
                knowledge_results.extend(intent_knowledge)
            
            # Remove duplicates and sort by relevance
            unique_results = {}
            for result in knowledge_results:
                if result.document.doc_id not in unique_results:
                    unique_results[result.document.doc_id] = result
                elif result.similarity_score > unique_results[result.document.doc_id].similarity_score:
                    unique_results[result.document.doc_id] = result
            
            return list(unique_results.values())
            
        except Exception as e:
            print(f"Knowledge retrieval error: {e}")
            return []
    
    async def _enhance_analysis_with_knowledge(
        self, 
        base_analysis: ConversationAnalysis, 
        knowledge_results: List[RetrievalResult],
        conversation: ConversationInput
    ) -> ConversationAnalysis:
        """Enhance conversation analysis with retrieved knowledge"""
        
        try:
            # Enhance objection responses with knowledge
            enhanced_objections = []
            for objection in base_analysis.objections:
                enhanced_response = await self.get_enhanced_objection_responses(objection)
                
                # Update objection with enhanced response
                enhanced_objection = ObjectionAnalysis(
                    objection_text=objection.objection_text,
                    objection_category=objection.objection_category,
                    severity=objection.severity,
                    suggested_response=enhanced_response[0] if enhanced_response else objection.suggested_response
                )
                enhanced_objections.append(enhanced_objection)
            
            # Enhance next steps with contextual knowledge
            enhanced_next_steps = await self.get_contextual_next_steps(conversation, base_analysis)
            
            # Enhance personalization notes with knowledge insights
            enhanced_personalization = self._enhance_personalization_notes(
                base_analysis.personalization_notes,
                knowledge_results
            )
            
            # Create enhanced analysis
            enhanced_analysis = ConversationAnalysis(
                lead_id=base_analysis.lead_id,
                summary=base_analysis.summary,
                detailed_summary=base_analysis.detailed_summary,
                detected_intent=base_analysis.detected_intent,
                intent_confidence=base_analysis.intent_confidence,
                objections=enhanced_objections,
                sentiment_analysis=base_analysis.sentiment_analysis,
                key_topics=base_analysis.key_topics,
                next_steps=enhanced_next_steps,
                recommended_follow_up_time=base_analysis.recommended_follow_up_time,
                conversion_probability=base_analysis.conversion_probability,
                urgency_level=base_analysis.urgency_level,
                personalization_notes=enhanced_personalization
            )
            
            return enhanced_analysis
            
        except Exception as e:
            print(f"Analysis enhancement error: {e}")
            return base_analysis
    
    async def _generate_knowledge_enhanced_steps(
        self, 
        original_steps: List[str], 
        knowledge_results: List[RetrievalResult],
        conversation: ConversationInput,
        analysis: ConversationAnalysis
    ) -> List[str]:
        """Generate next steps enhanced with specific knowledge"""
        
        enhanced_steps = []
        
        # Add original steps as base
        enhanced_steps.extend(original_steps)
        
        # Add knowledge-specific recommendations
        for result in knowledge_results[:3]:  # Top 3 most relevant
            doc = result.document
            
            if doc.doc_type == "objection_script":
                enhanced_steps.append(f"Use proven objection handling: {doc.title}")
            elif doc.doc_type == "case_study":
                enhanced_steps.append(f"Share relevant success story: {doc.title}")
            elif doc.doc_type == "product_info":
                enhanced_steps.append(f"Provide detailed information: {doc.title}")
            elif doc.category == "competitor_comparison":
                enhanced_steps.append(f"Address competition with: {doc.title}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_steps = []
        for step in enhanced_steps:
            if step not in seen:
                seen.add(step)
                unique_steps.append(step)
        
        return unique_steps[:6]  # Limit to 6 actionable steps
    
    def _extract_response_suggestions(self, content: str) -> List[str]:
        """Extract structured response suggestions from knowledge content"""
        
        # Split content into actionable items
        suggestions = []
        
        # Look for numbered or bulleted lists
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-')):
                # Clean up the suggestion
                clean_suggestion = line.lstrip('0123456789.)•- ').strip()
                if clean_suggestion:
                    suggestions.append(clean_suggestion)
        
        # If no structured list found, return first sentence
        if not suggestions:
            sentences = content.split('.')
            if sentences:
                suggestions.append(sentences[0].strip())
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _enhance_personalization_notes(
        self, 
        original_notes: str, 
        knowledge_results: List[RetrievalResult]
    ) -> str:
        """Enhance personalization notes with knowledge insights"""
        
        enhanced_notes = original_notes
        
        # Add knowledge-based insights
        knowledge_insights = []
        for result in knowledge_results[:2]:  # Top 2 most relevant
            doc = result.document
            insight = f"Reference {doc.title} for {doc.category}"
            knowledge_insights.append(insight)
        
        if knowledge_insights:
            if enhanced_notes:
                enhanced_notes += " | Knowledge: " + "; ".join(knowledge_insights)
            else:
                enhanced_notes = "Knowledge: " + "; ".join(knowledge_insights)
        
        return enhanced_notes
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        return self.knowledge_manager.get_knowledge_stats()
