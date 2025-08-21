"""
FirstTouch - AI-Powered Sales Call Optimization using XGBoost

Provides:
- FirstTouchModel (BaseMLModel subclass)
- generate_synthetic_training_data(num_samples=2000)
- predict_call_success(lead_data)
- generate_call_script(lead_data, prediction)
"""
from __future__ import annotations

from typing import Any, Dict, List
import logging
import random
import numpy as np
from datetime import datetime, timedelta

from xgboost import XGBClassifier
from ml.base_model import BaseMLModel

logger = logging.getLogger(__name__)


# Feature schema used by FirstTouch
FEATURES = [
    # Lead Characteristics
    "lead_source_score",           # 0.0 - 1.0 (organic=0.9, paid=0.7, social=0.6)
    "lead_intent_score",           # 0.0 - 1.0 (demo_request=0.9, inquiry=0.7, browse=0.4)
    "lead_urgency_score",          # 0.0 - 1.0 (immediate=0.9, soon=0.6, exploring=0.3)
    "geography_score",             # 0.0 - 1.0 (metro=0.8, tier2=0.6, rural=0.4)
    "device_type_score",           # 0.0 - 1.0 (desktop=0.8, mobile=0.6)
    
    # Timing Features
    "time_since_inquiry_minutes",  # 0-1440 minutes (24 hours)
    "call_time_hour",              # 9-21 (business hours)
    "day_of_week",                 # 1-7 (Monday=1)
    "is_peak_hours",               # 10-12, 14-17 = 1, else = 0
    "seasonal_factor",             # 0.8-1.2 admission season boost
    
    # Agent/System Features
    "agent_experience_months",     # 1-60 months
    "script_quality_score",        # 0.3-1.0 (standardized vs custom)
    "call_capacity_ratio",         # 0.0-1.0 current_calls/max_capacity
    "system_load_factor",          # 0.5-1.5 based on concurrent volume
    
    # Historical Features
    "similar_lead_success_rate",   # 0.0-1.0 conversion rate for similar profiles
    "previous_attempt_count",      # 0-5 previous attempts
    "lead_engagement_score",       # 0.0-1.0 email opens, page views, downloads
    
    # Cost/ROI Features
    "estimated_ltv",               # 15000-50000 customer lifetime value estimate
    "call_cost_per_minute",        # 2-8 telephony cost in INR
    "agent_cost_per_minute",       # 5-15 human agent cost vs AI
]


