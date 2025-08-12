"""
ReferMore - Referrer Likelihood Prediction using XGBoost
MongoDB Integration for Odin-School
"""
from __future__ import annotations

from typing import Any, Dict, List
import logging
import random

import numpy as np
from xgboost import XGBClassifier

from ml.base_model import BaseMLModel

logger = logging.getLogger(__name__)

# Feature schema used by ReferMore
FEATURES = [
    "completion_rate",          # 0.0 - 1.0
    "engagement_score",         # 0 - 100
    "satisfaction_rating",      # 1 - 10
    "invites_sent",             # int
    "link_clicks",              # int
    "signups_generated",        # int
    "forum_posts",              # int
    "social_shares",            # int
    "last_active_days",         # days since last activity
    "course_count",             # number of courses taken
    "certificate_earned",       # bool
    "cohort_rank_percentile",   # 0 - 100 (lower is better)
    "net_promoter_score",       # -100 to 100
    "prior_referrals",          # historical successful referrals
    "has_reward_claimed",       # bool
]

class ReferMoreModel(BaseMLModel):
    def __init__(self, model_name: str = "refermore_propensity"):
        super().__init__(model_name=model_name, model_type="classification")
        self.feature_columns = FEATURES

    def _create_model(self):
        # Reasonable, small XGBoost for quick training/inference
        return XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_lambda=1.0,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
            n_jobs=2,
        )

    def prepare_features(self, data: Dict[str, Any]) -> np.ndarray:
        # Coerce and order features consistently
        def b2i(v: Any) -> int:
            if isinstance(v, bool):
                return int(v)
            if v in ("true", "True", 1, "1"):
                return 1
            return 0

        vals: List[float] = [
            float(data.get("completion_rate", 0.5)),
            float(data.get("engagement_score", 50)),
            float(data.get("satisfaction_rating", 7)),
            float(data.get("invites_sent", 0)),
            float(data.get("link_clicks", 0)),
            float(data.get("signups_generated", 0)),
            float(data.get("forum_posts", 0)),
            float(data.get("social_shares", 0)),
            float(data.get("last_active_days", 7)),
            float(data.get("course_count", 1)),
            float(b2i(data.get("certificate_earned", False))),
            float(data.get("cohort_rank_percentile", 50)),
            float(data.get("net_promoter_score", 20)),
            float(data.get("prior_referrals", 0)),
            float(b2i(data.get("has_reward_claimed", False))),
        ]
        return np.array(vals, dtype=float)

refermore_model = ReferMoreModel()

def _latent_propensity(row: Dict[str, Any]) -> float:
    """Heuristic to generate synthetic label with structured signal.
    Returns a 0-1 probability."""
    completion = float(row["completion_rate"])  # 0-1
    engage = float(row["engagement_score"]) / 100.0
    sat = (float(row["satisfaction_rating"]) - 1) / 9.0  # 0-1
    social = min(1.0, (row["forum_posts"] * 0.02) + (row["social_shares"] * 0.03))
    recency = max(0.0, 1.0 - (float(row["last_active_days"]) / 30.0))
    nps = (float(row["net_promoter_score"]) + 100.0) / 200.0
    history = min(1.0, (row["prior_referrals"] * 0.25))
    certificate = 0.1 if row["certificate_earned"] else 0.0
    reward = 0.05 if row["has_reward_claimed"] else 0.0
    rank_bonus = max(0.0, (100 - float(row["cohort_rank_percentile"])) / 100.0) * 0.1

    score = (
        completion * 0.20
        + engage * 0.25
        + sat * 0.20
        + social * 0.12
        + recency * 0.08
        + nps * 0.08
        + history * 0.04
        + certificate
        + reward
        + rank_bonus
    )
    behavior = min(0.15, (row["invites_sent"] * 0.01) + (row["link_clicks"] * 0.01) + (row["signups_generated"] * 0.03))
    score += behavior
    score = max(0.0, min(1.0, score))
    score = max(0.0, min(1.0, np.random.normal(score, 0.05)))
    return float(score)

