"""
TrustDesk RAG Service
====================
Retrieval-Augmented Generation service that combines knowledge retrieval with Bedrock generation.
"""

import json
from typing import Dict, List, Optional, Any
from .models import CommentRequest, AIAnalysisResponse
from .knowledge import knowledge_service
from .embeddings import embedding_service
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

class RAGService:
    """RAG service combining knowledge retrieval with Bedrock Claude generation"""
    
    def __init__(self):
        """Initialize RAG service with Bedrock client"""
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.claude_model = 'anthropic.claude-v2'
    
    async def retrieve_relevant_knowledge(self, query: str) -> Dict[str, List[Dict]]:
        """
        Retrieve relevant knowledge for a query
        
        Args:
            query: User query/comment
            
        Returns:
            Dictionary with different types of relevant knowledge
        """
        # Search all knowledge sources in parallel
        knowledge_docs = await knowledge_service.search_knowledge(query, top_k=3)
        faq_docs = await knowledge_service.search_faq(query, top_k=2)
        historical_responses = await knowledge_service.search_historical_responses(query, top_k=2)
        
        return {
            "knowledge_base": knowledge_docs,
            "faq": faq_docs,
            "historical_responses": historical_responses
        }
    
    def _format_retrieved_context(self, retrieved_knowledge: Dict[str, List[Dict]]) -> str:
        """
        Format retrieved knowledge into context for Claude
        
        Args:
            retrieved_knowledge: Retrieved knowledge from various sources
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Add knowledge base documents
        if retrieved_knowledge.get("knowledge_base"):
            context_parts.append("**COMPANY KNOWLEDGE BASE:**")
            for i, doc in enumerate(retrieved_knowledge["knowledge_base"], 1):
                similarity = doc.get('similarity_score', 0)
                if similarity > 0.7:  # Only include highly relevant docs
                    context_parts.append(f"{i}. {doc['title']} ({doc['category']})")
                    context_parts.append(f"   {doc['content'][:300]}...")
                    context_parts.append("")
        
        # Add FAQ responses
        if retrieved_knowledge.get("faq"):
            context_parts.append("**FREQUENTLY ASKED QUESTIONS:**")
            for i, faq in enumerate(retrieved_knowledge["faq"], 1):
                similarity = faq.get('similarity_score', 0)
                if similarity > 0.6:  # FAQ threshold
                    context_parts.append(f"{i}. Q: {faq['question']}")
                    context_parts.append(f"   A: {faq['answer']}")
                    context_parts.append("")
        
        # Add historical successful responses
        if retrieved_knowledge.get("historical_responses"):
            context_parts.append("**SUCCESSFUL RESPONSE EXAMPLES:**")
            for i, resp in enumerate(retrieved_knowledge["historical_responses"], 1):
                similarity = resp.get('similarity_score', 0)
                if similarity > 0.7:  # High threshold for examples
                    context_parts.append(f"{i}. Similar situation: {resp['original_comment'][:150]}...")
                    context_parts.append(f"   Successful reply: {resp['successful_reply'][:200]}...")
                    context_parts.append(f"   Rating: {resp['resolution_rating']}/5.0")
                    context_parts.append("")
        
        return "\n".join(context_parts)
    
    async def analyze_comment_with_rag(self, comment_request: CommentRequest) -> AIAnalysisResponse:
        """
        Analyze comment using RAG approach
        
        Args:
            comment_request: Comment to analyze
            
        Returns:
            AI analysis enhanced with retrieved knowledge
        """
        try:
            # Step 1: Retrieve relevant knowledge
            retrieved_knowledge = await self.retrieve_relevant_knowledge(comment_request.text)
            
            # Step 2: Format context
            context = self._format_retrieved_context(retrieved_knowledge)
            
            # Step 3: Create enhanced prompt with retrieved context
            prompt = self._create_rag_prompt(comment_request.text, context)
            
            # Step 4: Generate response using Claude with context
            response = await self._generate_with_claude(prompt)
            
            return response
            
        except Exception as e:
            # Fallback to non-RAG response
            print(f"RAG analysis failed, using fallback: {str(e)}")
            return await self._fallback_analysis(comment_request.text)
    
    def _create_rag_prompt(self, comment: str, context: str) -> str:
        """Create enhanced prompt with retrieved context"""
        
        base_prompt = f"""You are 'TrustDesk', an AI brand reputation analyst for Odin School, an online education platform. 

You have access to the company's knowledge base, FAQ responses, and historical successful interactions below. Use this information to provide accurate, company-aligned responses.

{context}

