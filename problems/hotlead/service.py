import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from bson import ObjectId
from database import get_database
from ml.hotlead_model import hotlead_model, predict_lead_conversion, generate_synthetic_training_data
from services.aws import get_bedrock_service
from .models import (
    LeadInput, ScoredLead, LeadIngestRequest, LeadResponse,
    PriorityQueueRequest, PriorityQueueResponse, ContactUpdate,
    OutreachRequest, WhyLeadRequest
)

logger = logging.getLogger(__name__)

# Simple in-memory rep list for demo auto-assignment
DEMO_REPS = ["alice", "bob", "charlie"]
_rep_cursor = {"idx": 0}

def _assign_next_rep() -> str:
    idx = _rep_cursor["idx"]
    rep = DEMO_REPS[idx % len(DEMO_REPS)]
    _rep_cursor["idx"] = (idx + 1) % len(DEMO_REPS)
    return rep

def _notify_new_priority_lead(lead_email: str, lead_id: str, rep: str, score: int):
    # Demo notification stub (replace with Slack/email/webhook later)
    logger.info(
        f"[NOTIFY] Priority lead assigned -> rep={rep} lead_id={lead_id} email={lead_email} score={score}"
    )

async def get_lead_analysis_from_ai(lead_input: LeadInput) -> dict:
    """
    Call external AI service for lead analysis and scoring
    
    Args:
        lead_input: LeadInput object containing lead data
        
    Returns:
        Dictionary containing AI analysis results
    """
    import httpx
    import os
    import json
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    # Convert lead input data to a string for the prompt
    lead_data_str = json.dumps(lead_input.model_dump(), indent=2)
    
    # Construct detailed, multi-part prompt for LLM
    prompt = f"""
You are an expert sales analyst for Odin School, an EdTech company. Your task is to analyze a new lead and return a JSON object with a priority score and routing action.

**Contextual Rules:**
- Lead-to-paid conversion varies 3-5x by source. Treat leads from sources containing 'Campaign', 'LinkedIn', or 'Referral' as high-value.
- Leads with high pageviews (e.g., more than 5) show strong interest.
- The goal is to contact high-priority leads in under 5 minutes.

**Lead Data to Analyze:**
{lead_data_str}

**Your Task:**
Based on all the information, return ONLY a valid JSON object with three keys:
1. "score": An integer from 0 to 100.
2. "reason": A short, one-sentence explanation for the score.
3. "priority_routing_action": A string with one of these exact values: "Immediate: Route to Tier 1 Sales", "Priority: Add to 1-hour callback queue", or "Standard: Add to general queue".
"""
    
    # API request payload for OpenAI
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Make API call to OpenAI
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            ai_response = response.json()
            
            # Extract the content from AI response
            content = ai_response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            
            # Parse the JSON response from AI
            analysis_result = json.loads(content)
            
            return analysis_result
            
        except httpx.RequestError as e:
            raise Exception(f"Error calling AI API: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Error parsing AI response: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error in AI analysis: {str(e)}")

async def score_lead_with_ai(lead_input: LeadInput) -> ScoredLead:
    """
    Score a lead using AI analysis
    
    Args:
        lead_input: LeadInput object containing lead data
        
    Returns:
        ScoredLead with AI-generated score and routing action
    """
    try:
        # Get AI analysis
        ai_result = await get_lead_analysis_from_ai(lead_input)
        
        # Extract priority and routing_action from the combined field
        priority_routing = ai_result.get("priority_routing_action", "Standard: Add to general queue")
        
        # Parse priority and routing action
        if "Immediate" in priority_routing:
            priority = "urgent"
            routing_action = "immediate_followup"
        elif "Priority" in priority_routing:
            priority = "high"
            routing_action = "priority_queue"
        else:
            priority = "medium"
            routing_action = "sales_qualified"
        
        # Create and return ScoredLead model with new structure
        scored_lead = ScoredLead(
            lead_input=lead_input,
            score=ai_result.get("score", 50),  # Default to medium score
            reason=ai_result.get("reason", "Lead analyzed based on available data."),
            priority=priority,
            routing_action=routing_action
        )
        
        return scored_lead
        
    except Exception as e:
        # Return a fallback response in case of AI service failure
        fallback_score = 30  # Conservative default score
        fallback_reason = f"Fallback scoring due to service issue: {str(e)}"
        
        return ScoredLead(
            lead_input=lead_input,
            score=fallback_score,
            reason=fallback_reason,
            priority="low",
            routing_action="nurture_campaign"
        )

