import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import json
import logging
import os
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

# Feature definitions for ReferMore propensity prediction
FEATURES = [
    'completion_rate',
    'engagement_score', 
    'satisfaction_rating',
    'invites_sent',
    'link_clicks',
    'signups_generated',
    'forum_posts',
    'social_shares',
    'last_active_days',
    'course_count',
    'certificate_earned',
    'cohort_rank_percentile',
    'net_promoter_score',
    'prior_referrals',
    'has_reward_claimed'
]

# Target: will_refer (0/1) - based on likelihood to refer in next 30 days
TARGET = 'will_refer'

def generate_synthetic_referral_data(size: int = 5000) -> pd.DataFrame:
    """
    Generate realistic synthetic referral propensity data for OdinSchool
    
    Based on real-world referral patterns:
    - High completers more likely to refer
    - Satisfied learners (NPS > 7) have higher referral rates
    - Active community participants refer more
    - Previous referrers likely to refer again
    """
    
    np.random.seed(42)
    random.seed(42)
    
    data = []
    
    for i in range(size):
        # Basic engagement metrics
        completion_rate = np.random.beta(2, 1.5)  # Skewed towards higher completion
        engagement_score = int(np.random.normal(65, 20))  # 0-100 scale
        engagement_score = max(0, min(100, engagement_score))
        
        # Satisfaction correlates with completion and engagement
        base_satisfaction = 5 + (completion_rate * 4) + (engagement_score / 25)
        satisfaction_rating = int(np.random.normal(base_satisfaction, 1.5))
        satisfaction_rating = max(1, min(10, satisfaction_rating))
        
        # Previous referral activity (realistic distribution)
        has_referred_before = np.random.random() < 0.15  # 15% have referred before
        if has_referred_before:
            invites_sent = int(np.random.exponential(3) + 1)  # 1-10+ typical
            link_clicks = int(invites_sent * np.random.uniform(0.3, 0.8))  # 30-80% click rate
            signups_generated = int(np.random.poisson(link_clicks * 0.15))  # ~15% signup rate
            prior_referrals = int(np.random.poisson(1.5))
        else:
            invites_sent = 0
            link_clicks = 0
            signups_generated = 0
            prior_referrals = 0
        
        # Community engagement
        forum_posts = int(np.random.exponential(2)) if engagement_score > 50 else 0
        social_shares = int(np.random.poisson(0.8)) if satisfaction_rating >= 7 else 0
        
        # Course progress
        last_active_days = int(np.random.exponential(7))  # Most recent activity
        course_count = int(np.random.poisson(1.3)) + 1  # 1-4 courses typical
        
        # Achievement indicators
        certificate_earned = completion_rate > 0.8 and np.random.random() < 0.7
        cohort_rank_percentile = np.random.beta(1.5, 1.5) * 100  # Distributed ranking
        
        # Net Promoter Score (correlates with satisfaction)
        if satisfaction_rating >= 9:
            net_promoter_score = int(np.random.normal(8.5, 1.5))  # Promoters (9-10)
        elif satisfaction_rating >= 7:
            net_promoter_score = int(np.random.normal(7.5, 1))    # Passives (7-8)
        else:
            net_promoter_score = int(np.random.normal(4, 2))      # Detractors (0-6)
        net_promoter_score = max(0, min(10, net_promoter_score))
        
        # Rewards
        has_reward_claimed = signups_generated > 0 and np.random.random() < 0.8
        
        # Personal info for messaging
        first_names = ['Rahul', 'Priya', 'Amit', 'Sneha', 'Vikram', 'Anita', 'Rohit', 'Kavya', 
                      'Arjun', 'Meera', 'Siddharth', 'Nisha', 'Karan', 'Pooja', 'Aditya']
        name = random.choice(first_names)
        email = f"{name.lower()}.{random.randint(100,999)}@{random.choice(['gmail.com', 'yahoo.com', 'outlook.com'])}"
        
        courses = ['Data Science Bootcamp', 'AI & Machine Learning', 'Investment Banking', 
                  'Full Stack Development', 'Digital Marketing', 'Product Management']
        course_completed = random.choice(courses) if certificate_earned else None
        
        # TARGET CALCULATION: Referral Propensity
        # Based on research: completion, satisfaction, engagement, and past behavior are key predictors
        propensity_score = (
            completion_rate * 0.3 +           # 30% weight: completed learners refer more
            (satisfaction_rating / 10) * 0.25 + # 25% weight: satisfaction drives referrals
            (engagement_score / 100) * 0.2 +    # 20% weight: engaged users are active referrers
            (prior_referrals / 5) * 0.15 +      # 15% weight: past behavior predicts future
            (forum_posts / 10) * 0.05 +         # 5% weight: community participation
            (social_shares / 5) * 0.05          # 5% weight: social activity
        )
        
        # Add some noise and realistic thresholds
        propensity_score += np.random.normal(0, 0.1)
        propensity_score = max(0, min(1, propensity_score))
        
        # Convert to binary: realistic 8-12% referral rate
        will_refer = propensity_score > 0.75  # ~10-15% will refer
        
        # Create record
        record = {
            'learner_id': f"LRN{str(i+1).zfill(5)}",
            'name': name,
            'email': email,
            'completion_rate': round(completion_rate, 2),
            'engagement_score': engagement_score,
            'satisfaction_rating': satisfaction_rating,
            'invites_sent': invites_sent,
            'link_clicks': link_clicks,
            'signups_generated': signups_generated,
            'forum_posts': forum_posts,
            'social_shares': social_shares,
            'last_active_days': last_active_days,
            'course_count': course_count,
            'certificate_earned': int(certificate_earned),
            'cohort_rank_percentile': round(cohort_rank_percentile, 1),
            'net_promoter_score': net_promoter_score,
            'prior_referrals': prior_referrals,
            'has_reward_claimed': int(has_reward_claimed),
            'course_completed': course_completed or '',
            'will_refer': int(will_refer),
            'propensity_score': round(propensity_score, 3),
            'created_at': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
        }
        
        data.append(record)
    
    df = pd.DataFrame(data)
    
    # Ensure realistic distributions
    print(f"Generated {len(df)} referral records")
    print(f"Referral rate: {df['will_refer'].mean():.1%}")
    print(f"Avg completion rate: {df['completion_rate'].mean():.2f}")
    print(f"Avg satisfaction: {df['satisfaction_rating'].mean():.1f}")
    print(f"Active referrers: {(df['prior_referrals'] > 0).sum()} ({(df['prior_referrals'] > 0).mean():.1%})")
    
    return df

