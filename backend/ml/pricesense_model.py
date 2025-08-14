"""
PriceSense - Pricing and Payment Plan Optimization using XGBoost

Provides:
- PriceSenseModel (BaseMLModel subclass)
- generate_synthetic_training_data(num_samples=2000)
- predict_optimal_plan(segment_data)
- generate_pricing_message(segment_data, plan_prediction)
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


# Feature schema used by PriceSense
FEATURES = [
    # User Segment Features
    "source_score",              # 0.0 - 1.0 (organic=0.9, paid=0.7, social=0.6, etc.)
    "geography_score",           # 0.0 - 1.0 (metro=0.9, tier2=0.7, rural=0.5, intl=0.8)
    "device_score",              # 0.0 - 1.0 (desktop=0.9, mobile=0.7, tablet=0.8)
    "prior_engagement_score",    # 0.0 - 1.0 (pageviews, time spent, downloads, etc.)
    
    # Plan Context Features
    "plan_upfront_amount",       # Absolute upfront payment amount
    "plan_total_amount",         # Total course cost
    "plan_duration_months",      # Payment plan duration (1-24 months)
    "plan_monthly_payment",      # Monthly payment amount
    "plan_interest_rate",        # Interest rate for installments (0-15%)
    "scholarship_eligible",      # 0 or 1
    "scholarship_discount_pct",  # 0-50% discount available
    
    # Market Context Features
    "competitor_price_ratio",    # Our price / avg competitor price
    "seasonality_factor",        # 0.8-1.2 based on time of year
    "demand_pressure",           # 0.5-1.5 (course popularity, seat availability)
    
    # Behavioral Features
    "price_sensitivity_score",  # 0.0-1.0 (derived from browsing patterns)
    "urgency_score",            # 0.0-1.0 (time since first visit, demo requests)
    "income_tier_score",        # 0.0-1.0 (estimated from location + device + behavior)
    
    # Historical Features
    "similar_segment_success",   # 0.0-1.0 (conversion rate for similar segments)
    "churn_risk_score",         # 0.0-1.0 (likelihood to default/refund based on segment)
]


class PriceSenseModel(BaseMLModel):
    def __init__(self, model_name: str = "pricesense_optimization"):
        super().__init__(model_name=model_name, model_type="classification")
        self.feature_columns = FEATURES

    def _create_model(self):
        # XGBoost optimized for pricing optimization
        return XGBClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.08,
            subsample=0.85,
            colsample_bytree=0.85,
            reg_lambda=1.2,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
            n_jobs=2,
        )

    def prepare_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Convert segment and plan data into feature vector"""
        def safe_float(v: Any, default: float = 0.0) -> float:
            try:
                return float(v)
            except (ValueError, TypeError):
                return default

        vals: List[float] = [
            safe_float(data.get("source_score", 0.7)),
            safe_float(data.get("geography_score", 0.7)),
            safe_float(data.get("device_score", 0.8)),
            safe_float(data.get("prior_engagement_score", 0.5)),
            safe_float(data.get("plan_upfront_amount", 5000)),
            safe_float(data.get("plan_total_amount", 25000)),
            safe_float(data.get("plan_duration_months", 6)),
            safe_float(data.get("plan_monthly_payment", 4000)),
            safe_float(data.get("plan_interest_rate", 5.0)),
            safe_float(data.get("scholarship_eligible", 0)),
            safe_float(data.get("scholarship_discount_pct", 0)),
            safe_float(data.get("competitor_price_ratio", 1.0)),
            safe_float(data.get("seasonality_factor", 1.0)),
            safe_float(data.get("demand_pressure", 1.0)),
            safe_float(data.get("price_sensitivity_score", 0.5)),
            safe_float(data.get("urgency_score", 0.5)),
            safe_float(data.get("income_tier_score", 0.5)),
            safe_float(data.get("similar_segment_success", 0.6)),
            safe_float(data.get("churn_risk_score", 0.3)),
        ]
        return np.array(vals, dtype=float)


