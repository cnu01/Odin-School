from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import tempfile
from .models import (
    CommentInput, AnalyzedComment, CommentRequest, AIAnalysisResponse,
    RAGCommentRequest, RAGAnalysisResponse, KnowledgeDocumentInput,
    FAQInput, KnowledgeSearchRequest, KnowledgeSearchResult
)
from .service import TrustdeskService
from .rag_service import rag_service
from .knowledge import knowledge_service
from .document_manager import DocumentManager

router = APIRouter()

# Initialize services
trustdesk_service = TrustdeskService()

# Initialize document manager with vector DB type from environment
vector_db_type = os.getenv('VECTOR_DB_TYPE', 'opensearch')
document_manager = DocumentManager(vector_db_type=vector_db_type)

@router.get("/")
async def trustdesk_home():
    """TrustDesk - Comment/Review Management - Now with RAG and Amazon Bedrock"""
    return {
        "problem": "TrustDesk - Comment/Review Management",
        "description": "Brand safety and response automation with RAG-enhanced AI analysis",
        "status": "Active - Amazon Bedrock Claude-v2 + RAG Integration",
        "version": "3.0.0",
        "ai_provider": "Amazon Bedrock Claude-v2 + Titan Embeddings",
        "features": [
            "Knowledge-informed responses using RAG",
            "Company policy-aware analysis",
            "Historical response learning",
            "FAQ integration",
            "Vector similarity search"
        ],
        "endpoints": {
            "/analyze": "POST - Legacy endpoint: Analyze customer comments (backward compatible)",
            "/analyze-bedrock": "POST - Direct Bedrock analysis",
            "/analyze-rag": "POST - RAG-enhanced analysis with knowledge retrieval",
            "/knowledge": "POST - Add knowledge base documents",
            "/faq": "POST - Add FAQ entries",
            "/search": "POST - Search knowledge base",
            "/stats": "GET - Knowledge base statistics"
        }
    }

@router.post("/analyze", response_model=AnalyzedComment)
async def analyze_comment(comment_input: CommentInput):
    """
    Legacy endpoint: Analyze a customer comment using AI for sentiment, urgency, and response generation
    Now powered by Amazon Bedrock Claude-v2 with backward compatibility
    
    Args:
        comment_input: CommentInput containing the comment text
        
    Returns:
        AnalyzedComment with AI analysis and suggested reply (legacy format)
    """
    try:
        # Process comment with AI analysis (now Bedrock-powered)
        analyzed_comment = await trustdesk_service.analyze_comment(comment_input.comment_text)
        return analyzed_comment
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing comment: {str(e)}"
        )

@router.post("/analyze-bedrock", response_model=AIAnalysisResponse)
async def analyze_comment_bedrock(comment_request: CommentRequest):
    """
    Bedrock endpoint: Analyze a customer comment using Amazon Bedrock Claude-v2 directly
    Returns enhanced structured response format optimized for Bedrock
    
    Args:
        comment_request: CommentRequest containing the comment text to analyze
        
    Returns:
        AIAnalysisResponse with structured Bedrock analysis results
    """
    try:
        # Process comment using Bedrock service directly
        bedrock_analysis = await trustdesk_service.analyze_comment_bedrock(comment_request)
        return bedrock_analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing comment with Bedrock: {str(e)}"
        )

@router.post("/analyze-rag", response_model=RAGAnalysisResponse)
async def analyze_comment_rag(rag_request: RAGCommentRequest):
    """
    RAG endpoint: Analyze a customer comment using RAG (Retrieval-Augmented Generation)
    Combines knowledge base retrieval with Bedrock Claude-v2 generation
    
    Args:
        rag_request: RAGCommentRequest with text and RAG options
        
    Returns:
        RAGAnalysisResponse with knowledge-informed analysis
    """
    try:
        if not rag_request.use_rag:
            # Fall back to regular Bedrock analysis
            regular_request = CommentRequest(text=rag_request.text)
            bedrock_result = await trustdesk_service.analyze_comment_bedrock(regular_request)
            return RAGAnalysisResponse(
                urgency=bedrock_result.urgency,
                is_sensitive=bedrock_result.is_sensitive,
                summary=bedrock_result.summary,
                draft_reply=bedrock_result.draft_reply,
                context_used=False
            )
        
        # Use RAG analysis
        regular_request = CommentRequest(text=rag_request.text)
        rag_result = await rag_service.analyze_comment_with_rag(regular_request)
        
        # Convert to RAG response format with additional metadata
        return RAGAnalysisResponse(
            urgency=rag_result.urgency,
            is_sensitive=rag_result.is_sensitive,
            summary=rag_result.summary,
            draft_reply=rag_result.draft_reply,
            knowledge_sources=["knowledge_base", "faq", "historical_responses"],
            confidence_score=0.95,  # High confidence when using RAG
            context_used=True
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing comment with RAG: {str(e)}"
        )

@router.post("/knowledge")
async def add_knowledge_document(doc_input: KnowledgeDocumentInput):
    """
    Add a new document to the knowledge base
    
    Args:
        doc_input: Knowledge document to add
        
    Returns:
        Success message with document ID
    """
    try:
        from .knowledge import KnowledgeDocument
        
        knowledge_doc = KnowledgeDocument(**doc_input.model_dump())
        doc_id = await knowledge_service.add_knowledge_document(knowledge_doc)
        
        return {
            "success": True,
            "message": "Knowledge document added successfully",
            "document_id": doc_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error adding knowledge document: {str(e)}"
        )

