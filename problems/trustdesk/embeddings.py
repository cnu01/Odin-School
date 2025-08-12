"""
TrustDesk Embedding Service
==========================
Handles text embeddings using Amazon Bedrock Titan Embeddings model.
"""

import boto3
import json
import os
import numpy as np
from typing import List, Union
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    """Service for generating and managing text embeddings using Amazon Bedrock"""
    
    def __init__(self):
        """Initialize Bedrock client for embeddings"""
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1'),
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            self.embedding_model = 'amazon.titan-embed-text-v1'
            self.embedding_dimension = 1536  # Titan embeddings dimension
            self.available = True
        except Exception as e:
            print(f"⚠️ Bedrock embeddings not available: {e}")
            self.bedrock_client = None
            self.embedding_model = None
            self.embedding_dimension = 1536
            self.available = False
    
    async def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text using Bedrock Titan
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not self.available or not self.bedrock_client:
            print("⚠️ Embeddings service not available, returning dummy embedding")
            # Return a dummy embedding for testing
            return [0.1] * self.embedding_dimension
        
        try:
            # Prepare request for Bedrock Titan Embeddings
            request_body = {
                "inputText": text
            }
            
            # Call Bedrock Titan Embeddings model
            response = self.bedrock_client.invoke_model(
                body=json.dumps(request_body),
                modelId=self.embedding_model,
                accept='application/json',
                contentType='application/json'
            )
            
            # Parse response
            response_body = json.loads(response.get('body').read())
            embedding = response_body.get('embedding', [])
            
            if not embedding:
                raise ValueError("No embedding returned from Bedrock")
                
            return embedding
            
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            # Return zero vector as fallback
            return [0.0] * self.embedding_dimension
    
    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = await self.get_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1, higher = more similar)
        """
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            print(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def find_most_similar(self, query_embedding: List[float], 
                         candidate_embeddings: List[List[float]], 
                         top_k: int = 5) -> List[tuple]:
        """
        Find most similar embeddings to query
        
        Args:
            query_embedding: Query vector
            candidate_embeddings: List of candidate vectors
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples, sorted by similarity
        """
        similarities = []
        
        for i, candidate in enumerate(candidate_embeddings):
            similarity = self.cosine_similarity(query_embedding, candidate)
            similarities.append((i, similarity))
        
        # Sort by similarity (descending) and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

# Global embedding service instance
embedding_service = EmbeddingService()
