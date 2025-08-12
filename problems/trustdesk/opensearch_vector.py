"""
TrustDesk AWS OpenSearch Vector Service
======================================
Implementation using Amazon OpenSearch Serverless for vector storage and search.
"""

import boto3
import json
import uuid
from typing import List, Dict, Optional, Any
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import os
from dotenv import load_dotenv

load_dotenv()

class OpenSearchVectorService:
    """AWS OpenSearch Serverless vector database service for TrustDesk RAG"""
    
    def __init__(self):
        """Initialize OpenSearch client"""
        self.region = os.getenv('AWS_REGION', 'us-west-2')
        self.collection_endpoint = os.getenv('OPENSEARCH_ENDPOINT')
        
        # Set up AWS authentication  
        if self.collection_endpoint:
            try:
                credentials = boto3.Session().get_credentials()
                self.awsauth = AWS4Auth(
                    credentials.access_key,
                    credentials.secret_key,
                    self.region,
                    'aoss',
                    session_token=credentials.token
                )
                
                # Extract host from endpoint
                host = self.collection_endpoint.replace('https://', '').replace('http://', '')
                
                # OpenSearch client
                self.client = OpenSearch(
                    hosts=[{'host': host, 'port': 443}],
                    http_auth=self.awsauth,
                    use_ssl=True,
                    verify_certs=True,
                    connection_class=RequestsHttpConnection,
                    timeout=60
                )
                
                # Test connection
                try:
                    self.client.cat.indices()
                    print("✅ OpenSearch Serverless connection established")
                    
                    # Test write permissions
                    test_index = "test-connection"
                    try:
                        if not self.client.indices.exists(index=test_index):
                            self.client.indices.create(
                                index=test_index,
                                body={"mappings": {"properties": {"test": {"type": "text"}}}}
                            )
                            self.client.indices.delete(index=test_index)
                            print("✅ Write permissions confirmed")
                            self.has_write_access = True
                    except Exception as e:
                        if "authorization_exception" in str(e).lower():
                            print("⚠️ Connected to OpenSearch but no write permissions.")
                            print("   Admin needs to update data access policy with write permissions:")
                            print("   - aoss:CreateIndex")
                            print("   - aoss:WriteDocument")
                            print("   - aoss:UpdateDocument") 
                            print("   - aoss:DeleteDocument")
                            self.has_write_access = False
                        else:
                            raise e
                        
                except Exception as e:
                    print(f"❌ OpenSearch connection test failed: {e}")
                    self.client = None
                    
            except Exception as e:
                print(f"❌ Failed to setup OpenSearch authentication: {e}")
                self.client = None
        else:
            print("⚠️ OpenSearch endpoint not configured. Set OPENSEARCH_ENDPOINT in .env")
            self.client = None
        
        # Index names
        self.knowledge_index = "trustdesk-knowledge"
        self.faq_index = "trustdesk-faq"
        self.responses_index = "trustdesk-responses"
        
        # Vector dimension (Bedrock Titan)
        self.vector_dimension = 1536
    
    async def initialize_indices(self):
        """Create OpenSearch indices with vector field mappings"""
        if not self.client:
            return False
        
        if not getattr(self, 'has_write_access', False):
            print("⚠️ No write access to OpenSearch. Indices must be created by admin.")
            print("   Provide these mappings to your admin:")
            
            # Print the mappings for admin to create manually
            knowledge_mapping = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "title": {"type": "text", "analyzer": "standard"},
                        "content": {"type": "text", "analyzer": "standard"},
                        "category": {"type": "keyword"},
                        "document_type": {"type": "keyword"},
                        "file_path": {"type": "keyword"},
                        "chunk_id": {"type": "keyword"},
                        "embedding": {
                            "type": "dense_vector",
                            "dims": self.vector_dimension,
                            "index": True,
                            "similarity": "cosine"
                        },
                        "created_at": {"type": "date"},
                        "is_active": {"type": "boolean"}
                    }
                }
            }
            
            print(f"\n📋 Index mapping for {self.knowledge_index}:")
            print(json.dumps(knowledge_mapping, indent=2))
            return False
        
        try:
            # Knowledge base index mapping (updated for OpenSearch Serverless)
            knowledge_mapping = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "title": {"type": "text", "analyzer": "standard"},
                        "content": {"type": "text", "analyzer": "standard"},
                        "category": {"type": "keyword"},
                        "document_type": {"type": "keyword"},
                        "file_path": {"type": "keyword"},
                        "chunk_id": {"type": "keyword"},
                        "embedding": {
                            "type": "dense_vector",
                            "dims": self.vector_dimension,
                            "index": True,
                            "similarity": "cosine"  # OpenSearch Serverless uses cosine
                        },
                        "created_at": {"type": "date"},
                        "is_active": {"type": "boolean"}
                    }
                }
            }
            
            # Create knowledge index
            if not self.client.indices.exists(index=self.knowledge_index):
                self.client.indices.create(index=self.knowledge_index, body=knowledge_mapping)
                print(f"✅ Created OpenSearch index: {self.knowledge_index}")
            else:
                print(f"ℹ️ Index already exists: {self.knowledge_index}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing OpenSearch indices: {str(e)}")
            return False
    
    async def add_knowledge_document(self, doc_data: Dict[str, Any], embedding: List[float]) -> str:
        """Add knowledge document to OpenSearch"""
        if not self.client:
            raise Exception("OpenSearch client not available")
        
        doc_id = doc_data.get('id', str(uuid.uuid4()))
        
        # Prepare document for OpenSearch
        opensearch_doc = {
            "id": doc_id,
            "title": doc_data.get('title', ''),
            "content": doc_data.get('content', ''),
            "category": doc_data.get('category', ''),
            "department": doc_data.get('department', ''),
            "priority": doc_data.get('priority', 1),
            "tags": doc_data.get('tags', []),
            "embedding": embedding,
            "created_at": doc_data.get('created_at'),
            "is_active": doc_data.get('is_active', True)
        }
        
        # Index document
        response = self.client.index(
            index=self.knowledge_index,
            id=doc_id,
            body=opensearch_doc
        )
        
        return doc_id
    
    async def add_faq_document(self, faq_data: Dict[str, Any], embedding: List[float]) -> str:
        """Add FAQ document to OpenSearch"""
        if not self.client:
            raise Exception("OpenSearch client not available")
        
        faq_id = faq_data.get('id', str(uuid.uuid4()))
        
        opensearch_doc = {
            "id": faq_id,
            "question": faq_data.get('question', ''),
            "answer": faq_data.get('answer', ''),
            "category": faq_data.get('category', ''),
            "keywords": faq_data.get('keywords', []),
            "embedding": embedding,
            "usage_count": faq_data.get('usage_count', 0),
            "effectiveness_rating": faq_data.get('effectiveness_rating', 0.0),
            "created_at": faq_data.get('created_at'),
            "is_active": faq_data.get('is_active', True)
        }
        
        response = self.client.index(
            index=self.faq_index,
            id=faq_id,
            body=opensearch_doc
        )
        
        return faq_id
    
    async def ensure_indices_exist(self) -> bool:
        """Ensure required indices exist in OpenSearch"""
        if not self.client:
            return False
        
        try:
            # Check knowledge index
            if not self.client.indices.exists(index=self.knowledge_index):
                print(f"📝 Creating knowledge index: {self.knowledge_index}")
                await self._create_indices()
            
            # Check FAQ index  
            if not self.client.indices.exists(index=self.faq_index):
                print(f"📝 Creating FAQ index: {self.faq_index}")
                await self._create_indices()
            
            return True
        except Exception as e:
            print(f"❌ Error ensuring indices exist: {e}")
            return False

    async def index_document(self, doc_id: str, content: str, embedding: List[float], 
                           metadata: Dict[str, Any] = None) -> bool:
        """
        Index a document with its embedding for vector search
        Generic method that can be used by document manager
        """
        if not self.client:
            print("❌ OpenSearch client not available")
            return False
        
        # Ensure indices exist
        await self.ensure_indices_exist()
        
        if not getattr(self, 'has_write_access', False):
            print("⚠️ No write access to OpenSearch. Document indexing skipped.")
            print(f"   Document would be indexed: {doc_id}")
            print(f"   Content preview: {content[:100]}...")
            return False
        
        try:
            # Prepare document for indexing
            doc_body = {
                "content": content,
                "title": metadata.get('filename', '') if metadata else '',
                "document_type": metadata.get('document_type', 'knowledge') if metadata else 'knowledge',
                "file_path": metadata.get('file_path', '') if metadata else '',
                "chunk_id": doc_id,
                "embedding": embedding,
                "created_at": metadata.get('processed_at') if metadata else None,
                "is_active": True
            }
            
            # Index to knowledge base
            response = self.client.index(
                index=self.knowledge_index,
                id=doc_id,
                body=doc_body
            )
            
            success = response.get('result') in ['created', 'updated']
            if success:
                print(f"✅ Document indexed: {doc_id}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error indexing document {doc_id}: {str(e)}")
            return False
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its chunks from the vector database"""
        if not self.client:
            return False
        
        try:
            # Delete from knowledge index (supports wildcards for chunks)
            delete_query = {
                "query": {
                    "wildcard": {
                        "id": f"{document_id}*"
                    }
                }
            }
            
            response = self.client.delete_by_query(
                index=self.knowledge_index,
                body=delete_query
            )
            
            return response.get('deleted', 0) > 0
            
        except Exception as e:
            print(f"Error deleting document {document_id}: {str(e)}")
            return False

    async def search_knowledge(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search knowledge base using text query (generates embedding first)
        Compatible with document manager interface
        """
        if not self.client:
            return []
        
        try:
            # First, ensure indices exist
            await self.ensure_indices_exist()
            
            # Generate embedding for the query
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from embeddings import EmbeddingService
            embedding_service = EmbeddingService()
            query_embedding = await embedding_service.get_embedding(query)
            
            # Perform vector search
            return await self.vector_search(
                index_name=self.knowledge_index,
                query_embedding=query_embedding,
                top_k=limit
            )
            
        except Exception as e:
            print(f"❌ Error in knowledge search: {e}")
            return []

    async def vector_search(self, index_name: str, query_embedding: List[float], 
                           top_k: int = 5, filters: Optional[Dict] = None) -> List[Dict]:
        """Perform vector similarity search in OpenSearch Serverless"""
        if not self.client:
            return []
        
        # Check if index exists
        try:
            if not self.client.indices.exists(index=index_name):
                print(f"⚠️ Index {index_name} does not exist")
                return []
        except Exception as e:
            print(f"❌ Error checking index existence: {e}")
            return []
        
        # Build query for OpenSearch Serverless dense_vector search
        search_query = {
            "size": top_k,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": query_embedding}
                    }
                }
            },
            "_source": {
                "excludes": ["embedding"]  # Don't return large embedding vectors
            }
        }
        
        # Add filters if provided
        if filters:
            bool_query = {"bool": {"must": [], "filter": []}}
            bool_query["bool"]["must"].append(search_query["query"])
            
            for field, value in filters.items():
                if isinstance(value, list):
                    bool_query["bool"]["filter"].append({"terms": {field: value}})
                else:
                    bool_query["bool"]["filter"].append({"term": {field: value}})
            
            search_query["query"] = bool_query
        
        try:
            response = self.client.search(index=index_name, body=search_query)
            
            results = []
            for hit in response['hits']['hits']:
                result = hit['_source']
                result['similarity_score'] = hit['_score']
                result['document_id'] = hit['_id']
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ Vector search error in {index_name}: {str(e)}")
            return []
    
    async def search_knowledge(self, query_embedding: List[float], top_k: int = 5, 
                              category: Optional[str] = None) -> List[Dict]:
        """Search knowledge base using vector similarity"""
        filters = {"is_active": True}
        if category:
            filters["category"] = category
        
        return await self.vector_search(
            self.knowledge_index, query_embedding, top_k, filters
        )
    
    async def search_faq(self, query_embedding: List[float], top_k: int = 3) -> List[Dict]:
        """Search FAQ using vector similarity"""
        filters = {"is_active": True}
        
        return await self.vector_search(
            self.faq_index, query_embedding, top_k, filters
        )
    
    async def search_responses(self, query_embedding: List[float], top_k: int = 3) -> List[Dict]:
        """Search historical responses using vector similarity"""
        filters = {"is_effective": True}
        
        return await self.vector_search(
            self.responses_index, query_embedding, top_k, filters
        )
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get OpenSearch index statistics"""
        if not self.client:
            return {}
        
        try:
            stats = {}
            
            for index_name in [self.knowledge_index, self.faq_index, self.responses_index]:
                if self.client.indices.exists(index=index_name):
                    index_stats = self.client.indices.stats(index=index_name)
                    doc_count = index_stats['indices'][index_name]['total']['docs']['count']
                    stats[index_name] = {
                        "document_count": doc_count,
                        "index_size": index_stats['indices'][index_name]['total']['store']['size_in_bytes']
                    }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting statistics: {str(e)}")
            return {}

# Global OpenSearch service instance
opensearch_service = OpenSearchVectorService()
