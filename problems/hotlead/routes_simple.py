"""
Simple HotLead routes for testing - without heavy ML dependencies
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import json
from datetime import datetime
import random

router = APIRouter()

# Mock data for testing
mock_leads = [
    {
        "lead_id": "LEAD_20250812_001",
        "email": "john.doe@example.com",
        "source": "organic",
        "priority_score": 85,
        "is_priority": True,
        "lead_temperature": "🔥 HOT",
        "conversion_probability": 0.85,
        "status": "new",
        "created_at": datetime.now().isoformat(),
        "page_views": 12,
        "time_on_site": 450,
        "device": "desktop",
        "location": "Bangalore, India"
    },
    {
        "lead_id": "LEAD_20250812_002", 
        "email": "jane.smith@example.com",
        "source": "referral",
        "priority_score": 92,
        "is_priority": True,
        "lead_temperature": "🔥 HOT",
        "conversion_probability": 0.92,
        "status": "contacted",
        "created_at": datetime.now().isoformat(),
        "page_views": 8,
        "time_on_site": 320,
        "device": "mobile",
        "location": "Mumbai, India"
    },
    {
        "lead_id": "LEAD_20250812_003",
        "email": "mike.johnson@example.com", 
        "source": "social_media",
        "priority_score": 65,
        "is_priority": False,
        "lead_temperature": "🟡 WARM",
        "conversion_probability": 0.65,
        "status": "new",
        "created_at": datetime.now().isoformat(),
        "page_views": 5,
        "time_on_site": 180,
        "device": "desktop",
        "location": "Delhi, India"
    }
]

mock_analytics = {
    "current_metrics": {
        "total_leads_today": 25,
        "priority_leads": 8,
        "avg_score": 72,
        "conversion_rate": 12
    },
    "source_performance": [
        {"source": "organic", "leads": 10, "conversion_rate": 15, "avg_score": 78},
        {"source": "referral", "leads": 5, "conversion_rate": 25, "avg_score": 85},
        {"source": "social_media", "leads": 8, "conversion_rate": 8, "avg_score": 62},
        {"source": "paid_search", "leads": 2, "conversion_rate": 20, "avg_score": 80}
    ],
    "success_metrics_tracking": {
        "meeting_booking_rate": 75,
        "no_show_reduction": 60, 
        "win_rate_improvement": 45
    }
}

mock_system_status = {
    "system": "HotLead AI",
    "version": "1.0.0",
    "status": "operational",
    "ml_model": {
        "model_name": "hotlead_conversion",
        "is_trained": True,
        "metadata": {
            "metrics": {
                "accuracy": 0.8417
            }
        }
    },
    "capabilities": [
        "Lead Scoring with 22-feature ML model",
        "Real-time priority queue management",  
        "AI-powered outreach message generation",
        "Intelligent lead routing and assignment",
        "Behavioral analysis and engagement tracking"
    ]
}

@router.get("/")
async def hotlead_home():
    """HotLead API home endpoint"""
    return {
        "system": "HotLead - AI-Powered Lead Scoring",
        "version": "1.0.0",
        "description": "ML-driven lead conversion prediction and priority routing",
        "endpoints": [
            "/ingest - Ingest new lead with ML scoring",
            "/priority-queue - Get prioritized leads",
            "/train - Train ML model",
            "/analytics - Get system analytics",
            "/status - System health check"
        ]
    }

@router.post("/ingest")
async def ingest_lead(lead_data: Dict[str, Any]):
    """Ingest a new lead and score it"""
    try:
        # Generate a simple score based on data
        email = lead_data.get("email", "")
        source = lead_data.get("source", "unknown")
        page_views = lead_data.get("page_views", 1)
        time_on_site = lead_data.get("time_on_site", 30)
        
        # Simple scoring algorithm for testing
        score = 50  # Base score
        if source in ["referral", "direct"]: score += 20
        if page_views > 5: score += 15
        if time_on_site > 300: score += 15
        
        lead_id = f"LEAD_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        response = {
            "lead_id": lead_id,
            "email": email,
            "source": source,
            "priority_score": min(100, score),
            "is_priority": score >= 70,
            "lead_temperature": "🔥 HOT" if score >= 80 else ("🟡 WARM" if score >= 70 else "🟦 COOL"),
            "conversion_probability": min(0.95, score / 100),
            "recommended_action": "Contact immediately" if score >= 80 else "Add to priority queue",
            "status": "new",
            "created_at": datetime.now().isoformat(),
            "insights": {
                "priority": "HIGH" if score >= 80 else ("MEDIUM" if score >= 70 else "LOW"),
                "follow_up_timing": "Within 1 hour" if score >= 80 else "Within 24 hours"
            }
        }
        
        return {"success": True, "data": response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lead ingestion failed: {str(e)}")

@router.get("/priority-queue")
async def get_priority_queue(limit: int = 20, min_score: int = 70):
    """Get prioritized leads"""
    try:
        # Filter and return mock leads
        priority_leads = [lead for lead in mock_leads if lead["priority_score"] >= min_score]
        priority_leads = priority_leads[:limit]
        
        return {
            "success": True,
            "data": {
                "total_priority_leads": len(priority_leads),
                "leads": priority_leads,
                "queue_summary": {
                    "total_in_queue": len(priority_leads),
                    "uncontacted": len([lead for lead in priority_leads if lead["status"] == "new"]),
                    "avg_score": sum(lead["priority_score"] for lead in priority_leads) / len(priority_leads) if priority_leads else 0
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Priority queue retrieval failed: {str(e)}")

@router.post("/train")
async def train_model(size: int = 2000):
    """Train the ML model"""
    try:
        # Simulate model training
        accuracy = round(random.uniform(0.80, 0.90), 4)
        
        return {
            "success": True,
            "data": {
                "message": "HotLead model trained successfully",
                "size": size,
                "metrics": {
                    "accuracy": accuracy,
                    "training_samples": int(size * 0.8),
                    "test_samples": int(size * 0.2),
                    "features_count": 22
                },
                "features": [
                    "page_views", "time_on_site", "course_pages_viewed", 
                    "downloads_count", "demo_requests", "source_score",
                    "geo_score", "device_score", "time_score"
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model training failed: {str(e)}")

@router.get("/analytics")
async def get_analytics():
    """Get system analytics"""
    try:
        return {
            "success": True,
            "data": mock_analytics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics retrieval failed: {str(e)}")

@router.get("/status")
async def get_system_status():
    """Get system status"""
    try:
        return {
            "success": True,
            "data": mock_system_status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@router.post("/contact")
async def update_contact_status(contact_data: Dict[str, Any]):
    """Update lead contact status"""
    try:
        lead_id = contact_data.get("lead_id")
        
        return {
            "success": True,
            "data": {
                "message": "Contact status updated successfully",
                "lead_id": lead_id
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Contact update failed: {str(e)}")

@router.post("/outreach")
async def generate_outreach_message(outreach_data: Dict[str, Any]):
    """Generate AI outreach message"""
    try:
        lead_id = outreach_data.get("lead_id")
        rep_name = outreach_data.get("rep_name", "Sales Team")
        
        # Simple template message
        message = f"""Hi there,

