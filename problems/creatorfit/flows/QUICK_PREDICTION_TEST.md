# 🚀 Quick Prediction Pipeline Test Guide

## **For Developers - 2 Minutes Setup**

### **Prerequisites**
- Python 3.8+ installed
- Virtual environment activated (`.venv`)

### **Step 1: Install Dependencies**
```bash
pip install pandas numpy scikit-learn lightgbm sentence-transformers joblib
```

### **Step 2: Navigate to Frontend Directory**
```bash
cd problems/creatorfit/frontend
```

### **Step 3: Run Prediction Pipeline**
```bash
python prediction_pipeline.py sample_creators.csv data_science
```

### **Expected Output**
- **File Generated**: `sample_creators_prediction_results.json`
- **Terminal Shows**: Analysis summary with top 5 creators and business metrics
- **Processing Time**: ~15-30 seconds

### **Sample Terminal Output**
```
🚀 PRODUCTION CREATORFIT ANALYSIS COMPLETE!
Program: Data_Science
Creators Analyzed: 1500
Total Predicted Leads: 403,817
Estimated CPL: ₹0
Top Creator: EDU_1254 - 5956 leads predicted
```

### **Test with Your Own Data**
```bash
# Replace 'your_file.csv' with your CSV file
python prediction_pipeline.py your_file.csv data_science

# Available program types: data_science, frontend, backend, devops
```

### **Required CSV Columns**
Your CSV must have these columns:
- `creator_id`
- `recent_video_transcript` 
- `views_90d`
- `topic`
- `language`
- `creator_tier`
- `posting_cadence_days`

### **JSON Output Structure**
```json
{
  "success": true,
  "results": [
    {
      "creator_id": "EDU_1254",
      "predicted_qualified_leads": 5956,
      "fit_score": 0.539,
      "confidence_score": 0.996,
      "recommendation": "BOOK"
    }
  ],
  "summary": {
    "total_predicted_leads": 403817,
    "estimated_cpl": 0.25,
    "estimated_roi_percent": 2018986.2
  }
}
```

### **Troubleshooting**
- **Import Error**: Ensure you're in the correct directory and `.venv` is activated
- **Model Not Found**: Run training first: `python -m problems.creatorfit.train`
- **CSV Error**: Check your CSV has all required columns

### **Quick Commands Reference**
```bash
# Full pipeline test
cd problems/creatorfit/frontend
python prediction_pipeline.py sample_creators.csv data_science

# Check output
ls -la sample_creators_prediction_results.json
```

---
**⚡ That's it! Your prediction pipeline is ready to forecast qualified leads for any creator dataset.**
