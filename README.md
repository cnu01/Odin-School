# 🎯 Odin School - EdTech Solutions Backend

FastAPI backend for 9 AI-driven EdTech solutions. Ready for 24-hour development sprint.

## 🚀 Quick Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the application
fastapi dev main.py
# OR using uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 Prerequisites Checklist

### ✅ What You Have
- [x] Python 3.11+ ✅ (You have 3.11.13)
- [x] Project structure ✅
- [x] Environment configuration ✅

### ⚠️ What You Need to Install
- [ ] **Virtual Environment** - Run: `python3 -m venv venv && source venv/bin/activate`
- [ ] **FastAPI & dependencies** - Run: `pip install -r requirements.txt`
- [ ] **MongoDB** (Optional - for persistence)
  - Local: `brew install mongodb-community` (macOS)
  - Or use MongoDB Atlas (cloud)
  - App can start without MongoDB; database-dependent endpoints will fail until MongoDB is reachable. The app logs a warning instead of crashing.

## 🌐 API Access

Once running:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **API Base**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

## 🎯 9 Problems Structure

```
problems/
├── hotlead/      # Sales Lead Scoring & Prioritization
├── creatorfit/   # Influencer Marketing Optimization  
├── trustdesk/    # Comment/Review Management
├── adlift/       # Marketing Campaign Optimization
├── refermore/    # Referral System Enhancement
├── pricesense/   # Pricing & Payment Optimization
├── firsttouch/   # Sales Automation & First Contact
├── onetruth/     # Marketing Analytics Dashboard
└── closemore/    # Sales Conversation Analysis
```

Each problem folder contains:
- `models.py` - Data schemas
- `routes.py` - API endpoints  
- `service.py` - Business logic
- `__init__.py` - Problem description

## 🛠️ Development

### For Each Problem
1. Go to: `problems/{problem_name}/`
2. Define models in `models.py`
3. Create API endpoints in `routes.py`
4. Add business logic in `service.py`

### Team Development
- Each developer works on their problem folder
- No conflicts between problems
- Independent deployment possible

## ⚙️ Configuration

Environment variables in `.env`:
```bash
MONGODB_URL=mongodb://localhost:27017  # Your MongoDB connection
DATABASE_NAME=odin_school_db           # Database name
DEBUG=true                             # Development mode
API_HOST=0.0.0.0                       # Server host
API_PORT=8000                          # Server port
CORS_ORIGINS=http://localhost:8000,http://localhost:8001  # Comma-separated list; use '*' only if allow-credentials=false
```

## 🔧 Troubleshooting

### Common Issues
1. **Module not found errors**: Run `pip install -r requirements.txt`
2. **MongoDB unreachable**: App starts and logs a warning; DB-using routes will fail until it’s reachable. Install MongoDB or update MONGODB_URL.
3. **Port already in use**: Change API_PORT in .env
4. **CORS with credentials**: If you need cookies/Authorization headers, set explicit origins in CORS_ORIGINS (don’t use '*').
5. **FastAPI command not found**: Use `uvicorn main:app --reload` instead

### Testing Installation
```bash
# Activate virtual environment first
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Test Python imports
python -c "import fastapi, uvicorn; print('FastAPI Ready!')"

# Test app startup (dry run)
python -c "from main import app; print('App loads successfully!')"
```

## 🚀 Ready to Start!

Your backend is configured and ready. Each problem can be developed independently by different team members without conflicts!