pricesense_model = PriceSenseModel()


def _calculate_plan_attractiveness(row: Dict[str, Any]) -> float:
    """Heuristic to generate synthetic label based on plan and segment fit"""
    
    # Base attractiveness from segment quality
    segment_quality = (
        float(row["source_score"]) * 0.25 +
        float(row["geography_score"]) * 0.2 +
        float(row["device_score"]) * 0.1 +
        float(row["prior_engagement_score"]) * 0.25
    )
    
    # Plan affordability and structure
    upfront = float(row["plan_upfront_amount"])
    total = float(row["plan_total_amount"])
    monthly = float(row["plan_monthly_payment"])
    duration = float(row["plan_duration_months"])
    interest = float(row["plan_interest_rate"])
    
    # Affordability score (lower upfront is better for most segments)
    affordability = 1.0 - min(0.8, upfront / 15000)  # Normalize to 15k upfront
    
    # Payment structure score (reasonable monthly payment)
    optimal_monthly = total / duration if duration > 0 else total
    payment_structure = 1.0 - abs(monthly - optimal_monthly) / max(monthly, optimal_monthly, 1000)
    
    # Interest penalty
    interest_penalty = max(0.0, 1.0 - (interest / 20.0))  # Penalize high interest
    
    # Scholarship boost
    scholarship_boost = 0.0
    if row["scholarship_eligible"] > 0:
        scholarship_boost = float(row["scholarship_discount_pct"]) / 100.0 * 0.3
    
    # Market factors
    price_competitiveness = 1.0 - abs(float(row["competitor_price_ratio"]) - 0.95) / 0.5  # Optimal at 5% below competition
    seasonal_boost = float(row["seasonality_factor"]) - 1.0  # Seasonal factor around 1.0
    demand_factor = min(1.0, float(row["demand_pressure"]))
    
    # Personal fit
    price_sensitivity = 1.0 - float(row["price_sensitivity_score"])  # Lower sensitivity = higher conversion
    urgency_boost = float(row["urgency_score"]) * 0.2
    income_fit = float(row["income_tier_score"])
    
    # Historical success
    segment_success = float(row["similar_segment_success"])
    churn_penalty = 1.0 - float(row["churn_risk_score"])
    
    # Combine all factors
    score = (
        segment_quality * 0.25 +
        affordability * 0.15 +
        payment_structure * 0.1 +
        interest_penalty * 0.05 +
        scholarship_boost +
        price_competitiveness * 0.1 +
        (seasonal_boost + demand_factor) * 0.05 +
        price_sensitivity * 0.1 +
        urgency_boost +
        income_fit * 0.1 +
        segment_success * 0.1 +
        churn_penalty * 0.1
    )
    
    # Add some noise and clamp
    score = max(0.0, min(1.0, score + np.random.normal(0, 0.08)))
    return float(score)