class FirstTouchModel(BaseMLModel):
    def __init__(self, model_name: str = "firsttouch_call_optimization"):
        super().__init__(model_name=model_name, model_type="classification")
        self.feature_columns = FEATURES

    def _create_model(self):
        # XGBoost optimized for call success prediction
        return XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_lambda=1.5,
            reg_alpha=0.5,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
            n_jobs=2,
            scale_pos_weight=4.5,  # Handle imbalanced data (18% success rate)
        )

    def prepare_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Convert lead and call data into feature vector"""
        def safe_float(v: Any, default: float = 0.0) -> float:
            try:
                return float(v)
            except (ValueError, TypeError):
                return default

        vals: List[float] = [
            safe_float(data.get("lead_source_score", 0.7)),
            safe_float(data.get("lead_intent_score", 0.6)),
            safe_float(data.get("lead_urgency_score", 0.5)),
            safe_float(data.get("geography_score", 0.6)),
            safe_float(data.get("device_type_score", 0.7)),
            safe_float(data.get("time_since_inquiry_minutes", 120)),
            safe_float(data.get("call_time_hour", 14)),
            safe_float(data.get("day_of_week", 3)),
            safe_float(data.get("is_peak_hours", 1)),
            safe_float(data.get("seasonal_factor", 1.0)),
            safe_float(data.get("agent_experience_months", 12)),
            safe_float(data.get("script_quality_score", 0.7)),
            safe_float(data.get("call_capacity_ratio", 0.6)),
            safe_float(data.get("system_load_factor", 1.0)),
            safe_float(data.get("similar_lead_success_rate", 0.2)),
            safe_float(data.get("previous_attempt_count", 0)),
            safe_float(data.get("lead_engagement_score", 0.5)),
            safe_float(data.get("estimated_ltv", 25000)),
            safe_float(data.get("call_cost_per_minute", 4)),
            safe_float(data.get("agent_cost_per_minute", 8)),
        ]
        return np.array(vals, dtype=float)


firsttouch_model = FirstTouchModel()


def _calculate_call_success_probability(row: Dict[str, Any]) -> float:
    """Heuristic to generate synthetic label based on call timing and lead quality"""
    
    # Base success rate from lead quality
    lead_quality = (
        float(row["lead_source_score"]) * 0.3 +
        float(row["lead_intent_score"]) * 0.4 +
        float(row["lead_urgency_score"]) * 0.3
    )
    
    # Timing penalty - critical for speed-to-lead
    time_since_inquiry = float(row["time_since_inquiry_minutes"])
    if time_since_inquiry <= 5:
        timing_factor = 1.0  # Golden window
    elif time_since_inquiry <= 15:
        timing_factor = 0.8  # Still good
    elif time_since_inquiry <= 60:
        timing_factor = 0.6  # Acceptable
    elif time_since_inquiry <= 120:
        timing_factor = 0.4  # Poor
    else:
        timing_factor = 0.2  # Very poor
    
    # Call time optimization
    call_hour = int(row["call_time_hour"])
    is_peak = bool(row["is_peak_hours"])
    if is_peak and 10 <= call_hour <= 17:
        call_time_factor = 1.0
    elif 9 <= call_hour <= 20:
        call_time_factor = 0.8
    else:
        call_time_factor = 0.3  # Off hours
    
    # Day of week effect
    day_of_week = int(row["day_of_week"])
    if 2 <= day_of_week <= 4:  # Tue-Thu best
        day_factor = 1.0
    elif day_of_week in [1, 5]:  # Mon, Fri good
        day_factor = 0.8
    else:  # Weekend poor
        day_factor = 0.4
    
    # Agent and system factors
    agent_experience = float(row["agent_experience_months"])
    experience_factor = min(1.0, 0.5 + (agent_experience / 24))  # Plateau at 2 years
    
    script_quality = float(row["script_quality_score"])
    capacity_ratio = float(row["call_capacity_ratio"])
    system_load = float(row["system_load_factor"])
    
    # System performance penalty
    system_factor = (1.0 - capacity_ratio) * (2.0 - system_load) / 2.0
    system_factor = max(0.3, min(1.0, system_factor))
    
    # Historical success and previous attempts
    historical_success = float(row["similar_lead_success_rate"])
    previous_attempts = int(row["previous_attempt_count"])
    attempt_penalty = max(0.3, 1.0 - (previous_attempts * 0.15))
    
    # Engagement and geography
    engagement = float(row["lead_engagement_score"])
    geography = float(row["geography_score"])
    device_score = float(row["device_type_score"])
    
    # Seasonal boost
    seasonal = float(row["seasonal_factor"])
    
    # Combine all factors
    success_probability = (
        lead_quality * 0.25 +
        timing_factor * 0.20 +
        call_time_factor * 0.15 +
        day_factor * 0.05 +
        experience_factor * 0.10 +
        script_quality * 0.08 +
        system_factor * 0.07 +
        historical_success * 0.05 +
        attempt_penalty * 0.03 +
        engagement * 0.02 +
        geography * 0.02 +
        device_score * 0.01 +
        (seasonal - 1.0) * 0.02  # Seasonal adjustment
    )
    
    # Add some realistic noise and clamp
    success_probability = max(0.0, min(1.0, success_probability + np.random.normal(0, 0.08)))
    return float(success_probability)


def generate_synthetic_training_data(num_samples: int = 2000) -> List[Dict[str, Any]]:
    """Generate comprehensive synthetic training data for FirstTouch call optimization"""
    random.seed(42)
    np.random.seed(42)
    data: List[Dict[str, Any]] = []
    
    # Realistic distributions for EdTech leads
    lead_sources = {
        "organic_search": {"score": 0.9, "volume": 0.35},
        "paid_search": {"score": 0.8, "volume": 0.25},
        "social_organic": {"score": 0.6, "volume": 0.15},
        "referral": {"score": 0.95, "volume": 0.1},
        "direct": {"score": 0.85, "volume": 0.08},
        "social_paid": {"score": 0.7, "volume": 0.07}
    }
    
    intent_types = {
        "demo_request": {"score": 0.9, "volume": 0.2},
        "course_inquiry": {"score": 0.8, "volume": 0.3},
        "pricing_inquiry": {"score": 0.7, "volume": 0.25},
        "general_inquiry": {"score": 0.5, "volume": 0.15},
        "content_download": {"score": 0.4, "volume": 0.1}
    }
    
    urgency_levels = {
        "immediate": {"score": 0.9, "volume": 0.15},
        "this_month": {"score": 0.7, "volume": 0.25},
        "next_3_months": {"score": 0.5, "volume": 0.4},
        "exploring": {"score": 0.3, "volume": 0.2}
    }
    
    geographies = {
        "metro_tier1": {"score": 0.8, "volume": 0.4},
        "metro_tier2": {"score": 0.7, "volume": 0.25},
        "tier2_city": {"score": 0.6, "volume": 0.2},
        "tier3_city": {"score": 0.5, "volume": 0.1},
        "rural": {"score": 0.4, "volume": 0.05}
    }
    
    devices = {
        "desktop": {"score": 0.8, "volume": 0.6},
        "mobile": {"score": 0.6, "volume": 0.35},
        "tablet": {"score": 0.7, "volume": 0.05}
    }
    
    for i in range(num_samples):
        # Lead characteristics
        source = random.choices(list(lead_sources.keys()), 
                               weights=[lead_sources[s]["volume"] for s in lead_sources.keys()])[0]
        intent = random.choices(list(intent_types.keys()),
                               weights=[intent_types[t]["volume"] for t in intent_types.keys()])[0]
        urgency = random.choices(list(urgency_levels.keys()),
                                weights=[urgency_levels[u]["volume"] for u in urgency_levels.keys()])[0]
        geography = random.choices(list(geographies.keys()),
                                  weights=[geographies[g]["volume"] for g in geographies.keys()])[0]
        device = random.choices(list(devices.keys()),
                               weights=[devices[d]["volume"] for d in devices.keys()])[0]
        
        # Scores from selections
        lead_source_score = lead_sources[source]["score"]
        lead_intent_score = intent_types[intent]["score"]
        lead_urgency_score = urgency_levels[urgency]["score"]
        geography_score = geographies[geography]["score"]
        device_type_score = devices[device]["score"]
        
        # Timing features - critical for FirstTouch
        # Realistic distribution of response times (most leads called after hours/days)
        if random.random() < 0.41:  # Current 41% contacted within 2 hours
            time_since_inquiry_minutes = random.randint(1, 120)
        else:
            time_since_inquiry_minutes = random.randint(121, 1440)  # Up to 24 hours
        
        # Call timing
        call_time_hour = random.choices(
            range(9, 22), 
            weights=[0.5, 1.2, 1.5, 1.8, 1.0, 0.8, 1.5, 1.8, 1.5, 1.2, 0.8, 0.5, 0.3]
        )[0]
        
        day_of_week = random.randint(1, 7)
        is_peak_hours = 1 if (10 <= call_time_hour <= 12 or 14 <= call_time_hour <= 17) else 0
        
        # Seasonal factor (admission seasons)
        month = random.randint(1, 12)
        if month in [1, 2, 3, 8, 9]:  # Peak admission months
            seasonal_factor = np.clip(np.random.normal(1.15, 0.1), 1.0, 1.3)
        else:
            seasonal_factor = np.clip(np.random.normal(0.95, 0.05), 0.8, 1.1)
        
        # Agent and system features
        agent_experience_months = random.randint(1, 60)
        
        # Script quality varies - some agents use standardized, others improvise
        if random.random() < 0.3:  # 30% use high-quality standardized scripts
            script_quality_score = np.clip(np.random.normal(0.9, 0.05), 0.8, 1.0)
        else:  # 70% use variable quality custom scripts
            script_quality_score = np.clip(np.random.normal(0.6, 0.15), 0.3, 0.8)
        
        # System load factors
        call_capacity_ratio = np.clip(np.random.beta(2, 3), 0.1, 1.0)  # Most agents not at full capacity
        system_load_factor = np.clip(np.random.normal(1.0, 0.2), 0.5, 1.5)
        
        # Historical and engagement features
        base_success_rate = 0.18  # Industry baseline
        similar_lead_success_rate = np.clip(
            np.random.normal(base_success_rate, 0.08), 0.05, 0.4
        )
        
        previous_attempt_count = random.choices([0, 1, 2, 3, 4, 5], 
                                               weights=[0.6, 0.2, 0.1, 0.05, 0.03, 0.02])[0]
        
        # Engagement score based on lead quality
        base_engagement = (lead_source_score + lead_intent_score) / 2
        lead_engagement_score = np.clip(np.random.normal(base_engagement, 0.15), 0.1, 1.0)
        
        # Cost and LTV features
        estimated_ltv = random.choice([15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000])
        call_cost_per_minute = np.clip(np.random.normal(4, 1), 2, 8)
        agent_cost_per_minute = np.clip(np.random.normal(8, 2), 5, 15)
        
        # Create the data row
        row = {
            "lead_id": f"LEAD_{i:05d}",
            "source": source,
            "intent_type": intent,
            "urgency_level": urgency,
            "geography": geography,
            "device": device,
            
            # Features
            "lead_source_score": round(lead_source_score, 3),
            "lead_intent_score": round(lead_intent_score, 3),
            "lead_urgency_score": round(lead_urgency_score, 3),
            "geography_score": round(geography_score, 3),
            "device_type_score": round(device_type_score, 3),
            "time_since_inquiry_minutes": time_since_inquiry_minutes,
            "call_time_hour": call_time_hour,
            "day_of_week": day_of_week,
            "is_peak_hours": is_peak_hours,
            "seasonal_factor": round(seasonal_factor, 3),
            "agent_experience_months": agent_experience_months,
            "script_quality_score": round(script_quality_score, 3),
            "call_capacity_ratio": round(call_capacity_ratio, 3),
            "system_load_factor": round(system_load_factor, 3),
            "similar_lead_success_rate": round(similar_lead_success_rate, 3),
            "previous_attempt_count": previous_attempt_count,
            "lead_engagement_score": round(lead_engagement_score, 3),
            "estimated_ltv": estimated_ltv,
            "call_cost_per_minute": round(call_cost_per_minute, 2),
            "agent_cost_per_minute": round(agent_cost_per_minute, 2),
            
            # Additional context
            "timestamp": (datetime.now() - timedelta(days=random.randint(0, 90))).isoformat(),
        }
        
        # Calculate target variable
        success_probability = _calculate_call_success_probability(row)
        
        # Primary target: call_success (binary)
        call_success = success_probability > 0.18  # Above baseline
        
        # Additional outcomes for realism
        connected = np.random.random() < success_probability
        qualified = False
        booked = False
        
        if connected:
            # If connected, chance of qualification based on lead quality
            qualification_prob = (lead_intent_score + lead_urgency_score) / 2
            qualified = np.random.random() < qualification_prob
            
            if qualified:
                # If qualified, chance of booking
                booking_prob = 0.7  # High booking rate for qualified leads
                booked = np.random.random() < booking_prob
        
        # Call duration and outcome
        if connected:
            if qualified and booked:
                call_duration_seconds = random.randint(180, 600)  # 3-10 minutes
                outcome = "booked"
            elif qualified:
                call_duration_seconds = random.randint(120, 300)  # 2-5 minutes
                outcome = "qualified_no_booking"
            else:
                call_duration_seconds = random.randint(30, 120)   # 30sec-2min
                outcome = "connected_unqualified"
        else:
            call_duration_seconds = 0
            outcome = "no_connect"
        
        row.update({
            "call_success": bool(call_success),  # Primary target
            "success_probability": round(success_probability, 3),
            "connected": connected,
            "qualified": qualified,
            "booked": booked,
            "call_duration_seconds": call_duration_seconds,
            "outcome": outcome,
        })
        
        data.append(row)
    
    # Log statistics
    success_count = sum(1 for d in data if d["call_success"])
    connected_count = sum(1 for d in data if d["connected"])
    qualified_count = sum(1 for d in data if d["qualified"])
    booked_count = sum(1 for d in data if d["booked"])
    
    logger.info(f"Generated {num_samples} FirstTouch training samples:")
    logger.info(f"  - Call successes: {success_count} ({success_count/num_samples*100:.1f}%)")
    logger.info(f"  - Connected: {connected_count} ({connected_count/num_samples*100:.1f}%)")
    logger.info(f"  - Qualified: {qualified_count} ({qualified_count/num_samples*100:.1f}%)")
    logger.info(f"  - Booked: {booked_count} ({booked_count/num_samples*100:.1f}%)")
    
    return data


def predict_call_success(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict call success probability and generate insights
    """
    try:
        # Make prediction
        prediction_result = firsttouch_model.predict(lead_data)
        
        # Extract probability
        probability = prediction_result.get("probabilities", {}).get("True", 0.18)
        if isinstance(probability, dict):
            probability = max(probability.values())
        
        success_score = round(float(probability) * 100, 1)
        
        # Generate insights based on lead characteristics
        insights = _generate_call_insights(lead_data, success_score)
        
        # Call recommendations
        recommendations = _generate_call_recommendations(lead_data, success_score)
        
        return {
            "prediction": {
                "call_success": bool(prediction_result.get("prediction")),
                "success_score": success_score,
                "confidence": float(probability),
            },
            "insights": insights,
            "recommendations": recommendations,
            "model": prediction_result.get("model_name"),
            "timestamp": prediction_result.get("prediction_timestamp"),
        }
        
    except Exception as e:
        logger.error(f"Call success prediction failed: {str(e)}")
        return {
            "prediction": {
                "call_success": False,
                "success_score": 18.0,
                "confidence": 0.18,
            },
            "insights": {
                "timing": "unknown",
                "lead_quality": "medium",
                "primary_factors": ["insufficient_data"]
            },
            "recommendations": {
                "optimal_time": "within_15_minutes",
                "script_type": "standardized",
                "priority": "medium"
            },
            "model": "FirstTouch_v1.0",
            "timestamp": datetime.now().isoformat(),
        }


