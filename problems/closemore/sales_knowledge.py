"""
Sales Knowledge Manager for CloseMore RAG System
Manages sales playbooks, objection handling scripts, and product knowledge for retrieval
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import hashlib
from .embeddings import ClosemoreEmbeddingService, EmbeddingResult

@dataclass
class SalesDocument:
    """Sales knowledge document structure"""
    doc_id: str
    title: str
    content: str
    doc_type: str  # playbook, objection_script, product_info, case_study, etc.
    category: str  # price_objections, technical_questions, competitor_comparison, etc.
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    priority: int  # 1-10 priority for retrieval
    embedding_vector: Optional[List[float]] = None

@dataclass
class RetrievalResult:
    """Result from knowledge retrieval"""
    document: SalesDocument
    similarity_score: float
    relevance_reason: str

class SalesKnowledgeManager:
    """Manages sales knowledge documents and retrieval for CloseMore"""
    
    def __init__(self, storage_path: str = "data/closemore"):
        """Initialize sales knowledge manager"""
        self.storage_path = storage_path
        self.knowledge_file = os.path.join(storage_path, "sales_knowledge.json")
        self.embedding_service = ClosemoreEmbeddingService()
        
        # Create storage directory
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize with default sales knowledge
        self._initialize_default_knowledge()
        
        print(f"SalesKnowledgeManager initialized with storage at: {storage_path}")
    
    def add_document(
        self, 
        title: str, 
        content: str, 
        doc_type: str, 
        category: str, 
        tags: List[str], 
        priority: int = 5
    ) -> str:
        """
        Add a new sales knowledge document
        
        Args:
            title: Document title
            content: Document content
            doc_type: Type of document (playbook, objection_script, etc.)
            category: Category for organization
            tags: Tags for categorization
            priority: Priority level (1-10)
            
        Returns:
            Document ID
        """
        # Generate document ID
        doc_id = self._generate_doc_id(title, content)
        
        # Generate embedding for the content
        embedding_result = self.embedding_service.get_embedding(content)
        
        # Create document
        document = SalesDocument(
            doc_id=doc_id,
            title=title,
            content=content,
            doc_type=doc_type,
            category=category,
            tags=tags,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            priority=priority,
            embedding_vector=embedding_result.vector if embedding_result.success else None
        )
        
        # Load existing documents
        documents = self._load_documents()
        
        # Add or update document
        documents[doc_id] = asdict(document)
        
        # Save documents
        self._save_documents(documents)
        
        print(f"Sales document added: {title} (ID: {doc_id})")
        return doc_id
    
    def retrieve_relevant_knowledge(
        self, 
        query: str, 
        doc_types: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        top_k: int = 5,
        min_similarity: float = 0.3
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant sales knowledge based on query
        
        Args:
            query: Search query (conversation content, objection, etc.)
            doc_types: Filter by document types
            categories: Filter by categories
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of RetrievalResult objects
        """
        # Generate query embedding
        query_embedding = self.embedding_service.get_embedding(query)
        
        if not query_embedding.success:
            return []
        
        # Load documents
        documents = self._load_documents()
        
        # Calculate similarities and filter
        results = []
        for doc_data in documents.values():
            # Apply filters
            if doc_types and doc_data['doc_type'] not in doc_types:
                continue
            if categories and doc_data['category'] not in categories:
                continue
            
            # Skip documents without embeddings
            if not doc_data.get('embedding_vector'):
                continue
            
            # Calculate similarity
            similarity = self.embedding_service.calculate_similarity(
                query_embedding.vector,
                doc_data['embedding_vector']
            )
            
            # Apply minimum similarity threshold
            if similarity < min_similarity:
                continue
            
            # Create document object
            document = SalesDocument(**{
                **doc_data,
                'created_at': datetime.fromisoformat(doc_data['created_at']),
                'updated_at': datetime.fromisoformat(doc_data['updated_at'])
            })
            
            # Generate relevance reason
            relevance_reason = self._generate_relevance_reason(query, document, similarity)
            
            results.append(RetrievalResult(
                document=document,
                similarity_score=similarity,
                relevance_reason=relevance_reason
            ))
        
        # Sort by similarity score and priority
        results.sort(key=lambda x: (x.similarity_score * 0.8 + x.document.priority * 0.02), reverse=True)
        
        return results[:top_k]
    
    def get_objection_responses(self, objection_text: str) -> List[RetrievalResult]:
        """Get specific objection handling responses"""
        return self.retrieve_relevant_knowledge(
            query=objection_text,
            doc_types=["objection_script"],
            top_k=3,
            min_similarity=0.4
        )
    
    def get_competitive_comparisons(self, competitor_name: str) -> List[RetrievalResult]:
        """Get competitive comparison information"""
        return self.retrieve_relevant_knowledge(
            query=competitor_name,
            categories=["competitor_comparison"],
            top_k=3,
            min_similarity=0.3
        )
    
    def get_product_information(self, product_query: str) -> List[RetrievalResult]:
        """Get product-related information"""
        return self.retrieve_relevant_knowledge(
            query=product_query,
            doc_types=["product_info"],
            top_k=3,
            min_similarity=0.4
        )
    
    def get_success_stories(self, context: str) -> List[RetrievalResult]:
        """Get relevant success stories and case studies"""
        return self.retrieve_relevant_knowledge(
            query=context,
            doc_types=["case_study", "success_story"],
            top_k=2,
            min_similarity=0.3
        )
    
    def _initialize_default_knowledge(self):
        """Initialize with default sales knowledge if storage is empty"""
        if os.path.exists(self.knowledge_file):
            return  # Knowledge already exists
        
        # Default sales knowledge for Odin School
        default_knowledge = [
            {
                "title": "Price Objection - High Course Fee",
                "content": "When prospects mention high course fees: 1) Acknowledge their concern 2) Break down ROI - average 40% salary increase post-completion 3) Highlight payment plans - EMI options available 4) Share success story of similar profile 5) Emphasize job placement support with 85% success rate",
                "doc_type": "objection_script",
                "category": "price_objections",
                "tags": ["price", "objection", "roi", "payment_plans"],
                "priority": 9
            },
            {
                "title": "Job Guarantee Questions",
                "content": "Job placement support includes: 1) Dedicated placement team 2) Resume building and optimization 3) Mock interview sessions 4) Direct company partnerships 5) 85% placement rate within 3 months 6) Salary negotiation coaching 7) Continued support for 6 months post-completion",
                "doc_type": "product_info",
                "category": "job_support",
                "tags": ["job_placement", "guarantee", "support"],
                "priority": 10
            },
            {
                "title": "Competitor Comparison - DataCamp",
                "content": "DataCamp vs Odin School: DataCamp offers self-paced online courses but lacks: 1) Live instructor interaction 2) Job placement support 3) Industry project experience 4) Personalized mentorship 5) Local market focus. Odin School provides comprehensive career transformation with proven results.",
                "doc_type": "objection_script",
                "category": "competitor_comparison",
                "tags": ["datacamp", "comparison", "advantages"],
                "priority": 8
            },
            {
                "title": "Competitor Comparison - Simplilearn",
                "content": "Simplilearn vs Odin School: While Simplilearn has broader course catalog, Odin School excels in: 1) Smaller batch sizes (max 20 students) 2) Industry-specific curriculum 3) Higher placement rates (85% vs 65%) 4) Local market expertise 5) Personalized career coaching 6) Strong alumni network in your region",
                "doc_type": "objection_script",
                "category": "competitor_comparison",
                "tags": ["simplilearn", "comparison", "advantages"],
                "priority": 8
            },
            {
                "title": "Time Commitment Concerns",
                "content": "For working professionals concerned about time: 1) Flexible weekend batches available 2) Evening classes (7-10 PM) 3) Recorded sessions for review 4) Self-paced assignments 5) Mobile app for learning on-the-go 6) Average 8-10 hours/week commitment 7) Can pause/resume course if needed",
                "doc_type": "objection_script",
                "category": "time_commitment",
                "tags": ["time", "flexibility", "working_professionals"],
                "priority": 7
            },
            {
                "title": "Success Story - Business Analyst to Data Scientist",
                "content": "Rajesh, Business Analyst at TCS (3 years exp): Enrolled in Data Science course, completed in 6 months while working. Secured Data Scientist role at Flipkart with 60% salary increase (₹8L to ₹12.8L). Key factors: strong foundation building, practical projects, interview preparation, and dedicated placement support.",
                "doc_type": "case_study",
                "category": "success_stories",
                "tags": ["business_analyst", "data_science", "career_change", "salary_increase"],
                "priority": 9
            },
            {
                "title": "Course Curriculum - Data Science",
                "content": "Data Science curriculum covers: 1) Python fundamentals and libraries 2) Statistics and probability 3) Machine learning algorithms 4) Deep learning and neural networks 5) Data visualization (Tableau, Power BI) 6) Big data technologies (Spark, Hadoop) 7) Real industry projects 8) Capstone project 9) Soft skills and communication 10) Interview preparation",
                "doc_type": "product_info",
                "category": "curriculum",
                "tags": ["data_science", "curriculum", "python", "machine_learning"],
                "priority": 8
            },
            {
                "title": "Payment Plans and EMI Options",
                "content": "Flexible payment options: 1) Full payment - 5% discount 2) Two installments - no extra cost 3) EMI options through partners (6-24 months) 4) Scholarship program for meritorious students 5) Corporate sponsorship assistance 6) Income Share Agreement pilot program 7) Refund policy - full refund within first 2 weeks",
                "doc_type": "product_info",
                "category": "payment_plans",
                "tags": ["payment", "emi", "scholarship", "refund"],
                "priority": 9
            }
        ]
        
        # Add default knowledge documents
        for knowledge in default_knowledge:
            self.add_document(
                title=knowledge["title"],
                content=knowledge["content"],
                doc_type=knowledge["doc_type"],
                category=knowledge["category"],
                tags=knowledge["tags"],
                priority=knowledge["priority"]
            )
        
        print("Default sales knowledge initialized successfully")
    
    def _generate_doc_id(self, title: str, content: str) -> str:
        """Generate unique document ID"""
        content_hash = hashlib.md5(f"{title}{content}".encode()).hexdigest()
        return f"sales_{content_hash[:12]}"
    
    def _generate_relevance_reason(self, query: str, document: SalesDocument, similarity: float) -> str:
        """Generate explanation for why document is relevant"""
        if similarity > 0.8:
            return f"Highly relevant to '{query[:30]}...' - strong content match"
        elif similarity > 0.6:
            return f"Relevant to '{query[:30]}...' - good content alignment"
        elif similarity > 0.4:
            return f"Moderately relevant to '{query[:30]}...' - partial content match"
        else:
            return f"Basic relevance to '{query[:30]}...' - may contain useful information"
    
    def _load_documents(self) -> Dict[str, Any]:
        """Load documents from storage"""
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading documents: {e}")
            return {}
    
    def _save_documents(self, documents: Dict[str, Any]):
        """Save documents to storage"""
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(documents, f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving documents: {e}")
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        documents = self._load_documents()
        
        doc_types = {}
        categories = {}
        total_docs = len(documents)
        
        for doc_data in documents.values():
            doc_type = doc_data.get('doc_type', 'unknown')
            category = doc_data.get('category', 'unknown')
            
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            categories[category] = categories.get(category, 0) + 1
        
        return {
            "total_documents": total_docs,
            "document_types": doc_types,
            "categories": categories,
            "last_updated": datetime.now().isoformat()
        }
