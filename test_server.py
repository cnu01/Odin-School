#!/usr/bin/env python3
"""
Simple test server to isolate API issues
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Test Server")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Test server is working"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/onetruth/dashboard")
async def test_dashboard():
    return {
        "message": "Test dashboard data",
        "dashboard_summary": "AI-powered unified business analytics",
        "time_range": "7d",
        "data_points": 100,
        "test": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