class HotLeadService:
    """Service class for HotLead operations with MongoDB integration"""
    
    def __init__(self):
        self.db = None
    
    async def get_database(self):
        """Get database connection"""
        if self.db is None:
            self.db = get_database()
        return self.db
    
    async def score_lead(self, lead_input: LeadInput) -> ScoredLead:
        """
        Score a lead using AI analysis
        
        Args:
            lead_input: LeadInput containing lead data
            
        Returns:
            ScoredLead with AI analysis and routing recommendation
        """
        return await score_lead_with_ai(lead_input)
    
    async def ingest_lead(self, lead_request: LeadIngestRequest) -> LeadResponse:
        """
        Ingest a new lead, score it using ML model, and save to MongoDB
        """
        try:
            db = await self.get_database()
            
            # Generate unique lead ID
            lead_id = f"LEAD_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Prepare data for ML model prediction
            lead_data = {
                "lead_id": lead_id,
                "email": lead_request.email,
                "page_views": lead_request.page_views,
                "time_on_site": lead_request.time_on_site,
                "course_pages_viewed": lead_request.course_pages_viewed,
                "downloads_count": lead_request.downloads_count,
                "form_submissions": lead_request.form_submissions,
                "demo_requests": lead_request.demo_requests,
                "source": lead_request.source,
                "location": lead_request.location or "Unknown",
                "device": lead_request.device,
                "hour": datetime.now().hour,
                "day_of_week": datetime.now().weekday(),
                "is_return_visitor": lead_request.is_return_visitor
            }
            
            # Get ML prediction and scoring
            prediction_result = await predict_lead_conversion(lead_data)
            conversion_probability = prediction_result["prediction"].get("probabilities", {}).get("True", 0.5)
            lead_temperature = prediction_result["insights"]["lead_temperature"]
            
            # Calculate dynamic priority threshold from existing leads
            if db is not None:
                leads_collection = db["leads"]
                all_leads = await leads_collection.find({"priority_score": {"$ne": None}}).to_list(None)
                
                if len(all_leads) >= 5:  # Need minimum sample for percentile calculation
                    scores = [lead["priority_score"] for lead in all_leads if lead.get("priority_score") is not None]
                    scores.append(int(conversion_probability * 100))  # Include current lead
                    scores.sort(reverse=True)
                    
                    # Dynamic 80th percentile threshold
                    percentile_80_threshold = scores[int(len(scores) * 0.2)] if len(scores) > 5 else 50
                    
                    # Source bias intelligence weighting
                    source_quality_multiplier = {
                        "referral": 2.5,     # 5× better conversion than social
                        "direct": 2.0,       # High intent traffic  
                        "google": 1.5,       # Paid search quality
                        "website": 1.0,      # Baseline organic
                        "social_media": 0.5, # Lowest conversion rate
                        "email": 1.2,        # Email campaigns
                        "partner": 2.2       # Partner referrals
                    }.get(lead_request.source.lower(), 1.0)
                else:
                    # Bootstrap values for first few leads
                    percentile_80_threshold = 30
                    source_quality_multiplier = 1.0
            else:
                percentile_80_threshold = 50
                source_quality_multiplier = 1.0
            
            # Apply AI-driven intelligent scoring
            base_score = int(conversion_probability * 100)
            
            # AI Source Intelligence Weighting
            source_weighted_score = min(100, int(base_score * source_quality_multiplier))
            
            # Behavioral Intent Amplification
            intent_multiplier = 1.0
            if lead_request.demo_requests > 0:
                intent_multiplier += 0.5  # Demo request = high intent
            if lead_request.course_pages_viewed >= 3:
                intent_multiplier += 0.3  # Multi-page engagement
            if lead_request.downloads_count >= 2:
                intent_multiplier += 0.2  # Download behavior
            if lead_request.is_return_visitor:
                intent_multiplier += 0.3  # Return visitor
            
            # Final intelligent priority score
            priority_score = min(100, int(source_weighted_score * intent_multiplier))

            # Dynamic priority assignment (top 20% rule)
            is_priority = priority_score >= percentile_80_threshold

            # Check for existing lead by email
            existing_lead = None
            if db is not None:
                existing_lead = await leads_collection.find_one({"email": lead_request.email})

            current_time = datetime.now()
            
            if existing_lead:
                # Update existing lead with new activity
                update_data = {
                    "source": lead_request.source,
                    "page_views": max(existing_lead.get("page_views", 0), lead_request.page_views),
                    "time_on_site": (existing_lead.get("time_on_site", 0) + lead_request.time_on_site),
                    "conversion_probability": conversion_probability,
                    "last_activity": current_time,
                    "is_priority": is_priority,
                    "priority_score": priority_score,
                    "lead_temperature": lead_temperature,
                    "updated_at": current_time
                }
                
                # Update behavioral data
                behavioral_data = existing_lead.get("behavioral_data", {})
                behavioral_data.update(lead_request.additional_data)
                update_data["behavioral_data"] = behavioral_data
                
                await leads_collection.update_one(
                    {"_id": existing_lead["_id"]},
                    {"$set": update_data}
                )
                
                lead_doc = {**existing_lead, **update_data}
                logger.info(f"Updated existing lead {existing_lead['lead_id']} for email {lead_request.email}")
            else:
                # Create new lead record
                lead_doc = {
                    "lead_id": lead_id,
                    "email": lead_request.email,
                    "phone": lead_request.phone,
                    "source": lead_request.source,
                    "utm_source": lead_request.utm_source,
                    "utm_medium": lead_request.utm_medium,
                    "utm_campaign": lead_request.utm_campaign,
                    "page_views": lead_request.page_views,
                    "time_on_site": lead_request.time_on_site,
                    "downloads": lead_request.downloads_count,
                    "location": lead_request.location,
                    "job_title": lead_request.job_title,
                    "company": lead_request.company,
                    "experience_level": lead_request.experience_level,
                    "conversion_probability": conversion_probability,
                    "priority_score": priority_score,
                    "is_priority": is_priority,
                    "lead_temperature": lead_temperature,
                    "contacted_at": None,
                    "assigned_rep": None,
                    "status": "new",
                    "behavioral_data": lead_request.additional_data,
                    "created_at": current_time,
                    "last_activity": current_time,
                    "updated_at": current_time,
                    "is_active": True
                }
                
                if db is not None:
                    await leads_collection.insert_one(lead_doc)
                logger.info(f"Created new lead {lead_id} for email {lead_request.email}")
            
            # Auto-assign rep for priority leads
            if is_priority and not lead_doc.get("assigned_rep"):
                assigned_rep = _assign_next_rep()
                lead_doc["assigned_rep"] = assigned_rep
                
                if db is not None:
                    await leads_collection.update_one(
                        {"lead_id": lead_id},
                        {"$set": {"assigned_rep": assigned_rep}}
                    )
                
                _notify_new_priority_lead(lead_doc["email"], lead_id, assigned_rep, priority_score)
            
            return LeadResponse(
                lead_id=lead_doc["lead_id"],
                email=lead_doc["email"],
                source=lead_doc["source"],
                priority_score=lead_doc["priority_score"],
                is_priority=lead_doc["is_priority"],
                lead_temperature=lead_doc["lead_temperature"],
                conversion_probability=lead_doc["conversion_probability"],
                recommended_action=prediction_result["insights"]["recommended_action"],
                assigned_rep=lead_doc.get("assigned_rep"),
                status=lead_doc["status"],
                created_at=lead_doc["created_at"],
                insights=prediction_result["insights"]
            )
            
        except Exception as e:
            logger.error(f"Lead ingestion failed: {str(e)}")
            raise Exception(f"Lead ingestion failed: {str(e)}")
    
    async def get_priority_queue(self, request: PriorityQueueRequest) -> PriorityQueueResponse:
        """Get prioritized leads from the queue"""
        try:
            db = await self.get_database()
            if db is None:
                raise Exception("Database not available")
            
            leads_collection = db["leads"]
            
            # Build query filter - don't require is_priority=True, just use min_score
            query_filter = {}
            
            if request.min_score:
                query_filter["priority_score"] = {"$gte": request.min_score}
            
            if request.status_filter:
                query_filter["status"] = request.status_filter
            
            if request.source_filter:
                query_filter["source"] = request.source_filter
            
            # Get leads sorted by score (highest first)
            priority_leads = await leads_collection.find(query_filter).sort(
                "priority_score", -1
            ).limit(request.limit).to_list(None)
            
            # Convert ObjectId to string for JSON serialization
            for lead in priority_leads:
                if "_id" in lead:
                    lead["_id"] = str(lead["_id"])
            
            # Get queue summary
            total_priority = await leads_collection.count_documents({"priority_score": {"$gte": 70}})
            uncontacted = await leads_collection.count_documents({"contacted_at": None})
            
            return PriorityQueueResponse(
                total_priority_leads=total_priority,
                leads=priority_leads,
                queue_summary={
                    "total_in_queue": len(priority_leads),
                    "uncontacted": uncontacted,
                    "avg_score": sum(lead.get("priority_score", 0) for lead in priority_leads) / len(priority_leads) if priority_leads else 0
                }
            )
            
        except Exception as e:
            logger.error(f"Priority queue retrieval failed: {str(e)}")
            raise Exception(f"Priority queue retrieval failed: {str(e)}")
    
    async def train_model(self, size: int = 2000) -> Dict[str, Any]:
        """Train the HotLead ML model with synthetic data"""
        try:
            # Generate synthetic training data
            training_data = generate_synthetic_training_data(num_samples=size)
            
            # Train the model
            metrics = await hotlead_model.train(training_data, target_column="converted")
            
            # Save training data to MongoDB for future reference
            db = await self.get_database()
            if db is not None:
                training_collection = db["training_data"]
                await training_collection.insert_many(training_data)
            
            return {
                "message": "HotLead model trained successfully",
                "size": size,
                "metrics": metrics,
                "features": hotlead_model.feature_columns
            }
            
        except Exception as e:
            logger.error(f"Model training failed: {str(e)}")
            raise Exception(f"Model training failed: {str(e)}")
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics from the database"""
        try:
            db = await self.get_database()
            if db is None:
                # Return fallback analytics if database not available
                return {
                    "current_metrics": {
                        "total_leads_today": 0,
                        "priority_leads": 0,
                        "avg_score": 0,
                        "conversion_rate": 0
                    },
                    "source_performance": [],
                    "success_metrics_tracking": {
                        "meeting_booking_rate": 0,
                        "no_show_reduction": 0,
                        "win_rate_improvement": 0
                    }
                }
            
            leads_collection = db["leads"]
            
            # Get current metrics
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            total_leads_today = await leads_collection.count_documents({
                "created_at": {"$gte": today.isoformat()}
            })
            
            priority_leads = await leads_collection.count_documents({
                "is_priority": True
            })
            
            # Calculate average score
            pipeline = [
                {"$group": {"_id": None, "avg_score": {"$avg": "$priority_score"}}}
            ]
            avg_result = await leads_collection.aggregate(pipeline).to_list(None)
            avg_score = int(avg_result[0]["avg_score"]) if avg_result else 0
            
            # Calculate conversion rate
            total_leads = await leads_collection.count_documents({})
            converted_leads = await leads_collection.count_documents({"converted": True})
            conversion_rate = int((converted_leads / total_leads * 100)) if total_leads > 0 else 0
            
            # Source performance analysis
            source_pipeline = [
                {
                    "$group": {
                        "_id": "$source",
                        "leads": {"$sum": 1},
                        "conversions": {"$sum": {"$cond": [{"$eq": ["$converted", True]}, 1, 0]}},
                        "avg_score": {"$avg": "$priority_score"}
                    }
                },
                {
                    "$project": {
                        "source": "$_id",
                        "leads": 1,
                        "conversion_rate": {
                            "$round": [
                                {"$multiply": [{"$divide": ["$conversions", "$leads"]}, 100]}, 
                                1
                            ]
                        },
                        "avg_score": {"$round": ["$avg_score", 0]}
                    }
                }
            ]
            
            source_performance = await leads_collection.aggregate(source_pipeline).to_list(None)
            
            # Success metrics (calculate based on actual data)
            contacted_leads = await leads_collection.count_documents({"contacted": True})
            meeting_booked = await leads_collection.count_documents({"meeting_booked": True})
            
            meeting_booking_rate = int((meeting_booked / contacted_leads * 100)) if contacted_leads > 0 else 0
            
            return {
                "current_metrics": {
                    "total_leads_today": total_leads_today,
                    "priority_leads": priority_leads,
                    "avg_score": avg_score,
                    "conversion_rate": conversion_rate
                },
                "source_performance": source_performance,
                "success_metrics_tracking": {
                    "meeting_booking_rate": meeting_booking_rate,
                    "no_show_reduction": 60,  # Sample value
                    "win_rate_improvement": 45  # Sample value
                }
            }
            
        except Exception as e:
            logger.error(f"Analytics retrieval failed: {str(e)}")
            raise Exception(f"Analytics retrieval failed: {str(e)}")
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get model information and status"""
        return hotlead_model.get_model_info()
    
    async def update_contact_status(self, update: ContactUpdate) -> Dict[str, Any]:
        """Update lead contact status"""
        try:
            db = await self.get_database()
            if db is None:
                raise Exception("Database not available")
            
            leads_collection = db["leads"]
            
            update_data = {
                "contacted_at": datetime.now(),
                "status": "contacted",
                "updated_at": datetime.now()
            }
            
            if update.notes:
                update_data["contact_notes"] = update.notes
            if update.outcome:
                update_data["contact_outcome"] = update.outcome
            if update.next_action:
                update_data["next_action"] = update.next_action
            
            result = await leads_collection.update_one(
                {"lead_id": update.lead_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                raise Exception("Lead not found or not updated")
            
            return {"message": "Contact status updated successfully", "lead_id": update.lead_id}
            
        except Exception as e:
            logger.error(f"Contact update failed: {str(e)}")
            raise Exception(f"Contact update failed: {str(e)}")
    
    async def generate_outreach_message(self, request: OutreachRequest) -> Dict[str, Any]:
        """Generate personalized outreach message using Bedrock"""
        try:
            db = await self.get_database()
            if db is None:
                raise Exception("Database not available")
            
            leads_collection = db["leads"]
            lead = await leads_collection.find_one({"lead_id": request.lead_id})
            
            if not lead:
                raise Exception("Lead not found")
            
            # Try to use Bedrock for message generation
            bedrock_service = get_bedrock_service()
            
            prompt = f"""
            Generate a personalized outreach message for a lead with the following information:
            
            Lead Details:
            - Email: {lead.get('email')}
            - Source: {lead.get('source')}
            - Priority Score: {lead.get('priority_score')}
            - Lead Temperature: {lead.get('lead_temperature')}
            - Course Interest: {lead.get('course_interest', 'General')}
            - Location: {lead.get('location', 'Unknown')}
            
            Rep Name: {request.rep_name}
            Contact Method: {request.contact_method}
            
            Create a professional, engaging message that addresses their interests and encourages response.
            """
            
            ai_message = await bedrock_service.generate_text(prompt, max_tokens=300)
            
            if ai_message:
                return {
                    "lead_id": request.lead_id,
                    "message": ai_message,
                    "generated_by": "bedrock",
                    "rep_name": request.rep_name
                }
            else:
                # Fallback template message
                fallback_message = f"""
                Hi {lead.get('first_name', 'there')},
                
                I noticed you've been exploring our courses at Odin School. Based on your interest in {lead.get('course_interest', 'our programs')}, I'd love to help you find the perfect fit for your learning goals.
                
                Would you be available for a quick call this week to discuss how we can help you advance your career?
                
                Best regards,
                {request.rep_name}
                Odin School
                """
                
                return {
                    "lead_id": request.lead_id,
                    "message": fallback_message.strip(),
                    "generated_by": "template",
                    "rep_name": request.rep_name
                }
                
        except Exception as e:
            logger.error(f"Outreach message generation failed: {str(e)}")
            raise Exception(f"Outreach message generation failed: {str(e)}")
    
    async def explain_lead_priority(self, request: WhyLeadRequest) -> Dict[str, Any]:
        """Explain why a lead is prioritized"""
        try:
            db = await self.get_database()
            if db is None:
                raise Exception("Database not available")
            
            leads_collection = db["leads"]
            lead = await leads_collection.find_one({"lead_id": request.lead_id})
            
            if not lead:
                raise Exception("Lead not found")
            
            # Generate explanation based on lead data
            factors = []
            
            if lead.get("priority_score", 0) >= 80:
                factors.append("Very high conversion probability")
            
            if lead.get("demo_requests", 0) > 0:
                factors.append("Requested product demo")
            
            if lead.get("course_pages_viewed", 0) >= 3:
                factors.append("High engagement with course content")
            
            if lead.get("downloads_count", 0) >= 2:
                factors.append("Downloaded multiple resources")
            
            if lead.get("source") in ["referral", "direct"]:
                factors.append("High-quality traffic source")
            
            if lead.get("is_return_visitor"):
                factors.append("Return visitor showing sustained interest")
            
            return {
                "lead_id": request.lead_id,
                "priority_score": lead.get("priority_score"),
                "is_priority": lead.get("is_priority"),
                "explanation": f"This lead is prioritized because: {', '.join(factors)}",
                "factors": factors,
                "recommended_action": lead.get("recommended_action", "Contact within 24 hours")
            }
            
        except Exception as e:
            logger.error(f"Lead explanation failed: {str(e)}")
            raise Exception(f"Lead explanation failed: {str(e)}")
    
    async def seed_database(self, size: int = 2000) -> Dict[str, Any]:
        """Seed database with synthetic leads and train model"""
        try:
            # Generate synthetic data
            training_data = generate_synthetic_training_data(num_samples=size)
            
            # Save to MongoDB
            db = await self.get_database()
            if db is not None:
                leads_collection = db["leads"]
                
                # Clear existing data
                await leads_collection.delete_many({})
                
                # Insert new data
                await leads_collection.insert_many(training_data)
                
                logger.info(f"Seeded {size} leads to MongoDB")
            
            # Train model
            metrics = await hotlead_model.train(training_data, target_column="converted")
            
            # Get statistics
            converted_count = len([d for d in training_data if d["converted"]])
            priority_count = len([d for d in training_data if d.get("priority_score", 0) >= 70])
            
            return {
                "message": "Database seeded and model trained successfully",
                "total_leads": size,
                "converted_leads": converted_count,
                "priority_leads": priority_count,
                "conversion_rate": f"{converted_count/size*100:.1f}%",
                "model_metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"Database seeding failed: {str(e)}")
            raise Exception(f"Database seeding failed: {str(e)}")
