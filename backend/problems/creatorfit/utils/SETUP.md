# CreatorFit - Influencer Marketing ML Pipeline Setup Guide

## 🎯 Overview
CreatorFit is an AI-powered influencer marketing optimization tool for Odin School that uses LightGBM regression to predict qualified leads and score creator-program fit with **85.5% accuracy**.

## 🚀 Quick Start (5 minutes)
1. **Activate virtual environment**: `.venv\Scripts\activate`
2. **Train the model**: `python -m problems.creatorfit.train`
3. **Test predictions**: `python problems/creatorfit/frontend/process_csv.py sample_creators.csv data_science`
4. **Start frontend server**: `cd problems/creatorfit/frontend && python -m http.server 8000`
5. **Open frontend**: Navigate to `http://localhost:8000` in browser
6. **Upload CSV**: Select program and upload your creator dataset
7. **View results**: See Phase 3 ML pipeline results in beautiful table format

**Note**: Replace `data_science` with any program type: `web_development`, `python_programming`, or `career_guidance`

---

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8+ (3.9+ recommended)
- **OS**: Windows 10/11, macOS, or Linux
- **Memory**: 4GB+ RAM (8GB+ for large datasets)
- **Storage**: 2GB+ free space

### Dependencies
All required packages are listed in `requirements.txt`:
```bash
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.5.1
lightgbm==4.1.0
sentence-transformers==2.2.2
joblib==1.3.2
```

---

## 🔧 Installation & Setup

### 1. Virtual Environment Setup
```bash
# Navigate to project root
cd Odin-School

# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Installation
```bash
python -c "import pandas, numpy, sklearn, lightgbm, sentence_transformers; print('✅ All packages installed successfully')"
```

---

## 🎓 Model Training Process

### Phase 1: Data Generation (Optional)
If you need to create a new dataset:
```bash
# Generate synthetic EdTech creator dataset
python create_edtech_dataset.py

# This creates:
# - creator_campaign_audience_EDTECH.csv (raw data)
# - creator_campaign_audience_EDTECH.cleaned.csv (cleaned data)
```

### Phase 2: Model Training
```bash
# Train the LightGBM model with full pipeline
python -m problems.creatorfit.train

# This will:
# 1. Load and clean the dataset
# 2. Engineer 16 features (12 numeric + 4 categorical)
# 3. Train LightGBM regressor with Poisson objective
# 4. Save model artifacts to models/ directory
# 5. Display training metrics (R², MAE, RMSE, MAPE)
```

**Expected Output:**
```
✅ Data preprocessing complete. Fixed 407 issues.
📊 Clean dataset shape: (1500, 13)
🔧 Feature engineering complete. Built 16 features.
🤖 Model training complete: LightGBM
📊 Model performance: R² = 0.855
💾 Model saved to: models/creatorfit_lgb_model.pkl
```

### Phase 3: Prediction Pipeline
```bash
# Process new creator data for predictions
python problems/creatorfit/frontend/process_csv.py your_creators.csv PROGRAM_TYPE

# Available PROGRAM_TYPE values:
# - data_science      (Data Science Program)
# - web_development   (Web Development Program)  
# - python_programming (Python Programming Course)
# - career_guidance   (Career Guidance & Interview Prep)

# This creates:
# - your_creators_results.json (full ML pipeline results)
# - Includes: predicted leads, fit scores, creator tiers, model accuracy
# - Fit scores are calculated based on the selected program type
```

---

## 🌐 Frontend Usage

### 1. Open the Interface
```bash
# Navigate to frontend directory
cd problems/creatorfit/frontend

# Start HTTP server (REQUIRED for full functionality)
python -m http.server 8000

# Open in browser
# Navigate to: http://localhost:8000
```

**⚠️ Important**: The frontend requires an HTTP server to work properly due to JavaScript security restrictions. Opening `index.html` directly in the browser will result in limited functionality.

**Why HTTP Server is Required:**
- **CORS Restrictions**: Modern browsers block local file access for security
- **JavaScript Fetch API**: The frontend uses `fetch()` to load JSON results, which requires HTTP protocol
- **File Protocol Limitations**: `file://` protocol restricts AJAX calls and external resource loading
- **Production Simulation**: HTTP server mimics real-world deployment environment

### 2. Frontend Features
- **Program Selection**: Choose from 4 Odin School programs
- **CSV Upload**: Upload your creator dataset
- **Real-time Analysis**: View Phase 3 ML pipeline results
- **Interactive Table**: Sort by any column, filter results
- **Visual Indicators**: Color-coded fit scores and creator tiers

### 3. Supported CSV Format
Your CSV must contain these columns:
```csv
creator_id,topic,recent_video_transcript,posting_cadence_days,views_90d,clicks,leads,qualified_leads,enrollments,refunds,geography,language,edtech_topics
```

**Required Fields:**
- `creator_id`: Unique identifier
- `topic`: Creator's main content topic
- `recent_video_transcript`: Video content text
- `views_90d`: 90-day view count
- `geography`: Creator location (INDIA only)
- `language`: Content language (English/Hindi/Telugu)

