"""
HotLead AI System - Lead Scoring and Conversion Prediction Model
MongoDB Integration for Odin-School
"""
import numpy as np
import logging
from typing import Dict, Any, List
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from ml.base_model import BaseMLModel

logger = logging.getLogger(__name__)

class HotLeadModel(BaseMLModel):
    """
    Lead conversion prediction model using Random Forest - MongoDB version
    
    Features considered:
    - Lead source (organic, paid, referral, social)
    - Page views count
    - Time spent on site (seconds)
    - Course pages viewed
    - Download activity (brochure, syllabus)
    - Contact form submissions
    - Demo/trial requests
    - Geographic location score
    - Device type (mobile, desktop, tablet)
    - Time of day (business hours vs off-hours)
    - Day of week (weekday vs weekend)
    - Previous website visits
    """
    
    def __init__(self):
        super().__init__("hotlead_conversion", "classification")
        
        # Define feature columns matching PRD requirements
        self.feature_columns = [
            # Behavioral features
            "page_views", "time_on_site", "session_duration", "course_pages_viewed", 
            "downloads_count", "form_submissions", "demo_requests", "previous_visits",
            
            # Source and channel features
            "source_score", "utm_campaign_score", "utm_medium_score",
            
            # Geographic and demographic features
            "geo_score", "device_score", "location_quality_score",
            
            # Timing features
            "time_score", "day_score", "is_business_hours_score",
            
            # Intent and engagement features
            "return_visitor_score", "intent_score", "behavior_score",
            
            # Channel performance features
            "response_time_score", "source_quality_score"
        ]
        
        logger.info("HotLead conversion prediction model initialized")
    
    def prepare_features(self, data: Dict[str, Any]) -> np.ndarray:
        """
        Convert lead data into feature vector for ML model
        Enhanced to handle all PRD data points
        
        Args:
            data: Lead data dictionary containing comprehensive behavior and demographic info
            
        Returns:
            numpy array of features ready for model input
        """
        try:
            features = []
            
            # Behavioral features
            features.append(float(data.get("page_views", 1)))
            features.append(float(data.get("time_on_site", 30)))
            features.append(float(data.get("session_duration", data.get("time_on_site", 30))))
            features.append(float(data.get("course_pages_viewed", 0)))
            features.append(float(data.get("downloads_count", 0)))
            features.append(float(data.get("form_submissions", 0)))
            features.append(float(data.get("demo_requests", 0)))
            features.append(float(data.get("previous_visits", 1)))
            
            # Source and UTM scoring (enhanced for more sources)
            source = data.get("source", "unknown").lower()
            source_scores = {
                "referral": 0.95, "organic": 0.85, "direct": 0.80, "paid_search": 0.75,
                "email": 0.70, "social_paid": 0.65, "social_organic": 0.60, 
                "display": 0.45, "unknown": 0.30
            }
            features.append(source_scores.get(source, 0.30))
            
            # UTM Campaign scoring
            utm_campaign = data.get("utm_campaign", "").lower()
            campaign_scores = {
                "brand_awareness": 0.6, "course_launch": 0.8, "retargeting": 0.9,
                "competitor": 0.7, "skill_development": 0.75, "career_switch": 0.85,
                "student_referral": 0.95, "placement_guarantee": 0.9, "free_workshop": 0.8
            }
            campaign_score = 0.5  # default
            for campaign_type, score in campaign_scores.items():
                if campaign_type in utm_campaign:
                    campaign_score = score
                    break
            features.append(campaign_score)
            
            # UTM Medium scoring
            utm_medium = data.get("utm_medium", "").lower()
            medium_scores = {
                "cpc": 0.8, "organic": 0.85, "email": 0.7, "social": 0.6,
                "referral": 0.9, "display": 0.4, "affiliate": 0.75
            }
            features.append(medium_scores.get(utm_medium, 0.5))
            
            # Geographic scoring
            location = data.get("location", "").lower()
            geo_scores = {
                "bangalore": 0.9, "mumbai": 0.85, "delhi": 0.8, "hyderabad": 0.85,
                "pune": 0.8, "chennai": 0.75, "gurgaon": 0.9, "jaipur": 0.85,
                "ahmedabad": 0.65, "kolkata": 0.7, "kochi": 0.7
            }
            geo_score = 0.5  # default
            for city, score in geo_scores.items():
                if city in location:
                    geo_score = score
                    break
            features.append(geo_score)
            
            # Device scoring
            device = data.get("device", "desktop").lower()
            device_scores = {"desktop": 0.8, "mobile": 0.6, "tablet": 0.7}
            features.append(device_scores.get(device, 0.7))
            
            # Location quality score
            features.append(float(data.get("location_quality_score", geo_score)))
            
            # Timing features
            hour = data.get("hour", 12)
            # Business hours score (9 AM to 6 PM gets higher score)
            time_score = 0.8 if 9 <= hour <= 18 else 0.5
            features.append(time_score)
            
            # Day of week score (weekdays get higher score)
            day_of_week = data.get("day_of_week", 3)
            day_score = 0.8 if 1 <= day_of_week <= 5 else 0.6
            features.append(day_score)
            
            # Business hours indicator
            is_business_hours = data.get("is_business_hours", True)
            features.append(1.0 if is_business_hours else 0.5)
            
            # Return visitor score
            is_return_visitor = data.get("is_return_visitor", False)
            features.append(1.0 if is_return_visitor else 0.3)
            
            # Intent score (based on demo requests and downloads)
            intent_score = min(1.0, (data.get("demo_requests", 0) * 0.5 + 
                                   data.get("downloads_count", 0) * 0.2 + 
                                   data.get("form_submissions", 0) * 0.3))
            features.append(intent_score)
            
            # Behavior score (engagement level)
            behavior_score = min(1.0, (
                data.get("page_views", 1) / 10.0 +
                data.get("time_on_site", 30) / 600.0 +
                data.get("course_pages_viewed", 0) / 5.0
            ) / 3.0)
            features.append(behavior_score)
            
            # Response time score (lower is better)
            avg_response_time = data.get("avg_response_time_hours", 6)
            response_time_score = max(0.1, 1.0 - (avg_response_time / 24.0))
            features.append(response_time_score)
            
            # Source quality score
            source_quality = data.get("source_quality_score", source_scores.get(source, 0.5))
            features.append(source_quality)
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Failed to prepare features for HotLead model: {str(e)}")
            logger.error(f"Data keys: {list(data.keys()) if data else 'None'}")
            return None
    
    def _create_model(self):
        """Create Random Forest classifier for lead conversion prediction"""
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced'  # Handle imbalanced conversion rates
        )
    
    def generate_lead_insights(self, prediction_result: Dict[str, Any], lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate actionable insights for the lead
        
        Args:
            prediction_result: Model prediction output
            lead_data: Original lead data
            
        Returns:
            Dictionary with insights and recommendations
        """
        conversion_probability = prediction_result.get("probabilities", {}).get("True", 0.0)
        
        # Determine lead temperature
        if conversion_probability >= 0.8:
            temperature = "🔥 HOT"
            priority = "HIGH"
            action = "Contact immediately via phone"
        elif conversion_probability >= 0.6:
            temperature = "🟡 WARM"
            priority = "MEDIUM"
            action = "Send personalized email within 2 hours"
        elif conversion_probability >= 0.4:
            temperature = "🟦 COOL"
            priority = "LOW"
            action = "Add to nurturing campaign"
        else:
            temperature = "❄️ COLD"
            priority = "VERY LOW"
            action = "Add to long-term drip campaign"
        
        # Generate specific recommendations
        recommendations = []
        
        if lead_data.get("course_pages_viewed", 0) == 0:
            recommendations.append("Show course curriculum and success stories")
        
        if lead_data.get("demo_requests", 0) == 0:
            recommendations.append("Offer free demo or trial class")
        
        if lead_data.get("downloads_count", 0) == 0:
            recommendations.append("Provide course brochure and placement reports")
        
        if lead_data.get("time_on_site", 0) < 120:  # Less than 2 minutes
            recommendations.append("Send engaging video content to increase engagement")
        
        # Calculate urgency score
        urgency_factors = []
        if lead_data.get("demo_requests", 0) > 0:
            urgency_factors.append("Requested demo")
        if lead_data.get("form_submissions", 0) > 1:
            urgency_factors.append("Multiple form submissions")
        if lead_data.get("course_pages_viewed", 0) > 3:
            urgency_factors.append("Viewed multiple courses")
        
        return {
            "lead_temperature": temperature,
            "priority": priority,
            "conversion_probability": round(conversion_probability * 100, 1),
            "recommended_action": action,
            "recommendations": recommendations[:3],  # Top 3 recommendations
            "urgency_factors": urgency_factors,
            "follow_up_timing": "Within 1 hour" if conversion_probability >= 0.7 else "Within 24 hours",
            "expected_conversion_timeframe": "1-3 days" if conversion_probability >= 0.6 else "1-2 weeks"
        }

# Global model instance
hotlead_model = HotLeadModel()

async def predict_lead_conversion(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to predict lead conversion and generate insights
    
    Args:
        lead_data: Dictionary containing lead information
        
    Returns:
        Complete prediction result with insights
    """
    try:
        # Make prediction
        prediction_result = await hotlead_model.predict(lead_data)
        
        # Generate insights
        insights = hotlead_model.generate_lead_insights(prediction_result, lead_data)
        
        # Combine results
        return {
            "prediction": prediction_result,
            "insights": insights,
            "model_info": {
                "model_name": "HotLead Conversion Predictor",
                "version": "1.0.0",
                "confidence_threshold": 0.6
            }
        }
        
    except Exception as e:
        logger.error(f"Lead conversion prediction failed: {str(e)}")
        # Return default response if prediction fails
        return {
            "prediction": {
                "prediction": "Unknown",
                "confidence": 0.5,
                "model_name": "hotlead_conversion"
            },
            "insights": {
                "lead_temperature": "🟦 COOL",
                "priority": "MEDIUM",
                "conversion_probability": 50.0,
                "recommended_action": "Add to nurturing campaign",
                "recommendations": ["Engage with educational content"],
                "urgency_factors": [],
                "follow_up_timing": "Within 24 hours"
            },
            "error": str(e)
        }

def generate_synthetic_training_data(num_samples: int = 5000) -> List[Dict[str, Any]]:
    """
    Load enhanced training data from CSV or generate fallback data
    Uses the realistic 5000-lead dataset created by enhanced generator
    """
    import pandas as pd
    import os
    
    # Try to load the enhanced dataset first
    enhanced_data_path = "/Users/batman/Movies/odinschool/Odin-School/backend/data/enhanced_leads_5000.csv"
    
    try:
        if os.path.exists(enhanced_data_path):
            logger.info("Loading enhanced 5000-lead dataset from CSV...")
            df = pd.read_csv(enhanced_data_path)
            
            # Convert DataFrame to list of dictionaries
            training_data = []
            for _, row in df.iterrows():
                lead_data = {
                    "lead_id": row["lead_id"],
                    "source": row["source"],
                    "utm_source": row["utm_source"],
                    "utm_medium": row["utm_medium"],
                    "utm_campaign": row["utm_campaign"],
                    "page_views": int(row["page_views"]),
                    "time_on_site": int(row["time_on_site"]),
                    "course_pages_viewed": int(row["course_pages_viewed"]),
                    "demo_requests": int(row["demo_requests"]),
                    "device": row["device"],
                    "location": row["geography"],
                    "geography": row["geography"],
                    "hour": int(row["contact_hour"]),
                    "day_of_week": int(row["contact_day"]),
                    "is_business_hours": 9 <= int(row["contact_hour"]) <= 17 and 1 <= int(row["contact_day"]) <= 5,
                    "session_count": int(row["session_count"]),
                    "days_since_first_visit": int(row["days_since_first_visit"]),
                    "form_submissions": int(row["form_submissions"]),
                    "is_return_visitor": row["session_count"] > 1,
                    "downloads_count": 0,  # Will derive from other features
                    "previous_visits": int(row["session_count"]),
                    "contacted": row["contacted"],
                    "meeting_booked": row["meeting_scheduled"],
                    "enrolled": row["enrolled"],
                    "converted": row["enrolled"],  # Primary target
                    "revenue": int(row["revenue"]) if row["revenue"] > 0 else 0,
                    "rep_assigned": row["rep_assigned"],
                    "rep_experience_level": row["rep_experience_level"],
                    "response_time_hours": float(row["response_time_hours"]),
                    "contact_attempts": int(row["contact_attempts"]),
                    "lost_reason": row["lost_reason"] if row["lost_reason"] else "",
                    "objection_type": row["objection_type"] if row["objection_type"] else "",
                    
                    # Derived features for ML model
                    "avg_response_time_hours": float(row["response_time_hours"]),
                    "source_quality_score": 0.8,  # Will calculate dynamically
                    "location_quality_score": 0.7,  # Will calculate dynamically
                    "intent_score": min(1.0, (int(row["demo_requests"]) * 0.5 + int(row["course_pages_viewed"]) * 0.1)),
                    "behavior_score": min(1.0, int(row["page_views"]) / 10.0),
                    "lead_score": 75,  # Will calculate from ML model
                    "priority": "MEDIUM"  # Will calculate from conversion probability
                }
                training_data.append(lead_data)
            
            logger.info(f"✅ Loaded {len(training_data)} enhanced leads from CSV")
            
            # Print dataset statistics
            converted_count = len([d for d in training_data if d["converted"]])
            contacted_count = len([d for d in training_data if d["contacted"]])
            meeting_count = len([d for d in training_data if d["meeting_booked"]])
            total_revenue = sum(d["revenue"] for d in training_data)
            
            logger.info(f"Enhanced Dataset Statistics:")
            logger.info(f"  - Total leads: {len(training_data)}")
            logger.info(f"  - Converted: {converted_count} ({converted_count/len(training_data)*100:.1f}%)")
            logger.info(f"  - Contacted: {contacted_count} ({contacted_count/len(training_data)*100:.1f}%)")
            logger.info(f"  - Meetings: {meeting_count} ({meeting_count/len(training_data)*100:.1f}%)")
            logger.info(f"  - Total Revenue: ₹{total_revenue:,}")
            
            # Show source distribution
            source_counts = {}
            for lead in training_data:
                source = lead["source"]
                source_counts[source] = source_counts.get(source, 0) + 1
            
            logger.info("Source distribution:")
            for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
                pct = count / len(training_data) * 100
                logger.info(f"  - {source}: {count} ({pct:.1f}%)")
            
            return training_data
            
        else:
            logger.warning(f"Enhanced dataset not found at {enhanced_data_path}")
            logger.info("Falling back to synthetic data generation...")
            
    except Exception as e:
        logger.error(f"Error loading enhanced dataset: {e}")
        logger.info("Falling back to synthetic data generation...")
    
    # Fallback to original synthetic data generation
    return generate_original_synthetic_data(num_samples)


def generate_original_synthetic_data(num_samples: int = 2000) -> List[Dict[str, Any]]:
    """
    Generate comprehensive synthetic training data for the HotLead model
    Following PRD requirements with 1500-2000 samples covering all lead scenarios
    """
    import random
    from datetime import datetime, timedelta
    
    training_data = []
    
    # Enhanced data distributions based on real EdTech patterns
    sources = {
        "organic": {"quality": 0.85, "volume": 0.25, "avg_cpl": 450},
        "paid_search": {"quality": 0.75, "volume": 0.20, "avg_cpl": 650},
        "social_paid": {"quality": 0.65, "volume": 0.15, "avg_cpl": 550},
        "referral": {"quality": 0.90, "volume": 0.10, "avg_cpl": 200},
        "direct": {"quality": 0.80, "volume": 0.12, "avg_cpl": 300},
        "email": {"quality": 0.70, "volume": 0.08, "avg_cpl": 400},
        "social_organic": {"quality": 0.60, "volume": 0.06, "avg_cpl": 500},
        "display": {"quality": 0.45, "volume": 0.04, "avg_cpl": 800}
    }
    
    utm_campaigns = [
        "brand_awareness_q4", "course_launch_python", "retargeting_visitors",
        "competitor_keywords", "skill_development", "career_switch",
        "student_referral", "placement_guarantee", "free_workshop"
    ]
    
    utm_mediums = ["cpc", "social", "email", "organic", "referral", "display", "affiliate"]
    
    device_types = {
        "desktop": {"conversion_rate": 0.12, "engagement": 1.2},
        "mobile": {"conversion_rate": 0.08, "engagement": 0.8},
        "tablet": {"conversion_rate": 0.10, "engagement": 1.0}
    }
    
    # Geographic regions with different conversion patterns (Indian cities)
    locations = {
        "Bangalore, India": {"quality": 0.90, "income_level": "high"},
        "Mumbai, India": {"quality": 0.85, "income_level": "high"},
        "Delhi, India": {"quality": 0.80, "income_level": "medium"},
        "Hyderabad, India": {"quality": 0.85, "income_level": "high"},
        "Pune, India": {"quality": 0.80, "income_level": "medium"},
        "Chennai, India": {"quality": 0.75, "income_level": "medium"},
        "Kolkata, India": {"quality": 0.70, "income_level": "medium"},
        "Ahmedabad, India": {"quality": 0.65, "income_level": "medium"},
        "Kochi, India": {"quality": 0.70, "income_level": "medium"},
        "Chandigarh, India": {"quality": 0.75, "income_level": "medium"},
        "Jaipur, India": {"quality": 0.85, "income_level": "high"},
        "Gurgaon, India": {"quality": 0.90, "income_level": "high"},
        "Indore, India": {"quality": 0.80, "income_level": "high"},
        "Mysore, India": {"quality": 0.85, "income_level": "high"},
        "Visakhapatnam, India": {"quality": 0.80, "income_level": "high"},
        "Goa, India": {"quality": 0.75, "income_level": "high"}
    }
    
    # Course categories that leads might be interested in
    course_interests = [
        "python_fullstack", "data_science", "machine_learning", "web_development",
        "cloud_computing", "cybersecurity", "mobile_development", "devops",
        "artificial_intelligence", "blockchain", "digital_marketing", "ui_ux_design"
    ]
    
    # Lost reason categories (for leads that don't convert)
    lost_reasons = [
        "price_too_high", "timing_not_right", "course_not_suitable", 
        "competitor_chosen", "no_response", "technical_issues",
        "location_constraint", "schedule_conflict", "budget_constraint",
        "career_change_decision", "company_training", "other_priorities"
    ]
    
    for i in range(num_samples):
        # Determine lead quality tier (high, medium, low intent)
        quality_tier = random.choices(
            ["high_intent", "medium_intent", "low_intent"],
            weights=[0.25, 0.45, 0.30]
        )[0]
        
        # Select source based on realistic distributions
        source = random.choices(
            list(sources.keys()),
            weights=[sources[s]["volume"] for s in sources.keys()]
        )[0]
        
        source_quality = sources[source]["quality"]
        
        # Generate UTM parameters
        utm_campaign = random.choice(utm_campaigns)
        utm_medium = random.choice(utm_mediums)
        
        # Device and location
        device = random.choices(
            list(device_types.keys()),
            weights=[0.55, 0.35, 0.10]  # Desktop-heavy for educational content
        )[0]
        
        location = random.choice(list(locations.keys()))
        location_quality = locations[location]["quality"]
        
        # Time-based factors
        hour = random.randint(0, 23)
        day_of_week = random.randint(1, 7)  # 1=Monday, 7=Sunday
        is_business_hours = 9 <= hour <= 18 and 1 <= day_of_week <= 5
        
        # Generate behavioral data based on intent level
        if quality_tier == "high_intent":
            page_views = random.randint(8, 25)
            time_on_site = random.randint(600, 2400)  # 10-40 minutes
            session_duration = random.randint(400, 1800)
            course_pages_viewed = random.randint(3, 8)
            downloads_count = random.randint(2, 5)
            form_submissions = random.randint(1, 3)
            demo_requests = random.randint(1, 2)
            previous_visits = random.randint(2, 8)
            is_return_visitor = True
            
        elif quality_tier == "medium_intent":
            page_views = random.randint(4, 12)
            time_on_site = random.randint(180, 900)  # 3-15 minutes
            session_duration = random.randint(120, 600)
            course_pages_viewed = random.randint(1, 4)
            downloads_count = random.randint(0, 2)
            form_submissions = random.randint(0, 2)
            demo_requests = random.randint(0, 1)
            previous_visits = random.randint(1, 4)
            is_return_visitor = random.choice([True, False])
            
        else:  # low_intent
            page_views = random.randint(1, 6)
            time_on_site = random.randint(30, 300)  # 30 seconds - 5 minutes
            session_duration = random.randint(30, 180)
            course_pages_viewed = random.randint(0, 2)
            downloads_count = random.randint(0, 1)
            form_submissions = random.randint(0, 1)
            demo_requests = 0
            previous_visits = random.randint(0, 2)
            is_return_visitor = False
        
        # Calculate conversion probability
        base_probability = 0.1
        intent_multiplier = {"high_intent": 3.0, "medium_intent": 1.5, "low_intent": 0.5}[quality_tier]
        source_multiplier = source_quality
        location_multiplier = location_quality
        device_multiplier = device_types[device]["conversion_rate"] / 0.10
        timing_multiplier = 1.3 if is_business_hours else 0.8
        behavior_score = min(1.0, (page_views / 10 + time_on_site / 1000 + downloads_count / 3) / 3)
        behavior_multiplier = 1 + behavior_score
        
        conversion_probability = min(0.95, base_probability * intent_multiplier * source_multiplier * 
                                   location_multiplier * device_multiplier * timing_multiplier * behavior_multiplier)
        
        # Determine outcomes
        converted = random.random() < conversion_probability
        contacted = random.random() < (conversion_probability + 0.3)
        meeting_booked = converted or (contacted and random.random() < 0.4)
        enrolled = converted
        
        # Create lead record
        lead_data = {
            "lead_id": f"LEAD_{datetime.now().strftime('%Y%m%d')}_{i:04d}",
            "created_at": (datetime.now() - timedelta(days=random.randint(0, 90))).isoformat(),
            "source": source,
            "utm_campaign": utm_campaign,
            "utm_medium": utm_medium,
            "page_views": page_views,
            "time_on_site": time_on_site,
            "session_duration": session_duration,
            "course_pages_viewed": course_pages_viewed,
            "downloads_count": downloads_count,
            "previous_visits": previous_visits,
            "is_return_visitor": is_return_visitor,
            "form_submissions": form_submissions,
            "demo_requests": demo_requests,
            "device": device,
            "location": location,
            "geography": location,
            "hour": hour,
            "day_of_week": day_of_week,
            "is_business_hours": is_business_hours,
            "course_interest": random.choice(course_interests),
            "quality_tier": quality_tier,
            "source_quality_score": source_quality,
            "location_quality_score": location_quality,
            "contacted": contacted,
            "meeting_booked": meeting_booked,
            "enrolled": enrolled,
            "converted": converted,
            "conversion_probability": conversion_probability,
            "intent_score": intent_multiplier / 3.0,
            "behavior_score": behavior_score,
            "lead_score": min(100, conversion_probability * 100),
            "priority": "HIGH" if conversion_probability > 0.7 else ("MEDIUM" if conversion_probability > 0.4 else "LOW")
        }
        
        training_data.append(lead_data)
    
    # Log statistics
    converted_count = len([d for d in training_data if d["converted"]])
    contacted_count = len([d for d in training_data if d["contacted"]])
    meeting_count = len([d for d in training_data if d["meeting_booked"]])
    
    logger.info(f"Generated {num_samples} training samples:")
    logger.info(f"  - Converted: {converted_count} ({converted_count/num_samples*100:.1f}%)")
    logger.info(f"  - Contacted: {contacted_count} ({contacted_count/num_samples*100:.1f}%)")
    logger.info(f"  - Meeting Booked: {meeting_count} ({meeting_count/num_samples*100:.1f}%)")
    
    return training_data