@router.post("/faq")
async def add_faq_document(faq_input: FAQInput):
    """
    Add a new FAQ to the knowledge base
    
    Args:
        faq_input: FAQ to add
        
    Returns:
        Success message with FAQ ID
    """
    try:
        from .knowledge import FAQDocument
        
        faq_doc = FAQDocument(**faq_input.model_dump())
        faq_id = await knowledge_service.add_faq_document(faq_doc)
        
        return {
            "success": True,
            "message": "FAQ added successfully",
            "faq_id": faq_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error adding FAQ: {str(e)}"
        )

@router.post("/search", response_model=List[KnowledgeSearchResult])
async def search_knowledge_base(search_request: KnowledgeSearchRequest):
    """
    Search the knowledge base using vector similarity
    
    Args:
        search_request: Search query and parameters
        
    Returns:
        List of relevant knowledge documents
    """
    try:
        results = await knowledge_service.search_knowledge(
            query=search_request.query,
            top_k=search_request.top_k,
            category=search_request.category
        )
        
        # Convert to response format
        search_results = []
        for result in results:
            search_results.append(KnowledgeSearchResult(
                id=result['id'],
                title=result['title'],
                content=result['content'],
                category=result['category'],
                similarity_score=result['similarity_score'],
                metadata=result.get('metadata', {})
            ))
        
        return search_results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching knowledge base: {str(e)}"
        )

@router.get("/stats")
async def get_knowledge_stats():
    """
    Get statistics about the knowledge base
    
    Returns:
        Knowledge base statistics
    """
    try:
        stats = await rag_service.get_knowledge_stats()
        return {
            "success": True,
            "knowledge_base_stats": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting knowledge stats: {str(e)}"
        )

@router.post("/feedback")
async def submit_response_feedback(comment: str, reply: str, rating: float):
    """
    Submit feedback on a response to improve future RAG results
    
    Args:
        comment: Original customer comment
        reply: Reply that was used
        rating: Effectiveness rating (1-5)
        
    Returns:
        Success message
    """
    try:
        response_id = await rag_service.add_successful_response(
            original_comment=comment,
            reply=reply,
            rating=rating,
            sentiment="neutral"  # Could be detected automatically
        )
        
        return {
            "success": True,
            "message": "Response feedback submitted successfully",
            "response_id": response_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting feedback: {str(e)}"
        )


# ============================================================================
# DOCUMENT MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """
    Upload a document to the knowledge base
    
    Args:
        file: Document file (PDF, DOCX, TXT, MD, JSON)
        category: Document category (optional)
        description: Document description (optional)
        
    Returns:
        Upload result with document ID and processing status
    """
    try:
        # Check file size (max 10MB)
        if file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")
        
        # Check file type
        allowed_extensions = {'.txt', '.pdf', '.docx', '.md', '.json'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Upload and process document
            metadata = {
                'category': category or 'general',
                'description': description or '',
                'original_filename': file.filename,
                'uploaded_by': 'api_user'  # Could be from auth context
            }
            
            result = await document_manager.upload_document(temp_file_path, metadata)
            
            return {
                "success": True,
                "message": "Document uploaded and processed successfully",
                "result": result
            }
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading document: {str(e)}"
        )

@router.get("/documents")
async def list_documents():
    """
    List all documents in the knowledge base
    
    Returns:
        List of documents with metadata
    """
    try:
        documents = document_manager.list_documents()
        
        return {
            "success": True,
            "documents": documents,
            "total_count": len(documents)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing documents: {str(e)}"
        )

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document from the knowledge base
    
    Args:
        document_id: ID of the document to delete
        
    Returns:
        Deletion result
    """
    try:
        result = await document_manager.delete_document(document_id)
        
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            "success": True,
            "message": f"Document {document_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )

@router.post("/documents/search")
async def search_documents(query: str, limit: int = 10):
    """
    Search documents using vector similarity
    
    Args:
        query: Search query
        limit: Maximum number of results (default 10, max 50)
        
    Returns:
        Search results with relevance scores
    """
    try:
        # Limit validation
        if limit > 50:
            limit = 50
        
        results = await document_manager.search_documents(query, limit)
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "total_found": len(results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching documents: {str(e)}"
        )

@router.post("/documents/bulk-upload")
async def bulk_upload_sample_documents():
    """
    Upload all sample documents for testing
    
    Returns:
        Bulk upload results
    """
    try:
        sample_docs_path = "sample_documents"
        
        if not os.path.exists(sample_docs_path):
            raise HTTPException(status_code=404, detail="Sample documents directory not found")
        
        results = []
        
        # Upload each sample document
        for filename in os.listdir(sample_docs_path):
            if filename.endswith(('.txt', '.pdf', '.docx', '.md')):
                file_path = os.path.join(sample_docs_path, filename)
                
                metadata = {
                    'category': 'sample_data',
                    'description': f'Sample document: {filename}',
                    'uploaded_by': 'bulk_upload'
                }
                
                result = await document_manager.upload_document(file_path, metadata)
                results.append({
                    'filename': filename,
                    'result': result
                })
        
        return {
            "success": True,
            "message": f"Bulk upload completed: {len(results)} documents processed",
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in bulk upload: {str(e)}"
        )