def generate_synthetic_training_data(num_samples: int = 2000) -> List[Dict[str, Any]]:
    """Generate comprehensive synthetic training data for PriceSense optimization"""
    random.seed(42)
    np.random.seed(42)
    data: List[Dict[str, Any]] = []
    
    # Realistic distributions
    sources = {
        "organic": {"score": 0.9, "volume": 0.3},
        "paid_search": {"score": 0.8, "volume": 0.25},
        "social_paid": {"score": 0.7, "volume": 0.15},
        "referral": {"score": 0.95, "volume": 0.1},
        "direct": {"score": 0.85, "volume": 0.1},
        "social_organic": {"score": 0.6, "volume": 0.1}
    }
    
    geographies = {
        "metro_tier1": {"score": 0.9, "volume": 0.4, "income": "high"},
        "metro_tier2": {"score": 0.8, "volume": 0.25, "income": "medium"},
        "tier2_city": {"score": 0.7, "volume": 0.2, "income": "medium"},
        "rural": {"score": 0.5, "volume": 0.1, "income": "low"},
        "international": {"score": 0.85, "volume": 0.05, "income": "high"}
    }
    
    devices = {
        "desktop": {"score": 0.9, "volume": 0.6},
        "mobile": {"score": 0.7, "volume": 0.3},
        "tablet": {"score": 0.8, "volume": 0.1}
    }
    
    # Course pricing plans (realistic for Indian EdTech)
    base_prices = [15000, 20000, 25000, 30000, 35000, 40000]  # Base course prices
    plan_structures = [
        {"duration": 1, "interest": 0.0, "upfront_pct": 1.0},      # Full upfront
        {"duration": 3, "interest": 2.0, "upfront_pct": 0.3},     # 3-month plan
        {"duration": 6, "interest": 4.0, "upfront_pct": 0.2},     # 6-month plan
        {"duration": 12, "interest": 8.0, "upfront_pct": 0.1},    # 12-month plan
        {"duration": 18, "interest": 12.0, "upfront_pct": 0.05},  # 18-month plan
        {"duration": 24, "interest": 15.0, "upfront_pct": 0.0},   # 24-month plan
    ]
    
    for i in range(num_samples):
        # Select segment characteristics
        source = random.choices(list(sources.keys()), weights=[sources[s]["volume"] for s in sources.keys()])[0]
        geography = random.choices(list(geographies.keys()), weights=[geographies[g]["volume"] for g in geographies.keys()])[0]
        device = random.choices(list(devices.keys()), weights=[devices[d]["volume"] for d in devices.keys()])[0]
        
        # User segment scores
        source_score = sources[source]["score"]
        geography_score = geographies[geography]["score"]
        device_score = devices[device]["score"]
        
        # Prior engagement (influenced by source and device)
        base_engagement = (source_score + device_score) / 2
        prior_engagement_score = np.clip(np.random.normal(base_engagement, 0.15), 0.1, 1.0)
        
        # Plan characteristics
        base_price = random.choice(base_prices)
        plan_structure = random.choice(plan_structures)
        
        plan_total_amount = base_price
        plan_duration_months = plan_structure["duration"]
        plan_interest_rate = plan_structure["interest"]
        plan_upfront_amount = plan_total_amount * plan_structure["upfront_pct"]
        
        # Calculate monthly payment
        if plan_duration_months <= 1:
            plan_monthly_payment = plan_total_amount
        else:
            principal_monthly = (plan_total_amount - plan_upfront_amount) / plan_duration_months
            interest_monthly = principal_monthly * (plan_interest_rate / 100) / 12
            plan_monthly_payment = principal_monthly + interest_monthly
        
        # Scholarship eligibility (varies by geography and source)
        scholarship_eligible = 1 if (
            geography in ["tier2_city", "rural"] or 
            source == "referral" or 
            random.random() < 0.2
        ) else 0
        scholarship_discount_pct = random.choice([10, 15, 20, 25, 30, 35]) if scholarship_eligible else 0
        
        # Market context
        competitor_price_ratio = np.clip(np.random.normal(1.0, 0.2), 0.7, 1.4)
        
        # Seasonality (peak in Jan-Mar and Aug-Oct for EdTech)
        month = random.randint(1, 12)
        if month in [1, 2, 3, 8, 9, 10]:
            seasonality_factor = np.clip(np.random.normal(1.15, 0.1), 1.0, 1.3)
        elif month in [12, 4, 7]:
            seasonality_factor = np.clip(np.random.normal(0.9, 0.1), 0.7, 1.0)
        else:
            seasonality_factor = np.clip(np.random.normal(1.0, 0.05), 0.9, 1.1)
        
        demand_pressure = np.clip(np.random.normal(1.0, 0.2), 0.5, 1.5)
        
        # Behavioral characteristics
        income_tier_map = {"high": 0.8, "medium": 0.6, "low": 0.4}
        income_tier_score = income_tier_map[geographies[geography]["income"]]
        income_tier_score = np.clip(np.random.normal(income_tier_score, 0.1), 0.1, 1.0)
        
        # Price sensitivity (higher for lower income, mobile users)
        base_sensitivity = 0.5
        if geographies[geography]["income"] == "low":
            base_sensitivity += 0.2
        if device == "mobile":
            base_sensitivity += 0.1
        price_sensitivity_score = np.clip(np.random.normal(base_sensitivity, 0.15), 0.1, 0.9)
        
        urgency_score = np.clip(np.random.beta(2, 3), 0.1, 0.9)  # Most users have lower urgency
        
        # Historical success rate for similar segments
        similar_segment_success = np.clip(
            source_score * 0.5 + geography_score * 0.3 + (1 - price_sensitivity_score) * 0.2 + 
            np.random.normal(0, 0.1), 0.2, 0.8
        )
        
        # Churn risk (higher for longer payment plans, higher interest)
        base_churn_risk = 0.2
        if plan_duration_months > 12:
            base_churn_risk += 0.15
        if plan_interest_rate > 8:
            base_churn_risk += 0.1
        if price_sensitivity_score > 0.7:
            base_churn_risk += 0.1
        churn_risk_score = np.clip(np.random.normal(base_churn_risk, 0.08), 0.05, 0.6)
        
        # Create the data row
        row = {
            "user_id": f"USER_{i:05d}",
            "source": source,
            "geography": geography,
            "device": device,
            "plan_id": f"PLAN_{plan_duration_months}M_{int(plan_total_amount)}",
            
            # Features
            "source_score": round(source_score, 3),
            "geography_score": round(geography_score, 3),
            "device_score": round(device_score, 3),
            "prior_engagement_score": round(prior_engagement_score, 3),
            "plan_upfront_amount": round(plan_upfront_amount, 2),
            "plan_total_amount": plan_total_amount,
            "plan_duration_months": plan_duration_months,
            "plan_monthly_payment": round(plan_monthly_payment, 2),
            "plan_interest_rate": plan_interest_rate,
            "scholarship_eligible": scholarship_eligible,
            "scholarship_discount_pct": scholarship_discount_pct,
            "competitor_price_ratio": round(competitor_price_ratio, 3),
            "seasonality_factor": round(seasonality_factor, 3),
            "demand_pressure": round(demand_pressure, 3),
            "price_sensitivity_score": round(price_sensitivity_score, 3),
            "urgency_score": round(urgency_score, 3),
            "income_tier_score": round(income_tier_score, 3),
            "similar_segment_success": round(similar_segment_success, 3),
            "churn_risk_score": round(churn_risk_score, 3),
            
            # Additional context for outcomes
            "timestamp": (datetime.now() - timedelta(days=random.randint(0, 90))).isoformat(),
        }
        
        # Calculate target variables
        plan_attractiveness = _calculate_plan_attractiveness(row)
        
        # Primary target: optimal_plan_choice (binary)
        optimal_plan_choice = plan_attractiveness > 0.6
        
        # Secondary outcomes for realism
        converted = np.random.random() < plan_attractiveness
        refunded = False
        defaulted = False
        
        if converted:
            # Refund probability based on churn risk and plan mismatch
            refund_prob = churn_risk_score * 0.5
            refunded = np.random.random() < refund_prob
            
            # Default probability for payment plans (only if not refunded)
            if not refunded and plan_duration_months > 1:
                default_prob = churn_risk_score * 0.3
                defaulted = np.random.random() < default_prob
        
        row.update({
            "optimal_plan_choice": bool(optimal_plan_choice),  # Primary target
            "plan_attractiveness_score": round(plan_attractiveness, 3),
            "converted": converted,
            "refunded": refunded,
            "defaulted": defaulted,
        })
        
        data.append(row)
    
    # Log statistics
    optimal_count = sum(1 for d in data if d["optimal_plan_choice"])
    converted_count = sum(1 for d in data if d["converted"])
    refund_count = sum(1 for d in data if d["refunded"])
    default_count = sum(1 for d in data if d["defaulted"])
    
    logger.info(f"Generated {num_samples} PriceSense training samples:")
    logger.info(f"  - Optimal plan choices: {optimal_count} ({optimal_count/num_samples*100:.1f}%)")
    logger.info(f"  - Conversions: {converted_count} ({converted_count/num_samples*100:.1f}%)")
    logger.info(f"  - Refunds: {refund_count} ({refund_count/num_samples*100:.1f}%)")
    logger.info(f"  - Defaults: {default_count} ({default_count/num_samples*100:.1f}%)")
    
    return data