def generate_synthetic_training_data(num_samples: int = 2000) -> List[Dict[str, Any]]:
    random.seed(42)
    np.random.seed(42)
    data: List[Dict[str, Any]] = []
    for i in range(num_samples):
        completion_rate = np.clip(np.random.beta(2, 1.5), 0, 1)
        engagement_score = int(np.clip(np.random.normal(60, 20), 0, 100))
        satisfaction_rating = int(np.clip(np.random.normal(8, 2), 1, 10))
        prior_referrals = int(np.random.poisson(0.2))
        forum_posts = int(np.random.poisson(3))
        social_shares = int(np.random.poisson(2))
        invites_sent = int(np.random.poisson(1 + prior_referrals * 0.5))
        link_clicks = int(np.random.poisson(max(0.1, invites_sent * 0.8)))
        signups_generated = int(np.random.binomial(max(1, link_clicks), 0.15))
        last_active_days = int(np.clip(np.random.exponential(5), 0, 60))
        course_count = int(np.clip(np.random.normal(1.6, 0.9), 1, 6))
        certificate_earned = bool(np.random.rand() < (completion_rate * 0.7))
        cohort_rank_percentile = float(np.clip(np.random.normal(55, 25), 0, 100))
        net_promoter_score = int(np.clip(np.random.normal(35, 40), -100, 100))
        has_reward_claimed = bool(np.random.rand() < 0.15)

        row = {
            "student_id": f"STU_{i:05d}",
            "completion_rate": float(round(completion_rate, 3)),
            "engagement_score": engagement_score,
            "satisfaction_rating": satisfaction_rating,
            "invites_sent": invites_sent,
            "link_clicks": link_clicks,
            "signups_generated": signups_generated,
            "forum_posts": forum_posts,
            "social_shares": social_shares,
            "last_active_days": last_active_days,
            "course_count": course_count,
            "certificate_earned": certificate_earned,
            "cohort_rank_percentile": cohort_rank_percentile,
            "net_promoter_score": net_promoter_score,
            "prior_referrals": prior_referrals,
            "has_reward_claimed": has_reward_claimed,
        }

        p = _latent_propensity(row)
        made_referral = np.random.rand() < p
        row["made_referral"] = bool(made_referral)
        data.append(row)

    return data

async def predict_referral_likelihood(profile: Dict[str, Any]) -> Dict[str, Any]:
    pred = await refermore_model.predict(profile)
    prob = pred.get("probabilities", {}).get("True")
    if prob is None:
        if "probabilities" in pred and isinstance(pred["probabilities"], dict):
            prob = max(pred["probabilities"].values())
        else:
            prob = pred.get("confidence", 0.5)

    propensity_score = round(float(prob) * 100, 1)

    # Ensure label is JSON-serializable native bool
    label_val = pred.get("prediction")
    try:
        import numpy as _np  # local import to avoid global side-effects
        if isinstance(label_val, (_np.bool_,)):
            label_val = bool(label_val)
    except Exception:
        # Fallback: coerce truthy/falsy
        label_val = bool(label_val) if isinstance(label_val, (bool, int)) else label_val

    insights = {
        "propensity_score": propensity_score,
        "likelihood_bucket": "high" if propensity_score >= 70 else ("medium" if propensity_score >= 40 else "low"),
        "key_factors": [],
        "recommendations": []
    }

    # Generate key factors based on profile
    if profile.get("completion_rate", 0) >= 0.8:
        insights["key_factors"].append("High completion rate")
    if profile.get("engagement_score", 0) >= 70:
        insights["key_factors"].append("Strong engagement")
    if profile.get("satisfaction_rating", 0) >= 8:
        insights["key_factors"].append("High satisfaction")
    if profile.get("net_promoter_score", 0) >= 50:
        insights["key_factors"].append("Strong NPS score")
    if profile.get("certificate_earned", False):
        insights["key_factors"].append("Certificate earned")

    # Generate recommendations
    if propensity_score >= 70:
        insights["recommendations"].extend([
            "Reach out with referral incentive",
            "Highlight success stories",
            "Provide referral tools and templates"
        ])
    elif propensity_score >= 40:
        insights["recommendations"].extend([
            "Nurture with success stories",
            "Offer small referral rewards",
            "Follow up after course completion"
        ])
    else:
        insights["recommendations"].extend([
            "Focus on engagement first",
            "Improve satisfaction score",
            "Wait for better timing"
        ])

    return {
        "prediction": label_val,
        "confidence": float(prob),
        "propensity_score": propensity_score,
        "insights": insights,
        "model_name": "refermore_propensity"
    }

async def generate_personalized_message(profile: Dict[str, Any], prediction: Dict[str, Any]) -> str:
    """Generate a personalized referral message"""
    propensity = prediction.get("propensity_score", 50)
    name = profile.get("name", "there")
    course = profile.get("course_completed", "course")
    
    if propensity >= 70:
        # High propensity - direct ask
        message = f"""Hi {name}! 🎉
        
We noticed you've done incredibly well in our {course} program! Your success is exactly what we love to see.

Would you be interested in earning some rewards by referring friends who might benefit from the same transformation you've experienced?

For every successful referral, you'll receive:
• ₹5,000 cash reward
• Priority access to new courses
• Exclusive alumni network access

Ready to help others while earning rewards? Just share your referral link below!

Best regards,
Odin School Team"""

    elif propensity >= 40:
        # Medium propensity - softer approach
        message = f"""Hi {name}! 👋

Hope you're doing great after completing {course}! We'd love to hear about your experience.

If you know anyone who might benefit from upskilling like you did, we have a referral program that rewards you for helping others succeed.

No pressure at all - just thought you might be interested!

Cheers,
Odin School Team"""

    else:
        # Low propensity - focus on engagement
        message = f"""Hi {name}!

Thank you for being part of our {course} program. We hope you found it valuable!

We're always working to improve our courses. Would you mind sharing a quick review of your experience?

Your feedback helps us serve future students better.

Thanks!
Odin School Team"""

    return message