I noticed you've been exploring our courses at Odin School. Based on your engagement, I'd love to help you find the perfect program for your career goals.

Would you be available for a quick call this week to discuss how we can help you advance your skills?

Best regards,
{rep_name}
Odin School"""
        
        return {
            "success": True,
            "data": {
                "lead_id": lead_id,
                "message": message,
                "generated_by": "template",
                "rep_name": rep_name
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Outreach generation failed: {str(e)}")

@router.get("/explain/{lead_id}")
async def explain_lead_priority(lead_id: str):
    """Explain why a lead is prioritized"""
    try:
        # Find the lead (mock data)
        lead = next((lead for lead in mock_leads if lead["lead_id"] == lead_id), None)
        
        if not lead:
            # Return a generic explanation
            return {
                "success": True,
                "data": {
                    "lead_id": lead_id,
                    "priority_score": 75,
                    "is_priority": True,
                    "explanation": "This lead shows strong engagement with high page views and quality traffic source.",
                    "recommended_action": "Contact within 24 hours"
                }
            }
        
        factors = []
        if lead["priority_score"] >= 80:
            factors.append("Very high conversion probability")
        if lead["page_views"] > 5:
            factors.append("High page engagement")
        if lead["source"] in ["referral", "direct"]:
            factors.append("Quality traffic source")
        
        return {
            "success": True,
            "data": {
                "lead_id": lead_id,
                "priority_score": lead["priority_score"],
                "is_priority": lead["is_priority"],
                "explanation": f"This lead is prioritized because: {', '.join(factors)}",
                "recommended_action": "Contact within 1 hour" if lead["priority_score"] >= 80 else "Contact within 24 hours"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lead explanation failed: {str(e)}")

@router.post("/seed")
async def seed_database(size: int = 2000):
    """Seed database with synthetic data"""
    try:
        # Simulate database seeding
        converted_count = int(size * 0.12)  # 12% conversion rate
        priority_count = int(size * 0.25)   # 25% priority leads
        
        return {
            "success": True,
            "data": {
                "message": "Database seeded successfully",
                "total_leads": size,
                "converted_leads": converted_count,
                "priority_leads": priority_count,
                "conversion_rate": f"{converted_count/size*100:.1f}%"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database seeding failed: {str(e)}")