def _generate_call_insights(lead_data: Dict[str, Any], score: float) -> Dict[str, Any]:
    """Generate actionable insights for call optimization"""
    
    # Timing analysis
    time_since_inquiry = lead_data.get("time_since_inquiry_minutes", 120)
    if time_since_inquiry <= 5:
        timing_status = "golden_window"
    elif time_since_inquiry <= 15:
        timing_status = "good"
    elif time_since_inquiry <= 60:
        timing_status = "acceptable"
    else:
        timing_status = "poor"
    
    # Lead quality assessment
    intent_score = lead_data.get("lead_intent_score", 0.6)
    urgency_score = lead_data.get("lead_urgency_score", 0.5)
    source_score = lead_data.get("lead_source_score", 0.7)
    
    lead_quality_score = (intent_score + urgency_score + source_score) / 3
    if lead_quality_score >= 0.8:
        lead_quality = "high"
    elif lead_quality_score >= 0.6:
        lead_quality = "medium"
    else:
        lead_quality = "low"
    
    # Primary factors affecting success
    factors = []
    if time_since_inquiry > 60:
        factors.append("delayed_response")
    if lead_data.get("script_quality_score", 0.7) < 0.6:
        factors.append("script_inconsistency")
    if lead_data.get("call_capacity_ratio", 0.6) > 0.8:
        factors.append("high_agent_load")
    if lead_data.get("previous_attempt_count", 0) > 2:
        factors.append("multiple_attempts")
    
    return {
        "timing": timing_status,
        "lead_quality": lead_quality,
        "success_score": score,
        "primary_factors": factors[:3],  # Top 3 factors
        "optimal_window": time_since_inquiry <= 15,
        "agent_readiness": lead_data.get("call_capacity_ratio", 0.6) < 0.7
    }


