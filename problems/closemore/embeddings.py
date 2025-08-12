"""
Embeddings Service for CloseMore RAG System
Provides vector generation using Amazon Bedrock Titan Embeddings for sales knowledge retrieval
"""

import boto3
import json
import os
from typing import List, Dict, Any, Optional
import numpy as np
from dataclasses import dataclass

@dataclass
class EmbeddingResult:
    """Result from embedding generation"""
    vector: List[float]
    dimension: int
    model_used: str
    success: bool
    error_message: Optional[str] = None

class ClosemoreEmbeddingService:
    """Amazon Bedrock Titan Embeddings service for CloseMore knowledge vectors"""
    
    def __init__(self):
        """Initialize Bedrock embeddings client"""
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.embedding_model_id = "amazon.titan-embed-text-v1"
            self.dimension = 1536  # Titan embedding dimension
            print("CloseMore Embeddings service initialized successfully")
        except Exception as e:
            print(f"Warning: Bedrock embeddings client initialization failed: {e}")
            self.bedrock_client = None
    
    def get_embedding(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text using Amazon Bedrock Titan
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            EmbeddingResult with vector and metadata
        """
        if not self.bedrock_client:
            return self._create_fallback_embedding(text)
        
        try:
            # Clean and prepare text
            clean_text = self._prepare_text_for_embedding(text)
            
            # Prepare request for Titan embeddings
            request_body = {
                "inputText": clean_text
            }
            
            # Call Bedrock Titan embeddings
            response = self.bedrock_client.invoke_model(
                modelId=self.embedding_model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            embedding_vector = response_body.get('embedding', [])
            
            if not embedding_vector or len(embedding_vector) != self.dimension:
                raise Exception(f"Invalid embedding dimension: {len(embedding_vector)}")
            
            return EmbeddingResult(
                vector=embedding_vector,
                dimension=len(embedding_vector),
                model_used=self.embedding_model_id,
                success=True
            )
            
        except Exception as e:
            print(f"Bedrock embedding error: {e}")
            return self._create_fallback_embedding(text)
    
    def get_embeddings_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of EmbeddingResult objects
        """
        results = []
        for text in texts:
            result = self.get_embedding(text)
            results.append(result)
        
        return results
    
    def calculate_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vector1: First embedding vector
            vector2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        try:
            # Convert to numpy arrays
            v1 = np.array(vector1)
            v2 = np.array(vector2)
            
            # Calculate cosine similarity
            dot_product = np.dot(v1, v2)
            norm_v1 = np.linalg.norm(v1)
            norm_v2 = np.linalg.norm(v2)
            
            if norm_v1 == 0 or norm_v2 == 0:
                return 0.0
            
            similarity = dot_product / (norm_v1 * norm_v2)
            
            # Ensure result is between 0 and 1
            return max(0.0, min(1.0, float(similarity)))
            
        except Exception as e:
            print(f"Similarity calculation error: {e}")
            return 0.0
    
    def _prepare_text_for_embedding(self, text: str) -> str:
        """Prepare text for embedding generation"""
        # Clean and truncate text for embedding
        clean_text = text.strip()
        
        # Limit text length for embedding model (Titan has ~8000 token limit)
        max_chars = 7000
        if len(clean_text) > max_chars:
            clean_text = clean_text[:max_chars] + "..."
        
        return clean_text
    
    def _create_fallback_embedding(self, text: str) -> EmbeddingResult:
        """Create a fallback embedding when Bedrock is unavailable"""
        # Simple hash-based embedding as fallback
        import hashlib
        
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Create deterministic but pseudo-random vector
        np.random.seed(int(text_hash[:8], 16))
        fallback_vector = np.random.normal(0, 1, self.dimension).tolist()
        
        # Normalize vector
        norm = np.linalg.norm(fallback_vector)
        if norm > 0:
            fallback_vector = (np.array(fallback_vector) / norm).tolist()
        
        return EmbeddingResult(
            vector=fallback_vector,
            dimension=self.dimension,
            model_used="fallback_hash",
            success=False,
            error_message="Bedrock embeddings unavailable, using fallback"
        )