async def predict_optimal_plan(segment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict optimal plan for a user segment and generate insights
    """
    try:
        # Make prediction
        prediction_result = pricesense_model.predict(segment_data)
        
        # Extract probability
        probability = prediction_result.get("probabilities", {}).get("True", 0.5)
        if isinstance(probability, dict):
            probability = max(probability.values())
        
        optimization_score = round(float(probability) * 100, 1)
        
        # Generate insights based on segment characteristics
        insights = _generate_plan_insights(segment_data, optimization_score)
        
        # Plan recommendations
        recommendations = _generate_plan_recommendations(segment_data, optimization_score)
        
        return {
            "prediction": {
                "optimal_choice": bool(prediction_result.get("prediction")),
                "optimization_score": optimization_score,
                "confidence": float(probability),
            },
            "insights": insights,
            "recommendations": recommendations,
            "model": prediction_result.get("model_name"),
            "timestamp": prediction_result.get("prediction_timestamp"),
        }
        
    except Exception as e:
        logger.error(f"Plan optimization prediction failed: {str(e)}")
        return {
            "prediction": {
                "optimal_choice": False,
                "optimization_score": 50.0,
                "confidence": 0.5,
            },
            "insights": {
                "segment": "unknown",
                "primary_factors": ["insufficient_data"],
                "risk_level": "medium"
            },
            "recommendations": {
                "suggested_plan": "default_6_month",
                "messaging": "standard_pricing",
                "urgency": "medium"
            },
            "error": str(e)
        }


def _generate_plan_insights(segment_data: Dict[str, Any], score: float) -> Dict[str, Any]:
    """Generate actionable insights for plan optimization"""
    
    # Segment classification
    geo_score = segment_data.get("geography_score", 0.7)
    income_score = segment_data.get("income_tier_score", 0.5)
    price_sensitivity = segment_data.get("price_sensitivity_score", 0.5)
    
    if geo_score >= 0.8 and income_score >= 0.7:
        segment = "premium"
    elif price_sensitivity > 0.7 or income_score < 0.4:
        segment = "budget_conscious"
    else:
        segment = "standard"
    
    # Primary optimization factors
    factors = []
    upfront = segment_data.get("plan_upfront_amount", 5000)
    duration = segment_data.get("plan_duration_months", 6)
    scholarship = segment_data.get("scholarship_eligible", 0)
    
    if upfront > 10000 and price_sensitivity > 0.6:
        factors.append("high_upfront_barrier")
    if duration > 12 and segment_data.get("churn_risk_score", 0.3) > 0.4:
        factors.append("long_term_risk")
    if scholarship and segment_data.get("scholarship_discount_pct", 0) < 20:
        factors.append("underutilized_scholarship")
    if segment_data.get("competitor_price_ratio", 1.0) > 1.1:
        factors.append("pricing_disadvantage")
    
    # Risk assessment
    churn_risk = segment_data.get("churn_risk_score", 0.3)
    if churn_risk > 0.5:
        risk_level = "high"
    elif churn_risk > 0.3:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return {
        "segment": segment,
        "optimization_score": score,
        "primary_factors": factors[:3],  # Top 3 factors
        "risk_level": risk_level,
        "price_sensitivity": "high" if price_sensitivity > 0.7 else "medium" if price_sensitivity > 0.4 else "low",
        "urgency_level": "high" if segment_data.get("urgency_score", 0.5) > 0.7 else "medium"
    }


def _generate_plan_recommendations(segment_data: Dict[str, Any], score: float) -> Dict[str, Any]:
    """Generate specific plan and messaging recommendations"""
    
    price_sensitivity = segment_data.get("price_sensitivity_score", 0.5)
    income_score = segment_data.get("income_tier_score", 0.5)
    urgency = segment_data.get("urgency_score", 0.5)
    scholarship_eligible = segment_data.get("scholarship_eligible", 0)
    
    # Plan recommendation logic
    if price_sensitivity > 0.7 or income_score < 0.4:
        if scholarship_eligible:
            suggested_plan = "scholarship_12_month"
        else:
            suggested_plan = "budget_18_month"
    elif income_score > 0.7 and urgency > 0.6:
        suggested_plan = "premium_upfront"
    elif score > 70:
        suggested_plan = "standard_6_month"
    else:
        suggested_plan = "flexible_12_month"
    
    # Messaging strategy
    if scholarship_eligible and segment_data.get("scholarship_discount_pct", 0) >= 20:
        messaging = "scholarship_focused"
    elif urgency > 0.7:
        messaging = "urgency_limited_time"
    elif price_sensitivity > 0.6:
        messaging = "value_focused"
    else:
        messaging = "standard_benefits"
    
    # Urgency level
    if urgency > 0.7 or segment_data.get("seasonality_factor", 1.0) > 1.1:
        urgency_level = "high"
    elif urgency > 0.4:
        urgency_level = "medium"
    else:
        urgency_level = "low"
    
    return {
        "suggested_plan": suggested_plan,
        "messaging": messaging,
        "urgency": urgency_level,
        "highlight_scholarship": bool(scholarship_eligible),
        "emphasize_flexibility": price_sensitivity > 0.6,
        "show_competitor_comparison": segment_data.get("competitor_price_ratio", 1.0) < 0.95
    }


async def generate_pricing_message(segment_data: Dict[str, Any], prediction: Dict[str, Any] = None) -> str:
    """Generate personalized pricing message based on segment and prediction"""
    
    if prediction is None:
        prediction = await predict_optimal_plan(segment_data)
    
    recommendations = prediction.get("recommendations", {})
    insights = prediction.get("insights", {})
    
    # Extract key variables
    messaging_type = recommendations.get("messaging", "standard_benefits")
    suggested_plan = recommendations.get("suggested_plan", "standard_6_month")
    urgency = recommendations.get("urgency", "medium")
    scholarship = recommendations.get("highlight_scholarship", False)
    
    # Build personalized message
    greeting = "Ready to transform your career?"
    
    # Main value proposition based on messaging type
    if messaging_type == "scholarship_focused":
        value_prop = f"Great news! You're eligible for up to {segment_data.get('scholarship_discount_pct', 20)}% scholarship discount."
    elif messaging_type == "urgency_limited_time":
        value_prop = "Limited seats available - secure your spot today!"
    elif messaging_type == "value_focused":
        value_prop = "Get premium training at the most affordable rates in the market."
    else:
        value_prop = "Join thousands of successful career switchers."
    
    # Plan details based on suggestion
    if "upfront" in suggested_plan:
        plan_detail = "Pay once, learn forever - with full upfront payment benefits."
    elif "scholarship" in suggested_plan:
        plan_detail = "Flexible scholarship payment plan - no upfront stress."
    elif "budget" in suggested_plan:
        plan_detail = "Easy monthly payments as low as ₹2,500/month."
    elif "flexible" in suggested_plan:
        plan_detail = "Choose your payment timeline - 6, 12, or 18 months."
    else:
        plan_detail = "Convenient 6-month payment plan with minimal interest."
    
    # Urgency closer
    if urgency == "high":
        closer = "Enroll now - offer valid for next 48 hours only!"
    elif urgency == "medium":
        closer = "Start your journey this month and save more."
    else:
        closer = "Take the first step towards your dream career."
    
    # Combine message
    message = f"{greeting} {value_prop} {plan_detail} {closer}"
    
    # Add scholarship mention if eligible
    if scholarship:
        message += " Ask about additional scholarship opportunities!"
    
    return message.strip()