**INSTRUCTIONS:**
1. Use the retrieved knowledge above to inform your analysis
2. If the comment matches FAQ patterns, reference appropriate FAQ responses
3. If similar situations exist in historical responses, learn from successful approaches
4. Follow company policies from the knowledge base
5. Maintain professional, empathetic tone consistent with Odin School's brand

**BRAND VOICE GUIDE:**
- **DO:** Acknowledge feelings, be reassuring, reference specific policies when relevant
- **DO NOT:** Make promises not supported by retrieved knowledge, admit fault without policy backing

**YOUR TASK:**
Analyze the user's comment below and return ONLY a valid JSON object with these four keys:

1. `"urgency"`: Classify as 'High', 'Medium', or 'Low' based on content and retrieved context
2. `"is_sensitive"`: Boolean indicating if this contains sensitive topics
3. `"summary"`: Concise one-sentence summary of the main point
4. `"draft_reply"`: Professional response using retrieved knowledge when applicable

Here is the user comment to analyze:
---
{comment}
---

Remember: Return ONLY the JSON object, nothing else."""

        return base_prompt
    
    async def _generate_with_claude(self, prompt: str) -> AIAnalysisResponse:
        """Generate response using Claude with RAG context"""
        
        request_body = {
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": 1000,
            "temperature": 0.1,
            "top_k": 250,
            "top_p": 1,
            "stop_sequences": ["\n\nHuman:"]
        }
        
        response = self.bedrock_client.invoke_model(
            body=json.dumps(request_body),
            modelId=self.claude_model,
            accept='application/json',
            contentType='application/json'
        )
        
        response_body = json.loads(response.get('body').read())
        generated_text = response_body.get('completion', '').strip()
        
        # Parse JSON from Claude's response
        try:
            if '{' in generated_text and '}' in generated_text:
                start_idx = generated_text.find('{')
                end_idx = generated_text.rfind('}') + 1
                json_str = generated_text[start_idx:end_idx]
                analysis_result = json.loads(json_str)
            else:
                raise ValueError("No valid JSON found in response")
                
        except (json.JSONDecodeError, ValueError):
            # Fallback response
            analysis_result = {
                "urgency": "Medium",
                "is_sensitive": False,
                "summary": "Analysis completed with knowledge base context.",
                "draft_reply": "Thank you for your message. Our team has reviewed your inquiry and will respond with appropriate information from our knowledge base."
            }
        
        return AIAnalysisResponse(**analysis_result)
    
    async def _fallback_analysis(self, comment: str) -> AIAnalysisResponse:
        """Fallback analysis without RAG"""
        return AIAnalysisResponse(
            urgency="Medium",
            is_sensitive=False,
            summary="Unable to access knowledge base, providing standard response.",
            draft_reply="Thank you for your message. We appreciate your feedback and our team will review your inquiry. For immediate assistance, please contact our support team."
        )
    
    async def add_successful_response(self, original_comment: str, reply: str, 
                                    rating: float, sentiment: str = "neutral") -> str:
        """
        Add a successful response to the knowledge base for future learning
        
        Args:
            original_comment: Original customer comment
            reply: Successful reply that was used
            rating: Effectiveness rating (1-5)
            sentiment: Detected sentiment
            
        Returns:
            ID of the stored response
        """
        from .knowledge import HistoricalResponse
        
        historical_response = HistoricalResponse(
            original_comment=original_comment,
            successful_reply=reply,
            sentiment=sentiment,
            urgency_level="medium",  # Could be determined dynamically
            resolution_rating=rating,
            is_effective=rating >= 3.0  # Only mark as effective if rating >= 3
        )
        
        return await knowledge_service.add_historical_response(historical_response)
    
    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        knowledge_docs = await knowledge_service.get_all_knowledge()
        
        stats = {
            "total_knowledge_documents": len(knowledge_docs),
            "categories": {},
            "departments": {},
            "priority_distribution": {"high": 0, "medium": 0, "low": 0}
        }
        
        for doc in knowledge_docs:
            # Count by category
            category = doc.get('category', 'unknown')
            stats["categories"][category] = stats["categories"].get(category, 0) + 1
            
            # Count by department
            department = doc.get('department', 'unknown')
            stats["departments"][department] = stats["departments"].get(department, 0) + 1
            
            # Count by priority
            priority = doc.get('priority', 1)
            if priority == 3:
                stats["priority_distribution"]["high"] += 1
            elif priority == 2:
                stats["priority_distribution"]["medium"] += 1
            else:
                stats["priority_distribution"]["low"] += 1
        
        return stats

# Global RAG service instance
rag_service = RAGService()
