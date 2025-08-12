"""
Document Management Service for TrustDesk RAG System
Handles document upload, processing, and indexing for vector search
"""

import os
import json
import hashlib
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import fitz  # PyMuPDF for PDF processing
from docx import Document as DocxDocument
import magic  # For file type detection

from .embeddings import EmbeddingService
from .opensearch_vector import OpenSearchVectorService
from .fallback_vector import FallbackVectorService


class DocumentProcessor:
    """Processes various document formats for vector indexing"""
    
    def __init__(self):
        self.supported_formats = {
            '.txt': self._process_text,
            '.pdf': self._process_pdf,
            '.docx': self._process_docx,
            '.md': self._process_markdown,
            '.json': self._process_json
        }
    
    def process_document(self, file_path: str, metadata: Dict = None) -> Dict[str, Any]:
        """
        Process a document and extract text content
        
        Args:
            file_path: Path to the document file
            metadata: Additional metadata for the document
            
        Returns:
            Dictionary containing processed document data
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Document not found: {file_path}")
            
            # Get file extension
            file_ext = file_path.suffix.lower()
            
            if file_ext not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            # Process the document
            text_content = self.supported_formats[file_ext](file_path)
            
            # Create document metadata
            doc_metadata = {
                'filename': file_path.name,
                'file_path': str(file_path),
                'file_size': file_path.stat().st_size,
                'file_type': file_ext,
                'processed_at': datetime.utcnow().isoformat(),
                'content_hash': hashlib.md5(text_content.encode()).hexdigest(),
                **(metadata or {})
            }
            
            return {
                'content': text_content,
                'metadata': doc_metadata,
                'chunks': self._chunk_text(text_content)
            }
            
        except Exception as e:
            raise Exception(f"Error processing document {file_path}: {str(e)}")
    
    def _process_text(self, file_path: Path) -> str:
        """Process plain text files"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _process_pdf(self, file_path: Path) -> str:
        """Process PDF files using PyMuPDF"""
        try:
            doc = fitz.open(file_path)
            text_content = ""
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text_content += page.get_text()
                text_content += "\n\n"  # Add page break
            
            doc.close()
            return text_content.strip()
        
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def _process_docx(self, file_path: Path) -> str:
        """Process Word documents"""
        try:
            doc = DocxDocument(file_path)
            text_content = ""
            
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
            
            return text_content.strip()
        
        except Exception as e:
            raise Exception(f"Error processing DOCX: {str(e)}")
    
    def _process_markdown(self, file_path: Path) -> str:
        """Process Markdown files"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _process_json(self, file_path: Path) -> str:
        """Process JSON files by extracting text values"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            def extract_text(obj):
                if isinstance(obj, str):
                    return obj
                elif isinstance(obj, dict):
                    return " ".join([extract_text(v) for v in obj.values()])
                elif isinstance(obj, list):
                    return " ".join([extract_text(item) for item in obj])
                else:
                    return str(obj)
            
            return extract_text(data)
        
        except Exception as e:
            raise Exception(f"Error processing JSON: {str(e)}")
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks for better vector search
        
        Args:
            text: Input text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Characters to overlap between chunks
            
        Returns:
            List of text chunks with metadata
        """
        if len(text) <= chunk_size:
            return [{
                'chunk_id': 0,
                'content': text,
                'start_pos': 0,
                'end_pos': len(text),
                'size': len(text)
            }]
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end - 1, start + chunk_size // 2, -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk_content = text[start:end].strip()
            
            if chunk_content:
                chunks.append({
                    'chunk_id': chunk_id,
                    'content': chunk_content,
                    'start_pos': start,
                    'end_pos': end,
                    'size': len(chunk_content)
                })
                chunk_id += 1
            
            # Move start position with overlap
            start = max(start + chunk_size - overlap, end)
        
        return chunks


class DocumentManager:
    """Manages document upload, processing, and indexing"""
    
    def __init__(self, vector_db_type: str = "opensearch"):
        self.processor = DocumentProcessor()
        self.embedding_service = EmbeddingService()
        self.vector_db_type = vector_db_type
        
        # Initialize vector database based on type
        if vector_db_type == "opensearch":
            try:
                self.vector_service = OpenSearchVectorService()
                # Check if OpenSearch is properly configured
                if not self.vector_service.client:
                    print("⚠️ OpenSearch not configured, using fallback vector service")
                    self.vector_service = FallbackVectorService()
                    self.vector_db_type = "fallback"
            except Exception as e:
                print(f"⚠️ OpenSearch initialization failed: {e}, using fallback")
                self.vector_service = FallbackVectorService()
                self.vector_db_type = "fallback"
        elif vector_db_type == "bedrock_kb":
            self.s3_client = boto3.client('s3')
            self.bedrock_client = boto3.client('bedrock-agent')
        else:
            # Default to fallback for testing
            self.vector_service = FallbackVectorService()
            self.vector_db_type = "fallback"
        
        # Document storage path
        self.storage_path = Path("knowledge_base_storage")
        self.storage_path.mkdir(exist_ok=True)
    
    async def upload_document(self, file_path: str, metadata: Dict = None) -> Dict[str, Any]:
        """
        Upload and process a document for the knowledge base
        
        Args:
            file_path: Path to the document file
            metadata: Additional metadata for the document
            
        Returns:
            Upload result with document ID and status
        """
        try:
            # Process the document
            processed_doc = self.processor.process_document(file_path, metadata)
            
            # Generate document ID
            doc_id = hashlib.sha256(
                f"{processed_doc['metadata']['filename']}{processed_doc['metadata']['content_hash']}".encode()
            ).hexdigest()[:16]
            
            # Store document locally
            doc_storage_path = self.storage_path / f"{doc_id}.json"
            with open(doc_storage_path, 'w', encoding='utf-8') as f:
                json.dump(processed_doc, f, indent=2, ensure_ascii=False)
            
            # Index document based on vector DB type
            if self.vector_db_type == "opensearch":
                await self._index_to_opensearch(doc_id, processed_doc)
            elif self.vector_db_type == "bedrock_kb":
                await self._upload_to_bedrock_kb(doc_id, processed_doc)
            elif self.vector_db_type == "fallback":
                await self._index_to_fallback(doc_id, processed_doc)
            
            return {
                'document_id': doc_id,
                'status': 'uploaded',
                'filename': processed_doc['metadata']['filename'],
                'chunks_created': len(processed_doc['chunks']),
                'file_size': processed_doc['metadata']['file_size'],
                'processed_at': processed_doc['metadata']['processed_at']
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _index_to_opensearch(self, doc_id: str, processed_doc: Dict[str, Any]):
        """Index document chunks to OpenSearch"""
        try:
            for chunk in processed_doc['chunks']:
                # Generate embedding for chunk
                embedding = await self.embedding_service.get_embedding(chunk['content'])
                
                # Create document for indexing
                doc_for_index = {
                    'document_id': doc_id,
                    'chunk_id': chunk['chunk_id'],
                    'content': chunk['content'],
                    'embedding': embedding,
                    'metadata': {
                        **processed_doc['metadata'],
                        'chunk_size': chunk['size'],
                        'start_pos': chunk['start_pos'],
                        'end_pos': chunk['end_pos']
                    }
                }
                
                # Index to OpenSearch with clean ID
                import uuid
                clean_doc_id = str(uuid.uuid4())
                await self.vector_service.index_document(
                    doc_id=clean_doc_id,
                    content=chunk['content'],
                    embedding=embedding,
                    metadata={
                        **doc_for_index['metadata'],
                        'original_doc_id': doc_id,
                        'chunk_id': chunk['chunk_id']
                    }
                )
            
        except Exception as e:
            raise Exception(f"Error indexing to OpenSearch: {str(e)}")
    
    async def _upload_to_bedrock_kb(self, doc_id: str, processed_doc: Dict[str, Any]):
        """Upload document to S3 for Bedrock Knowledge Base"""
        try:
            bucket_name = os.getenv('S3_BUCKET_NAME')
            if not bucket_name:
                raise ValueError("S3_BUCKET_NAME not configured")
            
            # Upload original document to S3
            s3_key = f"knowledge-base/{doc_id}/{processed_doc['metadata']['filename']}"
            
            with open(processed_doc['metadata']['file_path'], 'rb') as f:
                self.s3_client.upload_fileobj(
                    f, bucket_name, s3_key,
                    ExtraArgs={
                        'Metadata': {
                            'document-id': doc_id,
                            'processed-at': processed_doc['metadata']['processed_at'],
                            'content-hash': processed_doc['metadata']['content_hash']
                        }
                    }
                )
            
            # Trigger Bedrock Knowledge Base sync (if configured)
            knowledge_base_id = os.getenv('BEDROCK_KNOWLEDGE_BASE_ID')
            data_source_id = os.getenv('BEDROCK_DATA_SOURCE_ID')
            
            if knowledge_base_id and data_source_id:
                self.bedrock_client.start_ingestion_job(
                    knowledgeBaseId=knowledge_base_id,
                    dataSourceId=data_source_id
                )
            
        except Exception as e:
            raise Exception(f"Error uploading to Bedrock KB: {str(e)}")
    
    async def _index_to_fallback(self, doc_id: str, processed_doc: Dict[str, Any]):
        """Index document chunks to fallback vector service"""
        try:
            for chunk in processed_doc['chunks']:
                # Try to generate embedding for chunk, fallback to simple storage if fails
                try:
                    embedding = await self.embedding_service.get_embedding(chunk['content'])
                except Exception as e:
                    print(f"Warning: Could not generate embedding: {e}, using content-only indexing")
                    embedding = [0.0] * 1536  # Dummy embedding
                
                # Index to fallback service
                await self.vector_service.index_document(
                    doc_id=f"{doc_id}_{chunk['chunk_id']}",
                    content=chunk['content'],
                    embedding=embedding,
                    metadata={
                        **processed_doc['metadata'],
                        'chunk_size': chunk['size'],
                        'start_pos': chunk['start_pos'],
                        'end_pos': chunk['end_pos']
                    }
                )
            
        except Exception as e:
            raise Exception(f"Error indexing to fallback service: {str(e)}")
    
    async def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents using vector similarity
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of relevant document chunks
        """
        try:
            if self.vector_db_type == "opensearch":
                return await self.vector_service.search_knowledge(query, limit)
            elif self.vector_db_type == "bedrock_kb":
                return await self._search_bedrock_kb(query, limit)
            elif self.vector_db_type == "fallback":
                return await self.vector_service.vector_search(query, limit)
            else:
                raise ValueError(f"Unsupported vector DB type: {self.vector_db_type}")
                
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            return []
    
    async def _search_bedrock_kb(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search using Bedrock Knowledge Base"""
        try:
            knowledge_base_id = os.getenv('BEDROCK_KNOWLEDGE_BASE_ID')
            if not knowledge_base_id:
                raise ValueError("BEDROCK_KNOWLEDGE_BASE_ID not configured")
            
            response = self.bedrock_client.retrieve(
                knowledgeBaseId=knowledge_base_id,
                retrievalQuery={'text': query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': limit
                    }
                }
            )
            
            results = []
            for item in response.get('retrievalResults', []):
                results.append({
                    'content': item['content']['text'],
                    'score': item.get('score', 0.0),
                    'metadata': item.get('metadata', {}),
                    'location': item.get('location', {})
                })
            
            return results
            
        except Exception as e:
            raise Exception(f"Error searching Bedrock KB: {str(e)}")
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all uploaded documents"""
        try:
            documents = []
            for doc_file in self.storage_path.glob("*.json"):
                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        doc_data = json.load(f)
                    
                    documents.append({
                        'document_id': doc_file.stem,
                        'filename': doc_data['metadata']['filename'],
                        'file_size': doc_data['metadata']['file_size'],
                        'file_type': doc_data['metadata']['file_type'],
                        'processed_at': doc_data['metadata']['processed_at'],
                        'chunks_count': len(doc_data['chunks'])
                    })
                except Exception as e:
                    print(f"Error reading document {doc_file}: {str(e)}")
                    continue
            
            return sorted(documents, key=lambda x: x['processed_at'], reverse=True)
            
        except Exception as e:
            print(f"Error listing documents: {str(e)}")
            return []
    
    async def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete a document from the knowledge base"""
        try:
            # Remove from local storage
            doc_file = self.storage_path / f"{document_id}.json"
            if doc_file.exists():
                doc_file.unlink()
            
            # Remove from vector database
            if self.vector_db_type == "opensearch":
                await self.vector_service.delete_document(document_id)
            elif self.vector_db_type == "bedrock_kb":
                # For Bedrock KB, would need to remove from S3 and sync
                pass
            
            return {
                'status': 'deleted',
                'document_id': document_id
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_document_manager():
        """Test the document management system"""
        
        # Initialize document manager
        doc_manager = DocumentManager(vector_db_type="opensearch")
        
        # Test document upload
        sample_docs = [
            "sample_documents/trustdesk_faq.txt",
            "sample_documents/support_procedures.txt",
            "sample_documents/product_features.txt"
        ]
        
        for doc_path in sample_docs:
            if os.path.exists(doc_path):
                print(f"\nUploading {doc_path}...")
                result = await doc_manager.upload_document(
                    doc_path,
                    metadata={'category': 'knowledge_base', 'version': '1.0'}
                )
                print(f"Upload result: {result}")
        
        # Test document search
        print("\n" + "="*50)
        print("Testing document search...")
        
        test_queries = [
            "How to reset password?",
            "What are the pricing plans?",
            "Customer support procedures",
            "Integration with CRM systems"
        ]
        
        for query in test_queries:
            print(f"\nSearching for: '{query}'")
            results = await doc_manager.search_documents(query, limit=3)
            
            for i, result in enumerate(results):
                print(f"Result {i+1}: {result['content'][:200]}...")
                print(f"Score: {result.get('score', 'N/A')}")
                print("-" * 30)
        
        # List all documents
        print("\n" + "="*50)
        print("All documents in knowledge base:")
        documents = doc_manager.list_documents()
        for doc in documents:
            print(f"- {doc['filename']} ({doc['chunks_count']} chunks)")
    
    # Run the test
    asyncio.run(test_document_manager())
