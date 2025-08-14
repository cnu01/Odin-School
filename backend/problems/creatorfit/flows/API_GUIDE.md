# CreatorFit FastAPI Backend

Simple FastAPI backend for CreatorFit influencer marketing analysis.

## 🚀 Quick Start

### Step 1: Start Backend (FastAPI Server)
```bash
# From project root directory
uvicorn main:app --reload
```
✅ Server will run on: http://localhost:8000

### Step 2: Start Frontend (HTTP Server)
```bash
# Open new terminal, go to frontend directory
cd problems/creatorfit/frontend
python -m http.server 8001
```
✅ Frontend will run on: http://localhost:8001

### Step 3: Open & Use
- **Frontend UI**: http://localhost:8001
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/api/creatorfit/health

## 📋 Complete Usage Flow

1. **Start both servers** (steps above)
2. **Open frontend**: http://localhost:8001
3. **Upload CSV file** with creator data
4. **Select program type** (Data Science, Web Development, etc.)
5. **Click "Run Production Analysis"**
6. **Get results**: Rankings, fit scores, lead predictions

## 📡 API Endpoints

### 1. **CSV Analysis** - Main Feature
```http
POST /api/creatorfit/analyze
```

**What it does**: Upload CSV file → Get creator rankings with fit scores and lead predictions

**Parameters**:
- `file`: CSV file with creator data
- `program_type`: data_science | web_development | digital_marketing | ai_ml
- `campaign_budget`: Budget for CPL calculation (default: 100000)

**Example using curl**:
```bash
curl -X POST "http://localhost:8000/api/creatorfit/analyze" \
     -F "file=@sample_creators.csv" \
     -F "program_type=data_science" \
     -F "campaign_budget=100000"
```

**Response**: JSON with creator rankings, fit scores, business metrics, and recommendations

### 2. **Lead Forecasting**
```http
POST /api/creatorfit/forecast
```

**What it does**: Send creator data → Get lead predictions before booking

**Example**:
```bash
curl -X POST "http://localhost:8000/api/creatorfit/forecast?program_type=data_science" \
     -H "Content-Type: application/json" \
     -d '{
       "creator_id": "creator_001",
       "topic": "Python Programming",
       "recent_video_transcript": "Python tutorial content...",
       "posting_cadence_days": 3,
       "views_90d": 150000,
       "language": "English",
       "category_tag": "Education"
     }'
```

### 3. **Other Endpoints**
- `GET /api/creatorfit/` - Service info
- `GET /api/creatorfit/programs` - Available program types
- `GET /api/creatorfit/health` - Health check

## 🧪 Testing

Run the test script:
```bash
cd problems/creatorfit
python test_api.py
```

## 📊 Expected CSV Format

Your CSV should have these columns:
```csv
creator_id,topic,recent_video_transcript,posting_cadence_days,views_90d,language,geography,category_tag
creator_001,"Python Programming","Tutorial content...",3,150000,"English","INDIA","Education"
```

## 🔄 Integration with ML Pipeline

The backend automatically integrates with your existing ML pipeline:
- Uses `frontend/prediction_pipeline.py`
- Loads trained models from `models/` directory
- Applies data preprocessing and feature engineering
- Returns production-ready predictions

## 🗄️ No Database Required

- **File-based**: Everything runs from trained models in `/models/` directory
- **Lightweight**: Just upload CSV and get instant results

## 🎯 Key Features

1. **CSV Upload & Analysis** - Core functionality
2. **Lead Forecasting** - Predict leads before booking creators
3. **Fit Scoring** - Semantic similarity between creator content and programs
4. **Business Intelligence** - CPL, ROI, creator rankings
5. **Simple Integration** - Uses existing ML pipeline

## 🚨 Troubleshooting

### Common Issues & Solutions

**❌ "Cannot connect to FastAPI server"**
```bash
# Solution: Start the backend server
uvicorn main:app --reload
```

**❌ "Frontend not loading"**
```bash
# Solution: Start HTTP server for frontend
cd problems/creatorfit/frontend
python -m http.server 8001
```

**❌ "ML pipeline not available"**
```bash
# Solution: Check if trained models exist
ls models/
# Should show: creatorfit_lgb_model.pkl, creatorfit_preprocessor.pkl, creatorfit_metadata.pkl
```