def _generate_call_recommendations(lead_data: Dict[str, Any], score: float) -> Dict[str, Any]:
    """Generate specific call timing and approach recommendations"""
    
    urgency = lead_data.get("lead_urgency_score", 0.5)
    intent = lead_data.get("lead_intent_score", 0.6)
    time_since_inquiry = lead_data.get("time_since_inquiry_minutes", 120)
    
    # Timing recommendation
    if time_since_inquiry <= 5:
        optimal_time = "immediate"
        priority = "critical"
    elif time_since_inquiry <= 15:
        optimal_time = "within_5_minutes"
        priority = "high"
    elif score > 60 and urgency > 0.7:
        optimal_time = "within_15_minutes"
        priority = "high"
    else:
        optimal_time = "within_1_hour"
        priority = "medium" if score > 30 else "low"
    
    # Script recommendation
    if intent > 0.8 and urgency > 0.7:
        script_type = "high_intent_accelerated"
    elif lead_data.get("previous_attempt_count", 0) > 0:
        script_type = "follow_up_nurture"
    elif lead_data.get("lead_source_score", 0.7) > 0.8:
        script_type = "organic_relationship"
    else:
        script_type = "standardized_discovery"
    
    # Channel recommendation
    if score > 70:
        preferred_channel = "voice_call"
    elif score > 40:
        preferred_channel = "voice_with_sms_backup"
    else:
        preferred_channel = "sms_first_then_call"
    
    return {
        "optimal_time": optimal_time,
        "priority": priority,
        "script_type": script_type,
        "preferred_channel": preferred_channel,
        "use_ai_dialer": score > 50,
        "human_handoff_ready": intent > 0.8 or urgency > 0.8
    }


