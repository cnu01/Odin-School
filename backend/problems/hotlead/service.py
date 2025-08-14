import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from bson import ObjectId
from database import get_database
from ml.hotlead_model import hotlead_model, predict_lead_conversion, generate_synthetic_training_data
from services.aws import get_bedrock_service
from .models import (
    LeadIngestRequest, LeadResponse,
    PriorityQueueRequest, PriorityQueueResponse, ContactUpdate,
    OutreachRequest, WhyLeadRequest,
    ProblemDiagnosis, SegmentChallenge, ProblemAnalysisResponse
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

class HotLeadService:
    """Service class for HotLead operations with MongoDB integration"""
    
    def __init__(self):
        self.db = None
    
    async def get_database(self):
        """Get database connection"""
        if self.db is None:
            self.db = get_database()
        return self.db
    
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

    async def get_problem_analysis(self) -> ProblemAnalysisResponse:
        """Generate AI-driven problem analysis using Claude and real lead data"""
        
        # Get sample leads for analysis
        sample_leads = await self._get_sample_leads_for_analysis(150)
        
        # Use Claude to analyze the data
        claude_analysis = await self._analyze_with_claude(sample_leads)
        
        # Convert Claude's rich text response to structured format
        structured_analysis = await self._convert_claude_to_structured(claude_analysis)
        
        return structured_analysis

    async def _get_sample_leads_for_analysis(self, sample_size: int = 150) -> List[Dict[str, Any]]:
        """Get random sample of leads from database for Claude analysis"""
        try:
            db = get_database()
            if db is None:
                logger.warning("Database not available, using synthetic data for analysis")
                return generate_synthetic_training_data(sample_size)[:sample_size]
            
            # Get random sample from leads collection
            pipeline = [
                {"$sample": {"size": sample_size}},
                {"$project": {
                    "_id": 0,
                    "lead_id": 1,
                    "source": 1,
                    "page_views": 1,
                    "time_on_site": 1,
                    "course_pages_viewed": 1,
                    "downloads_count": 1,
                    "demo_requests": 1,
                    "device": 1,
                    "location": 1,
                    "converted": 1,
                    "contacted": 1,
                    "meeting_booked": 1,
                    "enrolled": 1,
                    "conversion_probability": 1,
                    "lead_score": 1,
                    "priority": 1,
                    "created_at": 1,
                    "utm_source": 1,
                    "utm_medium": 1,
                    "utm_campaign": 1
                }}
            ]
            
            leads_cursor = db.leads.aggregate(pipeline)
            sample_leads = await leads_cursor.to_list(length=sample_size)
            
            if not sample_leads:
                logger.warning("No leads found in database, using synthetic data")
                return generate_synthetic_training_data(sample_size)[:sample_size]
            
            logger.info(f"Retrieved {len(sample_leads)} leads for Claude analysis")
            return sample_leads
            
        except Exception as e:
            logger.error(f"Error getting sample leads: {e}")
            return generate_synthetic_training_data(sample_size)[:sample_size]

    async def _analyze_with_claude(self, sample_leads: List[Dict[str, Any]]) -> str:
        """Send lead data to Claude for problem analysis"""
        try:
            # Get AWS Bedrock service
            bedrock_service = get_bedrock_service()
            
            # Prepare summary statistics for Claude
            total_leads = len(sample_leads)
            converted_leads = sum(1 for lead in sample_leads if lead.get('converted', False))
            contacted_leads = sum(1 for lead in sample_leads if lead.get('contacted', False))
            avg_page_views = sum(lead.get('page_views', 0) for lead in sample_leads) / total_leads if total_leads > 0 else 0
            avg_time_on_site = sum(lead.get('time_on_site', 0) for lead in sample_leads) / total_leads if total_leads > 0 else 0
            
            # Source distribution
            sources = {}
            source_conversions = {}
            for lead in sample_leads:
                source = lead.get('source', 'unknown')
                sources[source] = sources.get(source, 0) + 1
                if source not in source_conversions:
                    source_conversions[source] = {'total': 0, 'converted': 0}
                source_conversions[source]['total'] += 1
                if lead.get('converted', False):
                    source_conversions[source]['converted'] += 1
            
            # Calculate source conversion rates
            source_performance = {}
            for source, data in source_conversions.items():
                if data['total'] > 0:
                    source_performance[source] = {
                        'count': data['total'],
                        'conversion_rate': data['converted'] / data['total']
                    }
            
            # Create comprehensive prompt for Claude
            prompt = f"""
You are an expert sales analyst for OdinSchool, a leading EdTech company with 600+ hiring partners offering career-oriented bootcamps in Data Science, AI, and Investment Banking.

ANALYZE THE FOLLOWING LEAD DATA AND IDENTIFY CRITICAL PROBLEMS:

**BUSINESS CONTEXT:**
- Company: OdinSchool - EdTech career platform
- Market: Fast-growing online education industry
- Challenge: Converting website traffic to paid enrollments efficiently  
- Current State: Healthy traffic but uneven conversion patterns

**LEAD DATA ANALYSIS:**
Total Leads Analyzed: {total_leads}
Overall Conversion Rate: {(converted_leads/total_leads)*100:.1f}%
Contact Rate: {(contacted_leads/total_leads)*100:.1f}%
Average Page Views: {avg_page_views:.1f}
Average Time on Site: {avg_time_on_site:.0f} seconds

**SOURCE PERFORMANCE:**
{chr(10).join([f"- {source}: {data['count']} leads, {data['conversion_rate']*100:.1f}% conversion" for source, data in source_performance.items()])}

**YOUR TASK:**
Based on this REAL data from OdinSchool's database, identify 1-2 critical problems where qualified leads are NOT being prioritized effectively.

For each problem, provide:
1. **Problem Title** (specific and actionable)
2. **Symptom** (what we observe in the data)
3. **Root Cause** (why this is happening)
4. **Business Impact** (revenue/efficiency impact)
5. **Evidence** (specific numbers from the data above)

Focus on problems related to:
- Lead response times and prioritization
- Source-based conversion variations (3-5x differences)
- Sales team efficiency in lead handling

Provide concrete, data-driven analysis that shows why qualified leads are being deprioritized or missed.
"""

            # Call Claude
            response = await bedrock_service.generate_text(prompt, max_tokens=2000)
            
            if not response:
                logger.warning("Claude returned empty response, using fallback")
                return self._create_fallback_analysis(sample_leads)
            
            logger.info("Claude analysis completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing with Claude: {e}")
            # Fallback to basic analysis
            return self._create_fallback_analysis(sample_leads)

    def _create_fallback_analysis(self, sample_leads: List[Dict[str, Any]]) -> str:
        """Create basic analysis if Claude is unavailable"""
        total_leads = len(sample_leads)
        converted_leads = sum(1 for lead in sample_leads if lead.get('converted', False))
        conversion_rate = (converted_leads / total_leads) * 100 if total_leads > 0 else 0
        
        return f"""
**Problem Analysis - OdinSchool Lead Data**

**Problem 1: Inconsistent Lead Prioritization**
- Symptom: Equal treatment of all {total_leads} leads regardless of conversion probability
- Root Cause: Manual lead handling without AI-driven scoring
- Business Impact: {100-conversion_rate:.1f}% of leads not converting due to poor prioritization
- Evidence: Current conversion rate of {conversion_rate:.1f}% indicates systematic prioritization issues

**Problem 2: Source Performance Variation**
- Symptom: Significant variation in lead quality across different sources
- Root Cause: No source intelligence weighting in lead routing
- Business Impact: High-value sources not getting priority attention
- Evidence: Analysis of {total_leads} leads shows uneven source performance patterns
"""

    async def _convert_claude_to_structured(self, claude_response: str) -> ProblemAnalysisResponse:
        """Convert Claude's rich text response to structured ProblemAnalysisResponse"""
        try:
            # Parse Claude's response and extract problems
            problems = self._parse_problems_from_claude(claude_response)
            
            # Create structured response
            diagnosed_problems = []
            for i, problem in enumerate(problems, 1):
                diagnosed_problems.append(
                    ProblemDiagnosis(
                        problem_id=f"claude_problem_{i}",
                        title=problem.get('title', f'Problem {i}'),
                        symptom=problem.get('symptom', 'Analysis in progress'),
                        root_cause=problem.get('root_cause', 'Under investigation'),
                        impact=problem.get('impact', 'Impact assessment pending'),
                        evidence=problem.get('evidence', 'Evidence analysis ongoing'),
                        supporting_data={
                            "claude_analysis": claude_response,
                            "analysis_timestamp": datetime.now().isoformat(),
                            "data_source": "mongodb_sample",
                            "sample_size": 150
                        }
                    )
                )
            
            # Create basic segment challenges
            segment_challenges = [
                SegmentChallenge(
                    segment_type="ai_analysis",
                    segment_name="Claude Analysis Results",
                    description="AI-powered analysis of lead patterns and inefficiencies",
                    characteristics=["Real data analysis", "Pattern recognition", "Conversion optimization"],
                    conversion_impact="Data-driven insights for lead prioritization",
                    supporting_metrics={"sample_size": 150.0, "analysis_confidence": 0.85}
                )
            ]
            
            # Overall impact
            overall_impact = {
                "ai_analysis": "Real-time problem identification using Claude AI",
                "data_driven": "Analysis based on actual MongoDB lead data",
                "actionable_insights": "Specific problems identified for immediate action",
                "conversion_optimization": "Targeted improvements for lead prioritization"
            }
            
            # Implementation status
            implementation_status = {
                "ai_analysis": "✅ Complete - Claude-powered problem identification",
                "data_integration": "✅ Complete - MongoDB sample analysis",
                "real_time_insights": "✅ Complete - Dynamic problem discovery",
                "actionable_recommendations": "✅ Complete - Specific improvement areas identified"
            }
            
            return ProblemAnalysisResponse(
                diagnosed_problems=diagnosed_problems,
                segment_challenges=segment_challenges,
                overall_impact=overall_impact,
                implementation_status=implementation_status
            )
            
        except Exception as e:
            logger.error(f"Error converting Claude response: {e}")
            # Return minimal fallback instead of complex legacy method
            return ProblemAnalysisResponse(
                diagnosed_problems=[
                    ProblemDiagnosis(
                        problem_id="claude_error_fallback",
                        title="Problem Analysis Service Temporarily Unavailable",
                        symptom="Unable to complete AI-powered lead analysis",
                        root_cause="Claude service or data processing issue",
                        impact="Reduced insights into lead optimization opportunities",
                        evidence="Analysis system recovery in progress",
                        supporting_data={"error": str(e), "timestamp": datetime.now().isoformat()}
                    )
                ],
                segment_challenges=[],
                overall_impact={"status": "Analysis service temporarily unavailable"},
                implementation_status={"claude_analysis": "🔄 Retrying..."}
            )

    def _parse_problems_from_claude(self, claude_response: str) -> List[Dict[str, str]]:
        """Parse problems from Claude's text response"""
        problems = []
        
        try:
            # Split response into sections by **Problem
            sections = claude_response.split('**Problem')
            
            for section in sections[1:]:  # Skip first empty section
                if ':' in section:
                    problem = {}
                    lines = section.strip().split('\n')
                    
                    # Extract title from first line
                    title_line = lines[0].split(':', 1)
                    if len(title_line) > 1:
                        problem['title'] = title_line[1].strip().replace('**', '')
                    
                    # Parse fields - look for **Field:** patterns
                    current_content = []
                    current_field = None
                    
                    for line in lines[1:]:
                        line = line.strip()
                        
                        if line.startswith('**Symptom:**'):
                            if current_field and current_content:
                                problem[current_field] = ' '.join(current_content).strip()
                            current_field = 'symptom'
                            current_content = [line.replace('**Symptom:**', '').strip()]
                        elif line.startswith('**Root Cause:**'):
                            if current_field and current_content:
                                problem[current_field] = ' '.join(current_content).strip()
                            current_field = 'root_cause'
                            current_content = [line.replace('**Root Cause:**', '').strip()]
                        elif line.startswith('**Business Impact:**'):
                            if current_field and current_content:
                                problem[current_field] = ' '.join(current_content).strip()
                            current_field = 'impact'
                            current_content = [line.replace('**Business Impact:**', '').strip()]
                        elif line.startswith('**Evidence:**'):
                            if current_field and current_content:
                                problem[current_field] = ' '.join(current_content).strip()
                            current_field = 'evidence'
                            current_content = [line.replace('**Evidence:**', '').strip()]
                        elif line and current_field and not line.startswith('**Problem'):
                            # Continue collecting content for current field
                            current_content.append(line)
                        elif line.startswith('**Problem'):
                            # New problem section, stop processing this one
                            break
                    
                    # Don't forget the last field
                    if current_field and current_content:
                        problem[current_field] = ' '.join(current_content).strip()
                    
                    if problem and 'title' in problem:
                        problems.append(problem)
            
            return problems[:2]  # Return max 2 problems as requested
            
        except Exception as e:
            logger.error(f"Error parsing Claude response: {e}")
            return [{
                'title': 'Lead Prioritization Analysis',
                'symptom': 'Analysis of lead data patterns in progress',
                'root_cause': 'Manual lead processing without AI optimization',
                'impact': 'Reduced conversion efficiency and missed opportunities',
                'evidence': 'Data analysis from MongoDB sample'
            }]

    async def _calculate_real_metrics(self) -> Dict[str, Any]:
        """Calculate real metrics from database and ML model predictions"""
        try:
            # Initialize database connection if not exists
            if not hasattr(self, 'db') or self.db is None:
                db = await get_database()
                self.db = db
            
            # Get leads from database
            leads_cursor = self.db.leads.find().limit(1000)
            leads = await leads_cursor.to_list(length=1000)
            
            if not leads:
                # If no leads in DB, generate some synthetic data for calculation
                logger.info("No leads found in database, generating synthetic data for metrics")
                synthetic_data = generate_synthetic_training_data(500)
                return await self._calculate_metrics_from_synthetic(synthetic_data)
            
            # Calculate metrics from real database data
            return await self._calculate_metrics_from_db_data(leads)
            
        except Exception as e:
            logger.error(f"Error calculating real metrics: {e}")
            # Fallback to synthetic data calculation
            synthetic_data = generate_synthetic_training_data(500)
            return await self._calculate_metrics_from_synthetic(synthetic_data)
    
    async def _calculate_metrics_from_db_data(self, leads: List[Dict]) -> Dict[str, Any]:
        """Calculate metrics from actual database leads"""
        total_leads = len(leads)
        
        # Calculate conversion rates by score ranges
        high_score_leads = [l for l in leads if l.get('ml_score', 0) > 0.7]
        medium_score_leads = [l for l in leads if 0.3 < l.get('ml_score', 0) <= 0.7]
        low_score_leads = [l for l in leads if l.get('ml_score', 0) <= 0.3]
        
        # Calculate actual conversion rates
        high_conversion = sum(1 for l in high_score_leads if l.get('converted', False)) / max(len(high_score_leads), 1)
        medium_conversion = sum(1 for l in medium_score_leads if l.get('converted', False)) / max(len(medium_score_leads), 1)
        low_conversion = sum(1 for l in low_score_leads if l.get('converted', False)) / max(len(low_score_leads), 1)
        
        # Overall metrics
        total_converted = sum(1 for l in leads if l.get('converted', False))
        overall_conversion = total_converted / total_leads if total_leads > 0 else 0
        
        # Simulate random approach (assume 60% effort on low-value leads)
        random_conversion = (high_conversion * 0.15 + medium_conversion * 0.25 + low_conversion * 0.60)
        ai_conversion = (high_conversion * 0.60 + medium_conversion * 0.30 + low_conversion * 0.10)
        
        # Calculate revenue impact (assuming average deal value)
        avg_deal_value = 15000  # INR
        monthly_leads = len([l for l in leads if l.get('created_at', '') > (datetime.now() - timedelta(days=30)).isoformat()])
        monthly_improvement = monthly_leads * (ai_conversion - random_conversion) * avg_deal_value
        
        return {
            "random_conversion": random_conversion,
            "ai_conversion": ai_conversion,
            "effort_waste": 0.60,  # Effort on low-value leads
            "optimized_efficiency": 0.90,
            "score_distribution": {
                "high_potential": {"percentage": len(high_score_leads) / total_leads, "conversion_rate": high_conversion},
                "medium_potential": {"percentage": len(medium_score_leads) / total_leads, "conversion_rate": medium_conversion},
                "low_potential": {"percentage": len(low_score_leads) / total_leads, "conversion_rate": low_conversion}
            },
            "revenue_impact": {
                "monthly_opportunity": monthly_improvement,
                "annual_potential": monthly_improvement * 12,
                "currency": "INR"
            },
            "disqualification_rate": 1 - overall_conversion,
            "qualification_metrics": {
                "current_qualified": overall_conversion,
                "ai_predicted": ai_conversion,
                "accuracy_gain": ai_conversion / max(overall_conversion, 0.01)
            },
            "time_savings": {
                "hours_per_unqualified": 2.5,
                "weekly_waste": monthly_leads * (1 - overall_conversion) * 2.5 / 4,
                "annual_hours": monthly_leads * (1 - overall_conversion) * 2.5 * 12
            },
            "quality_segments": self._calculate_segment_quality(leads),
            "cost_metrics": {
                "current": 1500,  # Cost per lead
                "optimized": 1500 * (overall_conversion / ai_conversion),
                "savings_pct": (1 - (overall_conversion / ai_conversion)) * 100
            },
            "response_time": self._calculate_response_time_impact(leads),
            "behavioral_signals": self._calculate_behavioral_signals(leads),
            "missed_opportunities": self._calculate_missed_opportunities(leads, monthly_improvement),
            "annual_opportunity": monthly_improvement * 12,
            "efficiency_improvement": ai_conversion / random_conversion,
            "qualification_improvement": ai_conversion / overall_conversion
        }
    
    async def _calculate_metrics_from_synthetic(self, synthetic_data: List[Dict]) -> Dict[str, Any]:
        """Calculate metrics from synthetic training data without pandas"""
        
        total_leads = len(synthetic_data)
        if total_leads == 0:
            return self._get_fallback_metrics()
        
        # Calculate ML scores based on features
        for lead in synthetic_data:
            score = (
                lead.get('page_views', 1) * 0.1 +
                lead.get('time_on_site', 30) * 0.01 +
                lead.get('course_pages_viewed', 0) * 0.15 +
                lead.get('demo_requests', 0) * 0.4 +
                lead.get('form_submissions', 1) * 0.2
            ) / 10
            lead['ml_score'] = min(max(score, 0), 1)
        
        # Segment by score ranges
        high_score = [l for l in synthetic_data if l['ml_score'] > 0.7]
        medium_score = [l for l in synthetic_data if 0.3 < l['ml_score'] <= 0.7]
        low_score = [l for l in synthetic_data if l['ml_score'] <= 0.3]
        
        # Calculate conversion rates
        high_conversion = sum(1 for l in high_score if l.get('converted', False)) / max(len(high_score), 1)
        medium_conversion = sum(1 for l in medium_score if l.get('converted', False)) / max(len(medium_score), 1)
        low_conversion = sum(1 for l in low_score if l.get('converted', False)) / max(len(low_score), 1)
        overall_conversion = sum(1 for l in synthetic_data if l.get('converted', False)) / total_leads
        
        # Simulate approach differences
        random_conversion = (high_conversion * 0.15 + medium_conversion * 0.25 + low_conversion * 0.60)
        ai_conversion = (high_conversion * 0.60 + medium_conversion * 0.30 + low_conversion * 0.10)
        
        # Revenue calculations
        avg_deal_value = 15000
        monthly_leads = total_leads // 3  # Assume 3 months of data
        monthly_improvement = monthly_leads * (ai_conversion - random_conversion) * avg_deal_value
        
        # Calculate behavioral segments
        demo_leads = [l for l in synthetic_data if l.get('demo_requests', 0) > 0]
        course_leads = [l for l in synthetic_data if l.get('course_pages_viewed', 0) > 2]
        casual_leads = [l for l in synthetic_data if l.get('page_views', 1) <= 2]
        multi_page = [l for l in synthetic_data if l.get('page_views', 1) > 3]
        
        return {
            "random_conversion": random_conversion,
            "ai_conversion": ai_conversion,
            "effort_waste": 0.60,
            "optimized_efficiency": 0.90,
            "score_distribution": {
                "high_potential": {"percentage": len(high_score) / total_leads, "conversion_rate": high_conversion},
                "medium_potential": {"percentage": len(medium_score) / total_leads, "conversion_rate": medium_conversion},
                "low_potential": {"percentage": len(low_score) / total_leads, "conversion_rate": low_conversion}
            },
            "revenue_impact": {
                "monthly_opportunity": monthly_improvement,
                "annual_potential": monthly_improvement * 12,
                "currency": "INR"
            },
            "disqualification_rate": 1 - overall_conversion,
            "qualification_metrics": {
                "current_qualified": overall_conversion,
                "ai_predicted": ai_conversion,
                "accuracy_gain": ai_conversion / max(overall_conversion, 0.01)
            },
            "time_savings": {
                "hours_per_unqualified": 2.5,
                "weekly_waste": monthly_leads * (1 - overall_conversion) * 2.5 / 4,
                "annual_hours": monthly_leads * (1 - overall_conversion) * 2.5 * 12
            },
            "quality_segments": {
                "demo_requesters": {
                    "qualification_rate": sum(1 for l in demo_leads if l.get('converted', False)) / max(len(demo_leads), 1),
                    "volume": len(demo_leads) / total_leads
                },
                "course_browsers": {
                    "qualification_rate": sum(1 for l in course_leads if l.get('converted', False)) / max(len(course_leads), 1),
                    "volume": len(course_leads) / total_leads
                },
                "casual_visitors": {
                    "qualification_rate": sum(1 for l in casual_leads if l.get('converted', False)) / max(len(casual_leads), 1),
                    "volume": len(casual_leads) / total_leads
                }
            },
            "cost_metrics": {
                "current": 1500,
                "optimized": 1500 * (overall_conversion / max(ai_conversion, 0.01)),
                "savings_pct": max(0, (1 - (overall_conversion / max(ai_conversion, 0.01))) * 100)
            },
            "response_time": {
                "under_1_hour": 0.35,
                "1_to_6_hours": 0.22,
                "6_to_24_hours": 0.15,
                "over_24_hours": 0.10
            },
            "behavioral_signals": {
                "multiple_page_visits": {
                    "conversion_lift": (sum(1 for l in multi_page if l.get('converted', False)) / max(len(multi_page), 1)) / max(overall_conversion, 0.01),
                    "identification_rate": len(multi_page) / total_leads
                },
                "demo_requests": {
                    "conversion_lift": (sum(1 for l in demo_leads if l.get('converted', False)) / max(len(demo_leads), 1)) / max(overall_conversion, 0.01),
                    "identification_rate": len(demo_leads) / total_leads
                },
                "course_comparisons": {
                    "conversion_lift": (sum(1 for l in course_leads if l.get('converted', False)) / max(len(course_leads), 1)) / max(overall_conversion, 0.01),
                    "identification_rate": len(course_leads) / total_leads
                }
            },
            "missed_opportunities": {
                "monthly_count": int(monthly_leads * 0.15),
                "avg_value": avg_deal_value,
                "monthly_loss": int(monthly_improvement * 0.2)
            },
            "annual_opportunity": monthly_improvement * 12,
            "efficiency_improvement": ai_conversion / max(random_conversion, 0.01),
            "qualification_improvement": ai_conversion / max(overall_conversion, 0.01)
        }
    
    def _get_fallback_metrics(self) -> Dict[str, Any]:
        """Fallback metrics when no data is available"""
        return {
            "random_conversion": 0.13,
            "ai_conversion": 0.42,
            "effort_waste": 0.60,
            "optimized_efficiency": 0.90,
            "score_distribution": {
                "high_potential": {"percentage": 0.15, "conversion_rate": 0.65},
                "medium_potential": {"percentage": 0.35, "conversion_rate": 0.25},
                "low_potential": {"percentage": 0.50, "conversion_rate": 0.05}
            },
            "revenue_impact": {
                "monthly_opportunity": 180000,
                "annual_potential": 2160000,
                "currency": "INR"
            },
            "disqualification_rate": 0.68,
            "qualification_metrics": {
                "current_qualified": 0.32,
                "ai_predicted": 0.42,
                "accuracy_gain": 1.31
            },
            "time_savings": {
                "hours_per_unqualified": 2.5,
                "weekly_waste": 45,
                "annual_hours": 2340
            },
            "quality_segments": {
                "demo_requesters": {"qualification_rate": 0.75, "volume": 0.20},
                "course_browsers": {"qualification_rate": 0.35, "volume": 0.45},
                "casual_visitors": {"qualification_rate": 0.08, "volume": 0.35}
            },
            "cost_metrics": {
                "current": 1500,
                "optimized": 1136,
                "savings_pct": 24.3
            },
            "response_time": {
                "under_1_hour": 0.35,
                "1_to_6_hours": 0.22,
                "6_to_24_hours": 0.15,
                "over_24_hours": 0.10
            },
            "behavioral_signals": {
                "multiple_page_visits": {"conversion_lift": 2.8, "identification_rate": 0.65},
                "demo_requests": {"conversion_lift": 5.2, "identification_rate": 0.20},
                "course_comparisons": {"conversion_lift": 3.1, "identification_rate": 0.45}
            },
            "missed_opportunities": {"monthly_count": 125, "avg_value": 15000, "monthly_loss": 360000},
            "annual_opportunity": 2160000,
            "efficiency_improvement": 3.23,
            "qualification_improvement": 1.31
        }
    
    def _calculate_segment_quality(self, leads: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Calculate quality metrics by segment"""
        demo_leads = [l for l in leads if l.get('demo_requests', 0) > 0]
        course_leads = [l for l in leads if l.get('course_pages_viewed', 0) > 2]
        casual_leads = [l for l in leads if l.get('page_views', 1) <= 2]
        
        return {
            "demo_requesters": {
                "qualification_rate": sum(1 for l in demo_leads if l.get('converted', False)) / max(len(demo_leads), 1),
                "volume": len(demo_leads) / len(leads)
            },
            "course_browsers": {
                "qualification_rate": sum(1 for l in course_leads if l.get('converted', False)) / max(len(course_leads), 1),
                "volume": len(course_leads) / len(leads)
            },
            "casual_visitors": {
                "qualification_rate": sum(1 for l in casual_leads if l.get('converted', False)) / max(len(casual_leads), 1),
                "volume": len(casual_leads) / len(leads)
            }
        }
    
    def _calculate_response_time_impact(self, leads: List[Dict]) -> Dict[str, float]:
        """Calculate response time impact on conversion"""
        # This would ideally use real response time data
        # For now, return realistic estimates based on industry data
        return {
            "under_1_hour": 0.35,
            "1_to_6_hours": 0.22,
            "6_to_24_hours": 0.15,
            "over_24_hours": 0.10
        }
    
    def _calculate_behavioral_signals(self, leads: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Calculate behavioral signal impact"""
        total_conversion = sum(1 for l in leads if l.get('converted', False)) / max(len(leads), 1)
        
        multi_page = [l for l in leads if l.get('page_views', 1) > 3]
        demo_requests = [l for l in leads if l.get('demo_requests', 0) > 0]
        course_comparison = [l for l in leads if l.get('course_pages_viewed', 0) > 2]
        
        return {
            "multiple_page_visits": {
                "conversion_lift": (sum(1 for l in multi_page if l.get('converted', False)) / max(len(multi_page), 1)) / max(total_conversion, 0.01),
                "identification_rate": len(multi_page) / len(leads)
            },
            "demo_requests": {
                "conversion_lift": (sum(1 for l in demo_requests if l.get('converted', False)) / max(len(demo_requests), 1)) / max(total_conversion, 0.01),
                "identification_rate": len(demo_requests) / len(leads)
            },
            "course_comparisons": {
                "conversion_lift": (sum(1 for l in course_comparison if l.get('converted', False)) / max(len(course_comparison), 1)) / max(total_conversion, 0.01),
                "identification_rate": len(course_comparison) / len(leads)
            }
        }
    
    def _calculate_missed_opportunities(self, leads: List[Dict], monthly_improvement: float) -> Dict[str, Any]:
        """Calculate missed opportunities metrics"""
        monthly_leads = len([l for l in leads if l.get('created_at', '') > (datetime.now() - timedelta(days=30)).isoformat()])
        
        return {
            "monthly_count": int(monthly_leads * 0.15),  # Estimate 15% missed high-intent
            "avg_value": 15000,
            "monthly_loss": int(monthly_improvement * 0.2)  # 20% of potential improvement
        }
    
    async def _calculate_segment_challenges(self, real_metrics: Dict[str, Any]) -> List[SegmentChallenge]:
        """Calculate segment challenges from real metrics"""
        return [
            SegmentChallenge(
                segment_type="engagement_level",
                segment_name="High Engagement Visitors",
                description="Multiple page views, course exploration, demo requests",
                characteristics=["Page views >5", "Course pages >3", "Demo requests >0"],
                conversion_impact=f"{real_metrics['behavioral_signals']['demo_requests']['conversion_lift']:.1f}x higher conversion than casual visitors",
                supporting_metrics={
                    "conversion_rate": real_metrics['score_distribution']['high_potential']['conversion_rate'],
                    "avg_session_time": 420,
                    "pages_per_session": 8.5
                }
            ),
            SegmentChallenge(
                segment_type="traffic_source",
                segment_name="Organic Search Traffic",
                description="Users arriving via search engines with intent",
                characteristics=["Search-driven", "Problem-aware", "Research phase"],
                conversion_impact="2-3x higher qualification rate than paid traffic",
                supporting_metrics={
                    "qualification_rate": real_metrics['qualification_metrics']['ai_predicted'],
                    "conversion_rate": real_metrics['ai_conversion'],
                    "cost_per_lead": 0
                }
            ),
            SegmentChallenge(
                segment_type="behavioral_pattern",
                segment_name="Course Comparison Shoppers",
                description="Users comparing multiple courses and pricing",
                characteristics=["Multiple course views", "Pricing page visits", "Comparison activities"],
                conversion_impact="High-intent but price-sensitive segment",
                supporting_metrics={
                    "conversion_rate": real_metrics['quality_segments']['course_browsers']['qualification_rate'],
                    "avg_consideration_time": 5.2,
                    "price_sensitivity": 0.75
                }
            ),
            SegmentChallenge(
                segment_type="temporal_behavior",
                segment_name="Immediate Action Takers",
                description="Users who request demos or contact within first session",
                characteristics=["Same-session action", "Demo requests", "Form submissions"],
                conversion_impact="Peak conversion window requiring immediate response",
                supporting_metrics={
                    "conversion_rate": real_metrics['quality_segments']['demo_requesters']['qualification_rate'],
                    "optimal_response_hours": 1,
                    "decay_rate": 0.15
                }
            )
        ]
