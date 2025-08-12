"""
Fallback Vector Service for Testing
When AWS services are not configured, this provides in-memory vector search
"""

import json
import os
from typing import List, Dict, Any, Optional
import numpy as np
from pathlib import Path


class FallbackVectorService:
    """In-memory vector service for testing without AWS dependencies"""
    
    def __init__(self):
        self.documents = {}  # doc_id -> {content, embedding, metadata}
        self.storage_path = Path("fallback_vector_storage.json")
        self.load_storage()
    
    def load_storage(self):
        """Load documents from disk"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert embedding lists back to numpy arrays
                    for doc_id, doc_data in data.items():
                        if 'embedding' in doc_data:
                            doc_data['embedding'] = np.array(doc_data['embedding'])
                    self.documents = data
        except Exception as e:
            print(f"Warning: Could not load fallback storage: {e}")
    
    def save_storage(self):
        """Save documents to disk"""
        try:
            # Convert numpy arrays to lists for JSON serialization
            save_data = {}
            for doc_id, doc_data in self.documents.items():
                save_data[doc_id] = doc_data.copy()
                if 'embedding' in save_data[doc_id] and hasattr(save_data[doc_id]['embedding'], 'tolist'):
                    save_data[doc_id]['embedding'] = save_data[doc_id]['embedding'].tolist()
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save fallback storage: {e}")
    
    async def initialize_indices(self):
        """Initialize storage (no-op for fallback)"""
        return True
    
    async def index_document(self, doc_id: str, content: str, embedding: List[float], 
                           metadata: Dict[str, Any] = None) -> bool:
        """Index a document in memory"""
        try:
            self.documents[doc_id] = {
                'content': content,
                'embedding': np.array(embedding),
                'metadata': metadata or {},
                'doc_id': doc_id
            }
            self.save_storage()
            return True
        except Exception as e:
            print(f"Error indexing document {doc_id}: {e}")
            return False
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from memory"""
        try:
            # Delete exact match and chunks
            deleted_count = 0
            to_delete = []
            
            for doc_id in self.documents:
                if doc_id.startswith(document_id):
                    to_delete.append(doc_id)
            
            for doc_id in to_delete:
                del self.documents[doc_id]
                deleted_count += 1
            
            if deleted_count > 0:
                self.save_storage()
            
            return deleted_count > 0
        except Exception as e:
            print(f"Error deleting document {document_id}: {e}")
            return False
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            # Ensure vectors are numpy arrays
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            print(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    async def vector_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search documents using vector similarity (without embeddings service)
        For testing, we'll use simple text matching as fallback
        """
        try:
            if not self.documents:
                return []
            
            # Simple text-based scoring when no embeddings available
            results = []
            query_lower = query.lower()
            
            for doc_id, doc_data in self.documents.items():
                content = doc_data['content'].lower()
                
                # Calculate simple relevance score
                score = 0.0
                
                # Exact phrase match
                if query_lower in content:
                    score += 0.8
                
                # Word overlap
                query_words = set(query_lower.split())
                content_words = set(content.split())
                word_overlap = len(query_words.intersection(content_words))
                word_score = word_overlap / max(len(query_words), 1)
                score += word_score * 0.5
                
                if score > 0:
                    results.append({
                        'content': doc_data['content'],
                        'score': score,
                        'metadata': doc_data.get('metadata', {}),
                        'doc_id': doc_id
                    })
            
            # Sort by score and return top results
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:limit]
            
        except Exception as e:
            print(f"Error in vector search: {e}")
            return []
    
    async def vector_search_with_embedding(self, query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Search using actual vector embeddings when available"""
        try:
            if not self.documents:
                return []
            
            query_vec = np.array(query_embedding)
            results = []
            
            for doc_id, doc_data in self.documents.items():
                if 'embedding' in doc_data:
                    doc_embedding = doc_data['embedding']
                    similarity = self.cosine_similarity(query_vec, doc_embedding)
                    
                    results.append({
                        'content': doc_data['content'],
                        'score': similarity,
                        'metadata': doc_data.get('metadata', {}),
                        'doc_id': doc_id
                    })
            
            # Sort by similarity score
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:limit]
            
        except Exception as e:
            print(f"Error in embedding-based search: {e}")
            return []
    
    def get_document_count(self) -> int:
        """Get total number of documents"""
        return len(self.documents)
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information"""
        return {
            'document_count': len(self.documents),
            'storage_file': str(self.storage_path),
            'storage_exists': self.storage_path.exists(),
            'storage_size': self.storage_path.stat().st_size if self.storage_path.exists() else 0
        }