async def generate_call_script(lead_data: Dict[str, Any], prediction: Dict[str, Any] = None) -> str:
    """Generate personalized call script based on lead profile and prediction"""
    
    if prediction is None:
        prediction = await predict_call_success(lead_data)
    
    recommendations = prediction.get("recommendations", {})
    insights = prediction.get("insights", {})
    
    # Extract key variables
    script_type = recommendations.get("script_type", "standardized_discovery")
    lead_quality = insights.get("lead_quality", "medium")
    source = lead_data.get("source", "website")
    intent_type = lead_data.get("intent_type", "general_inquiry")
    
    # Build personalized script
    # Opening (compliance + brand introduction)
    opening = "Hi, this is [Agent Name] calling from APEX AI. I'm calling regarding your recent inquiry about our tech career programs. Do you have 2-3 minutes to chat?"
    
    # Consent line
    consent = "Great! Before we begin, I want to let you know this call may be recorded for quality and training purposes. Is that okay with you?"
    
    # Discovery based on script type
    if script_type == "high_intent_accelerated":
        discovery = f"I see you requested a demo for our {intent_type.replace('_', ' ')}. That's fantastic! What specific tech role are you looking to transition into?"
    elif script_type == "follow_up_nurture":
        discovery = "I wanted to follow up on your interest in our programs. Have you had a chance to think about what we discussed previously?"
    elif script_type == "organic_relationship":
        discovery = f"I noticed you found us through {source.replace('_', ' ')}. What initially caught your attention about APEX AI?"
    else:
        discovery = "I'd love to understand what brought you to look into tech career programs. Are you currently working, or looking to make a career change?"
    
    # Qualification questions
    qualification = """
Perfect! Let me ask a few quick questions to see how we can best help you:
1. What's your current background or work experience?
2. How soon are you looking to make this career transition?
3. Have you considered any specific tech roles or are you exploring options?
"""
    
    # Value proposition based on responses
    if lead_quality == "high":
        value_prop = "Based on what you've shared, I think you'd be a great fit for our intensive program. We've helped over 1000+ professionals make successful transitions to tech careers."
    else:
        value_prop = "That's exactly what our program is designed for. We specialize in helping professionals from non-tech backgrounds build the skills and confidence for tech careers."
    
    # Booking closer
    booking = """
I'd love to connect you with one of our career counselors who can create a personalized roadmap for your transition. They can show you our curriculum, discuss financing options, and answer any specific questions.

Would you prefer a call tomorrow morning or evening? The session takes about 30 minutes and you'll get a clear picture of your path forward.
"""
    
    # Objection handling note
    objection_note = """
[If hesitant: "I completely understand wanting to think it over. How about I send you some quick information, and we can schedule a brief 15-minute call when you're ready to learn more?"]
"""
    
    # Combine script
    script = f"""
{opening}

{consent}

{discovery}

{qualification}

{value_prop}

{booking}

{objection_note}
""".strip()
    
    return script