---

## 🔍 Understanding the Results

### Model Performance Metrics
- **R² Score**: 0.855 (85.5% accuracy)
- **MAE**: Mean Absolute Error in lead predictions
- **RMSE**: Root Mean Square Error
- **MAPE**: Mean Absolute Percentage Error

### Feature Engineering (16 Features)
**Numeric Features (12):**
- `views_90d`, `clicks`, `leads`, `qualified_leads`
- `posting_cadence_days`, `enrollments`, `refunds`
- `fit_score`, `creator_tier`, `india_focused`
- `language_score`, `is_educational`, `edtech_topic_depth`

**Categorical Features (4):**
- `topic`, `language`, `geography`, `edtech_topics`

### Output Interpretation
- **Fit Score**: 0.0-1.0 (higher = better program fit)
- **Predicted Leads**: ML-predicted qualified leads
- **Creator Tier**: Established/Growing/Emerging based on views
- **Rank**: Sorted by fit score (best creators first)

---

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### 1. "Module not found" errors
```bash
# Ensure virtual environment is activated
.venv\Scripts\activate

# Reinstall packages
pip install -r requirements.txt
```

#### 2. "Trained model not found" error
```bash
# Check if model files exist
ls models/

# If missing, retrain the model
python -m problems.creatorfit.train
```

#### 3. Frontend shows "Phase 3 results not found"
```bash
# Generate results first
python problems/creatorfit/frontend/process_csv.py your_file.csv data_science

# Then refresh frontend
```

#### 4. Frontend JavaScript errors or limited functionality
```bash
# Ensure you're using HTTP server, not opening file directly
cd problems/creatorfit/frontend
python -m http.server 8000

# Open http://localhost:8000 in browser (not file:// protocol)
```

#### 5. Low accuracy predictions
```bash
# Check data quality
python problems/creatorfit/utils/data_preprocessing.py

# Verify feature engineering
python problems/creatorfit/utils/features.py

# Retrain with better data
python -m problems.creatorfit.train
```

### Performance Optimization
- **Large datasets**: Use batch processing
- **Memory issues**: Reduce batch size in `train.py`
- **Slow predictions**: Use pre-trained model caching

---

## 📊 Business Impact & Targets

### Problem Statement Solved
✅ **Creator Underperformance Diagnosis**: Identified content-program misalignment and audience quality issues

✅ **AI-Driven Solutions**: 
1. **Content-Program Fit Scoring**: Semantic similarity + ML features
2. **Lead Forecasting**: LightGBM regression with 85.5% accuracy

### Expected Business Outcomes
- **CPL Reduction**: -25% cost per qualified lead
- **Enrollment Increase**: +20% from optimized creator selection
- **Brand Safety**: 100% EdTech topic relevance
- **ROI Improvement**: Better creator-program matching

---

## 🔄 Workflow Summary

### For Developers
1. **Setup**: Install dependencies, activate virtual environment
2. **Training**: Run `train.py` to build ML model
3. **Testing**: Use `process_csv.py` for predictions
4. **Frontend**: Start HTTP server and open `http://localhost:8000`

### For End Users
1. **Upload**: CSV file with creator data
2. **Select**: Odin School program type
3. **Analyze**: View AI-powered fit scores and predictions
4. **Optimize**: Use results to select best creators

---

## 📞 Support & Documentation

### File Structure
```
problems/creatorfit/
├── models/                    # Trained ML models
├── frontend/                  # Web interface
│   ├── index.html            # Main UI
│   ├── process_csv.py        # Prediction pipeline
│   └── sample_creators.csv   # Sample dataset
├── data_preprocessing.py      # Data cleaning
├── features.py               # Feature engineering
├── train.py                  # Model training
└── SETUP.md                  # This guide
```

### Key Commands Reference
```bash
# Training
python -m problems.creatorfit.train

# Predictions
python problems/creatorfit/frontend/process_csv.py file.csv program

# Frontend (REQUIRES HTTP SERVER)
cd problems/creatorfit/frontend
python -m http.server 8000
# Then open: http://localhost:8000
```

---

## 🎉 Success Criteria

Your setup is successful when:
- ✅ Model training completes with R² > 0.80
- ✅ Frontend loads without errors
- ✅ CSV upload generates JSON results
- ✅ Table displays sorted creator rankings
- ✅ Phase 3 pipeline info shows 85.5% accuracy

**Ready to optimize your influencer marketing with AI! 🚀**

## Flow to predict qualified leads
```
{
  "creator_id": "CREATOR_12345",
  "recent_video_transcript": "Complete Python programming tutorial covering data structures, algorithms, pandas, numpy for beginners...",
  "topic": "Python;Data Science",
  "views_90d": 150000,
  "posting_cadence_days": 3,
  "language": "English",
  "geography": "INDIA",
  "category_tag": "Education;Programming"
}
```