def train_refermore_model(data: pd.DataFrame) -> Dict[str, Any]:
    """Train Random Forest model for referral propensity prediction"""
    
    # Prepare features and target
    X = data[FEATURES].copy()
    y = data[TARGET]
    
    # Handle any missing values
    X = X.fillna(0)
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'  # Handle class imbalance
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Feature importance
    feature_importance = dict(zip(FEATURES, model.feature_importances_))
    
    # Save model artifacts
    model_path = os.environ.get("MODEL_DIR", os.path.join(os.path.dirname(__file__), "models"))
    os.makedirs(model_path, exist_ok=True)
    
    joblib.dump(model, os.path.join(model_path, "refermore_propensity_model.pkl"))
    joblib.dump(scaler, os.path.join(model_path, "refermore_propensity_scaler.pkl"))
    
    # Save metadata
    metadata = {
        "model_name": "refermore_propensity",
        "version": "1.0",
        "features": FEATURES,
        "target": TARGET,
        "accuracy": float(accuracy),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "feature_importance": {k: float(v) for k, v in feature_importance.items()},
        "trained_at": datetime.now().isoformat(),
        "model_type": "RandomForestClassifier"
    }
    
    with open(os.path.join(model_path, "refermore_propensity_metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Model trained with accuracy: {accuracy:.3f}")
    print(f"Top features: {sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]}")
    
    return {
        "accuracy": accuracy,
        "feature_importance": feature_importance,
        "test_samples": len(X_test),
        "training_samples": len(X_train),
        "metadata": metadata
    }

def predict_referral_propensity(learner_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Predict referral propensity for learners"""
    
    try:
        model_path = os.environ.get("MODEL_DIR", os.path.join(os.path.dirname(__file__), "models"))
        
        # Load model and scaler
        model = joblib.load(os.path.join(model_path, "refermore_propensity_model.pkl"))
        scaler = joblib.load(os.path.join(model_path, "refermore_propensity_scaler.pkl"))
        
        # Prepare features
        df = pd.DataFrame(learner_data)
        X = df[FEATURES].fillna(0)
        X_scaled = scaler.transform(X)
        
        # Predict
        predictions = model.predict(X_scaled)
        probabilities = model.predict_proba(X_scaled)[:, 1]  # Probability of referring
        
        # Format results
        results = []
        for i, (prediction, probability) in enumerate(zip(predictions, probabilities)):
            result = {
                "learner_id": learner_data[i].get("learner_id", f"learner_{i}"),
                "will_refer": bool(prediction),
                "propensity_score": float(probability),
                "confidence": "High" if probability > 0.8 else "Medium" if probability > 0.6 else "Low",
                "recommendation": "Priority referrer" if probability > 0.7 else "Potential referrer" if probability > 0.5 else "Low priority"
            }
            results.append(result)
        
        return results
        
    except Exception as e:
        print(f"Prediction failed: {e}")
        raise

# Model instance for easy import
refermore_model = {
    "train": train_refermore_model,
    "predict": predict_referral_propensity,
    "generate_data": generate_synthetic_referral_data,
    "features": FEATURES,
    "target": TARGET
}
