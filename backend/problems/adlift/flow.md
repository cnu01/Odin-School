# AdLift Marketing Optimizer - Quick Start Guide

## 1. Start Backend

```bash
# Navigate to project root
cd /path/to/your/APEX-AI

# Run FastAPI server
python -m uvicorn main:app --reload --port 8000
```

Backend runs at: `http://localhost:8000`

## 2. Access Frontend

Open browser: `http://localhost:8000/adlift/index.html`

## 3. API Endpoints

### Health Check
```
GET http://localhost:8000/api/adlift/health
```

### Analyze CSV
```
POST http://localhost:8000/api/adlift/analyze
Content-Type: multipart/form-data
Body: file=your_csv_file.csv
```

## 4. Input Format

CSV file with these columns:
```
headline,description,audience_segment,placement,impressions,clicks,spend,conversions,qualified_leads,CTR,CPC,CVR,qualified_rate
```

Example row:
```
"Master DSA Fast","Learn algorithms","Graduates","search",1500,45,350.0,12,6,0.03,7.78,0.27,0.50
```

## 5. Output Format

### API Response
```json
{
  "success": true,
  "message": "Analysis completed successfully",
  "data": {
    "performance_variance": {
      "ctr_range": "0.6% to 2.7%",
      "cpql_range": "₹347 to ₹2955",
      "total_campaigns": 128
    },
    "root_causes": [
      {
        "name": "Copy-Intent Mismatch",
        "case_count": 32,
        "evidence": [...]
      }
    ],
    "campaign_decisions": {
      "pause_count": 51,
      "keep_count": 30,
      "monitor_count": 47
    },
    "variants_data": {
      "variants_count": 40,
      "variants": [
        {
          "headline": "AI-Generated Headline",
          "description": "AI-Generated Description",
          "type": "winner-like",
          "segment": "Graduates",
          "placement": "search"
        }
      ]
    },
    "expected_impact": {
      "ctr_improvement": "+25%",
      "cpql_reduction": "-20%",
      "timeline": "30 days"
    }
  }
}
```

### Downloadable Files

1. **variants.csv** - AI-generated ad variants
2. **prioritization.csv** - Campaign decisions (KEEP/PAUSE/MONITOR)

## 6. UI Features

- Upload CSV file via drag & drop
- Real-time analysis with loading state
- **Solution Ranking** - Prioritized recommendations
- **AI Variants Preview** - Top 5 generated variants
- Performance metrics and root cause analysis
- Download buttons for CSV results

## 7. Quick Test

1. Start backend: `python -m uvicorn main:app --reload --port 8000`
2. Open: `http://localhost:8000/adlift/index.html`
3. Upload: `dataset/adlift_ads.csv`
4. View results and download files

## 8. File Structure

```
problems/adlift/
├── analysis.py          # Core analysis logic
├── variant_generator.py # AI variant generation
├── service.py          # Business logic service
├── models.py           # API data models
├── routes.py           # API endpoints
├── static/             # Frontend files
│   ├── index.html
│   ├── style.css
│   └── script.js
└── dataset/
    └── adlift_ads.csv  # Sample data
```

## 9. Troubleshooting

- **Backend won't start**: Check if port 8000 is free
- **Frontend not loading**: Ensure backend is running first
- **CSV upload fails**: Verify CSV has required columns
- **404 on upload**: Check frontend uses correct endpoint `/api/adlift/analyze`
- **Analysis errors**: Check CSV data format and encoding (UTF-8)