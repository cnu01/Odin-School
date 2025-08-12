# TrustDesk Frontend-Backend Integration

## 🎯 Overview

This document describes the complete integration between the TrustDesk React frontend and FastAPI backend, enabling AI-powered brand reputation management with RAG (Retrieval-Augmented Generation) capabilities.

## 🏗️ Architecture

### Frontend (React)
- **Location**: `frontend/src/pages/BrandReputation/`
- **Service Layer**: `frontend/src/services/trustdeskService.js`
- **API Client**: `frontend/src/services/api.js`

### Backend (FastAPI)
- **Location**: `problems/trustdesk/`
- **Main Router**: `routes.py`
- **Service Layer**: `service.py`
- **RAG Service**: `rag_service.py`
- **Models**: `models.py`

## 🔗 Integration Points

### 1. Comment Analysis
**Frontend → Backend Flow:**
```javascript
// Frontend: User clicks "AI Reply" button
trustdeskService.analyzeComment(commentData)
  ↓
// API call to backend
POST /api/trustdesk/analyze-rag
  ↓
// Backend: RAG-enhanced analysis
rag_service.analyze_comment_with_rag()
  ↓
// Returns: urgency, sentiment, AI-generated response
```

### 2. Response Generation
**AI-Powered Reply Generation:**
```javascript
// Frontend: Generate intelligent response
trustdeskService.generateResponse(commentText, category)
  ↓
// Backend: Uses Amazon Bedrock Claude-v2
bedrock_client.invoke_model('anthropic.claude-v2')
  ↓
// Returns: contextual, brand-safe response
```

### 3. Knowledge Base Integration
**RAG Enhancement:**
```javascript
// Frontend: Search knowledge base
trustdeskService.searchKnowledge(query)
  ↓
// Backend: Vector similarity search
knowledge_service.search_knowledge()
  ↓
// Returns: relevant company policies, FAQs
```

## 📡 API Endpoints

### Core Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/trustdesk/analyze-rag` | RAG-enhanced comment analysis |
| `POST` | `/api/trustdesk/analyze-bedrock` | Direct Bedrock analysis |
| `POST` | `/api/trustdesk/analyze` | Legacy endpoint (backward compatible) |
| `POST` | `/api/trustdesk/feedback` | Submit response effectiveness feedback |
| `POST` | `/api/trustdesk/search` | Search knowledge base |
| `GET` | `/api/trustdesk/stats` | Get knowledge base statistics |

### Request/Response Examples

#### Analyze Comment with RAG
```json
// Request
POST /api/trustdesk/analyze-rag
{
  "text": "The course content seems outdated. React 18 features are missing.",
  "use_rag": true,
  "include_context": true
}

// Response
{
  "urgency": "High",
  "is_sensitive": true,
  "summary": "Negative feedback about outdated course content and missing modern features.",
  "draft_reply": "Thank you for your feedback. We take all concerns seriously and are constantly updating our curriculum...",
  "knowledge_sources": ["course_policies", "curriculum_updates"],
  "confidence_score": 0.92,
  "context_used": true
}
```

## 🎨 Frontend Components

### BrandReputation.js - Main Features
1. **Real-time Comment Loading**: Fetches comments via API with filtering
2. **AI Analysis Integration**: Click-to-analyze comments with Bedrock
3. **Smart Reply Generation**: AI-powered response suggestions
4. **Loading States**: Smooth UX with progress indicators
5. **Error Handling**: Graceful fallbacks and user notifications
6. **Real-time Updates**: Updates comment status after responses

### Key UI/UX Improvements
- **AI Confidence Scores**: Shows analysis confidence percentage
- **Knowledge Source Indicators**: Displays which knowledge was used
- **Sensitive Content Warnings**: Highlights sensitive comments
- **Brand Voice Validation**: Ensures responses match company tone
- **Quick Templates**: Fallback templates when AI fails

## 🔧 Configuration

### Environment Variables
```bash
# Frontend (.env)
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENABLE_RAG=true
REACT_APP_ENABLE_MOCK_DATA=false

# Backend (.env)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
VECTOR_DB_TYPE=opensearch
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### API Service Configuration
```javascript
// frontend/src/services/api.js
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
});
```

## 🚀 Running the Integration

### Quick Start
```bash
# Run integration test and start servers
./start_trustdesk_integration.bat
```

### Manual Start
```bash
# Terminal 1: Start backend
uvicorn main:app --reload --port 8000

# Terminal 2: Start frontend  
cd frontend
npm start

