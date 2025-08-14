"""
TrustDesk Knowledge Base Management
==================================
Manages the knowledge base documents, embeddings, and retrieval for RAG.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel
import uuid
from database import get_database
from .embeddings import embedding_service

class KnowledgeDocument(BaseModel):
    """Model for knowledge base documents"""
    id: Optional[str] = None
    title: str
    content: str
    category: str  # policy, faq, course_info, procedure
    department: str = "customer_service"  # customer_service, technical, sales
    priority: int = 1  # 1=low, 2=medium, 3=high
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True

class FAQDocument(BaseModel):
    """Model for FAQ documents"""
    id: Optional[str] = None
    question: str
    answer: str
    category: str
    keywords: List[str] = []
    embedding: Optional[List[float]] = None
    usage_count: int = 0
    effectiveness_rating: float = 0.0
    created_at: Optional[datetime] = None
    is_active: bool = True

class HistoricalResponse(BaseModel):
    """Model for successful historical responses"""
    id: Optional[str] = None
    original_comment: str
    successful_reply: str
    sentiment: str
    urgency_level: str
    resolution_rating: float = 0.0
    response_time_hours: Optional[float] = None
    embedding: Optional[List[float]] = None
    created_at: Optional[datetime] = None
    is_effective: bool = True

class KnowledgeBaseService:
    """Service for managing the knowledge base"""
    
    def __init__(self):
        self.db = None
        self.knowledge_collection = "trustdesk_knowledge"
        self.faq_collection = "trustdesk_faq"
        self.responses_collection = "trustdesk_responses"
    
    async def _get_db(self):
        """Get database connection"""
        if not self.db:
            self.db = get_database()
        return self.db
    
    async def add_knowledge_document(self, document: KnowledgeDocument) -> str:
        """
        Add a new knowledge document with embedding
        
        Args:
            document: KnowledgeDocument to add
            
        Returns:
            Document ID
        """
        db = await self._get_db()
        if not db:
            raise Exception("Database not available")
        
        # Generate ID and timestamps
        document.id = str(uuid.uuid4())
        document.created_at = datetime.utcnow()
        document.updated_at = datetime.utcnow()
        
        # Generate embedding for the content
        content_text = f"{document.title} {document.content}"
        document.embedding = await embedding_service.get_embedding(content_text)
        
        # Insert into MongoDB
        doc_dict = document.model_dump()
        result = await db[self.knowledge_collection].insert_one(doc_dict)
        
        return document.id
    
    async def add_faq_document(self, faq: FAQDocument) -> str:
        """Add FAQ document with embedding"""
        db = await self._get_db()
        if not db:
            raise Exception("Database not available")
        
        faq.id = str(uuid.uuid4())
        faq.created_at = datetime.utcnow()
        
        # Generate embedding for question + answer
        faq_text = f"{faq.question} {faq.answer}"
        faq.embedding = await embedding_service.get_embedding(faq_text)
        
        doc_dict = faq.model_dump()
        await db[self.faq_collection].insert_one(doc_dict)
        
        return faq.id
    
    async def add_historical_response(self, response: HistoricalResponse) -> str:
        """Add historical response with embedding"""
        db = await self._get_db()
        if not db:
            raise Exception("Database not available")
        
        response.id = str(uuid.uuid4())
        response.created_at = datetime.utcnow()
        
        # Generate embedding for the original comment
        response.embedding = await embedding_service.get_embedding(response.original_comment)
        
        doc_dict = response.model_dump()
        await db[self.responses_collection].insert_one(doc_dict)
        
        return response.id
    
    async def search_knowledge(self, query: str, top_k: int = 5, 
                             category: Optional[str] = None) -> List[Dict]:
        """
        Search knowledge base using vector similarity
        
        Args:
            query: Search query
            top_k: Number of results to return
            category: Optional category filter
            
        Returns:
            List of relevant knowledge documents with similarity scores
        """
        db = await self._get_db()
        if not db:
            return []
        
        # Generate query embedding
        query_embedding = await embedding_service.get_embedding(query)
        
        # Build MongoDB filter
        filter_query = {"is_active": True}
        if category:
            filter_query["category"] = category
        
        # Get all documents matching filter
        cursor = db[self.knowledge_collection].find(filter_query)
        documents = await cursor.to_list(length=None)
        
        if not documents:
            return []
        
        # Extract embeddings and calculate similarities
        embeddings = [doc.get('embedding', []) for doc in documents]
        similarities = embedding_service.find_most_similar(
            query_embedding, embeddings, top_k
        )
        
        # Prepare results with similarity scores
        results = []
        for idx, similarity in similarities:
            doc = documents[idx].copy()
            doc['similarity_score'] = similarity
            doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
            results.append(doc)
        
        return results
    
    async def search_faq(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search FAQ using vector similarity"""
        db = await self._get_db()
        if not db:
            return []
        
        query_embedding = await embedding_service.get_embedding(query)
        
        cursor = db[self.faq_collection].find({"is_active": True})
        faqs = await cursor.to_list(length=None)
        
        if not faqs:
            return []
        
        embeddings = [faq.get('embedding', []) for faq in faqs]
        similarities = embedding_service.find_most_similar(
            query_embedding, embeddings, top_k
        )
        
        results = []
        for idx, similarity in similarities:
            faq = faqs[idx].copy()
            faq['similarity_score'] = similarity
            faq['_id'] = str(faq['_id'])
            results.append(faq)
        
        return results
    
    async def search_historical_responses(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search historical responses for similar situations"""
        db = await self._get_db()
        if not db:
            return []
        
        query_embedding = await embedding_service.get_embedding(query)
        
        cursor = db[self.responses_collection].find({"is_effective": True})
        responses = await cursor.to_list(length=None)
        
        if not responses:
            return []
        
        embeddings = [resp.get('embedding', []) for resp in responses]
        similarities = embedding_service.find_most_similar(
            query_embedding, embeddings, top_k
        )
        
        results = []
        for idx, similarity in similarities:
            response = responses[idx].copy()
            response['similarity_score'] = similarity
            response['_id'] = str(response['_id'])
            results.append(response)
        
        return results
    
    async def get_all_knowledge(self, category: Optional[str] = None) -> List[Dict]:
        """Get all knowledge documents"""
        db = await self._get_db()
        if not db:
            return []
        
        filter_query = {"is_active": True}
        if category:
            filter_query["category"] = category
        
        cursor = db[self.knowledge_collection].find(filter_query)
        documents = await cursor.to_list(length=None)
        
        # Convert ObjectId to string
        for doc in documents:
            doc['_id'] = str(doc['_id'])
        
        return documents
    
    async def update_knowledge_document(self, doc_id: str, updates: Dict) -> bool:
        """Update a knowledge document"""
        db = await self._get_db()
        if not db:
            return False
        
        updates['updated_at'] = datetime.utcnow()
        
        # If content is updated, regenerate embedding
        if 'content' in updates or 'title' in updates:
            # Get current document to combine title and content
            current_doc = await db[self.knowledge_collection].find_one({"id": doc_id})
            if current_doc:
                title = updates.get('title', current_doc.get('title', ''))
                content = updates.get('content', current_doc.get('content', ''))
                content_text = f"{title} {content}"
                updates['embedding'] = await embedding_service.get_embedding(content_text)
        
        result = await db[self.knowledge_collection].update_one(
            {"id": doc_id}, 
            {"$set": updates}
        )
        
        return result.modified_count > 0
    
    async def delete_knowledge_document(self, doc_id: str) -> bool:
        """Soft delete a knowledge document"""
        return await self.update_knowledge_document(doc_id, {"is_active": False})

# Global knowledge base service instance
knowledge_service = KnowledgeBaseService()