# Access application
# Frontend: http://localhost:3000/reputation
# Backend API: http://localhost:8000/docs
```

## 🧪 Testing the Integration

### 1. Functional Testing
- Navigate to `http://localhost:3000/reputation`
- Click any comment to open reply dialog
- Click "AI Reply" to test RAG integration
- Verify AI-generated responses appear
- Check browser network tab for API calls

### 2. Backend API Testing
```bash
# Run integration test
python test_trustdesk_integration.py

# Test specific endpoint
curl -X POST "http://localhost:8000/api/trustdesk/analyze-rag" \
  -H "Content-Type: application/json" \
  -d '{"text":"Great course!", "use_rag":true}'
```

### 3. Error Handling Testing
- Stop backend server and test frontend graceful degradation
- Test with invalid API keys (should show fallback responses)
- Test with network timeouts (should show retry options)

## 📊 Data Flow

### Comment Analysis Workflow
```
User Comment → Frontend BrandReputation Component
    ↓
API Service Layer (trustdeskService.js)
    ↓
HTTP Request to Backend (/api/trustdesk/analyze-rag)
    ↓
FastAPI Router (routes.py)
    ↓
TrustDesk Service (service.py)
    ↓
RAG Service (rag_service.py) + Bedrock Claude-v2
    ↓
Vector Knowledge Search + AI Generation
    ↓
Structured Response (urgency, sentiment, reply)
    ↓
Frontend Updates UI with AI Analysis
```

### State Management Flow
```javascript
// Frontend state updates
commentsData → API call → loading state → success/error → UI update
```

## 🔄 Real-time Features

### Auto-refresh Comments
- Polls for new comments every 30 seconds
- Updates comment status after responses sent
- Maintains filter and tab state during updates

### Live Analysis Feedback
- Shows AI confidence scores in real-time
- Indicates when knowledge base is used
- Provides immediate error feedback

## 🛡️ Error Handling

### Frontend Error Handling
```javascript
// Graceful degradation
if (result.success) {
  // Use AI response
  setDraftReply(result.data.draft_reply);
} else {
  // Fallback to templates
  setDraftReply(fallbackTemplate);
  showSnackbar('Using fallback response', 'warning');
}
```

### Backend Error Handling
```python
# Service layer error handling
try:
    return await rag_service.analyze_comment_with_rag(request)
except Exception as e:
    # Return fallback response
    return AIAnalysisResponse(
        urgency="Medium",
        is_sensitive=False,
        summary="Manual review required",
        draft_reply="Thank you for your feedback..."
    )
```

## 📈 Performance Optimizations

### Frontend Optimizations
- **Debounced Filtering**: Prevents excessive API calls
- **Lazy Loading**: Loads comments on demand
- **Caching**: Stores analysis results locally
- **Optimistic Updates**: Updates UI before API confirmation

### Backend Optimizations
- **Connection Pooling**: Reuses Bedrock connections
- **Response Caching**: Caches similar comment analyses
- **Async Processing**: Non-blocking API calls
- **Rate Limiting**: Prevents API abuse

## 🎯 Success Metrics

### Integration Health Indicators
✅ Frontend loads without errors  
✅ API calls complete successfully  
✅ AI responses generated correctly  
✅ Error handling works gracefully  
✅ Loading states provide good UX  
✅ Real-time updates function properly  

### User Experience Metrics
- **Response Time**: AI replies generated in < 3 seconds
- **Accuracy**: 90%+ relevant responses
- **Uptime**: 99%+ API availability
- **Error Rate**: < 1% failed requests

## 🚀 Next Steps

### Planned Enhancements
1. **Real-time WebSocket Updates**: Live comment streaming
2. **Advanced Analytics**: Response effectiveness tracking
3. **Multi-language Support**: International brand management
4. **Automated Escalation**: Critical issue routing
5. **Custom AI Training**: Brand-specific model fine-tuning

### Deployment Considerations
1. **Production Environment Variables**: Secure API keys
2. **CORS Configuration**: Proper domain allowlisting
3. **Rate Limiting**: API usage controls
4. **Monitoring**: Application performance tracking
5. **Backup Strategy**: Data persistence and recovery

---

## 🎉 Integration Complete!

The TrustDesk frontend and backend are now fully integrated with:
- ✅ AI-powered comment analysis
- ✅ RAG-enhanced response generation  
- ✅ Real-time UI updates
- ✅ Comprehensive error handling
- ✅ Professional user experience

Ready for production deployment! 🚀
