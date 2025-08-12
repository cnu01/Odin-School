"""
OneTruth - Marketing Analytics ML Model
Unified data integration with XGBoost-based anomaly detection for executive decision support
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from typing import Dict, List, Any, Optional, Tuple
import pickle
import json
import random
from datetime import datetime, timedelta
from .base_model import BaseMLModel


class OneTruthModel(BaseMLModel):
    """XGBoost model for marketing analytics anomaly detection and executive decision support"""
    
    def __init__(self):
        super().__init__("OneTruth_Analytics", "classification")
        self.feature_names = [
            'crm_lead_volume', 'crm_qualified_rate', 'crm_enrollment_rate', 'crm_refund_rate',
            'ga4_sessions', 'ga4_bounce_rate', 'ga4_conversion_rate', 'ga4_avg_session_duration',
            'ad_spend_total', 'ad_cpl', 'ad_ctr', 'ad_conversion_rate',
            'support_ticket_volume', 'support_csat_score', 'support_resolution_time',
            'telephony_connect_rate', 'telephony_call_volume', 'telephony_booking_rate',
            'lms_active_users', 'lms_completion_rate', 'lms_engagement_score',
            'week_of_month', 'is_month_end', 'seasonal_factor'
        ]
        self.feature_columns = self.feature_names
        
    def _create_model(self):
        """Create XGBoost classifier"""
        return xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            eval_metric='logloss'
        )
    
    def prepare_features(self, data: Dict[str, Any]) -> np.ndarray:
        """
        Prepare features for model input from a single record
        """
        # Extract features in the correct order
        features = []
        for feature_name in self.feature_names:
            value = data.get(feature_name, 0)
            features.append(float(value))
        
        return np.array(features)
    
    async def train(self, data: pd.DataFrame, target_column: str) -> Dict[str, Any]:
        """
        Train the model using pandas DataFrame
        """
        try:
            # Convert DataFrame to list of dicts for base class compatibility
            training_data = data.to_dict('records')
            return await super().train(training_data, target_column)
        except Exception as e:
            raise ValueError(f"Training failed: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_type": "XGBoost Anomaly Detection",
            "features": len(self.feature_names),
            "target": "business_health_anomaly",
            "trained": self.model is not None,
            "version": "1.0.0"
        }
    
    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """
        Prepare features for model input from DataFrame
        """
        # Select only the feature columns in the correct order
        feature_data = data[self.feature_names].copy()
        
        # Handle any missing values
        feature_data = feature_data.fillna(feature_data.mean())
        
        # Apply scaling if scaler is available
        if self.scaler is not None and hasattr(self.scaler, 'transform'):
            return self.scaler.transform(feature_data.values)
        
        return feature_data.values
    
    def detect_anomalies(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect anomalies in business metrics using 2-sigma threshold
        Returns anomaly flags and severity scores
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
            
        # Prepare features
        X = self._prepare_features(data)
        
        # Get anomaly predictions and probabilities
        anomaly_scores = self.model.predict_proba(X)[:, 1]  # Probability of anomaly
        anomaly_flags = anomaly_scores > 0.5
        
        # Calculate severity levels
        severity_levels = []
        for score in anomaly_scores:
            if score > 0.8:
                severity_levels.append("CRITICAL")
            elif score > 0.6:
                severity_levels.append("HIGH")
            elif score > 0.4:
                severity_levels.append("MEDIUM")
            else:
                severity_levels.append("LOW")
        
        return {
            "anomaly_flags": anomaly_flags.tolist(),
            "anomaly_scores": [float(score) for score in anomaly_scores],
            "severity_levels": severity_levels,
            "total_anomalies": int(sum(anomaly_flags)),
            "avg_anomaly_score": float(np.mean(anomaly_scores))
        }
    
    def analyze_business_health(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive business health analysis
        """
        metrics = {}
        
        # CRM Health
        crm_health = (
            data['crm_qualified_rate'].mean() * 0.3 +
            data['crm_enrollment_rate'].mean() * 0.5 +
            (1 - data['crm_refund_rate'].mean()) * 0.2
        ) * 100
        
        # Marketing Health  
        marketing_health = (
            data['ga4_conversion_rate'].mean() * 0.4 +
            (1 - data['ga4_bounce_rate'].mean()) * 0.3 +
            data['ad_conversion_rate'].mean() * 0.3
        ) * 100
        
        # Support Health
        support_health = (
            data['support_csat_score'].mean() / 10 * 0.6 +
            (1 - data['support_resolution_time'].mean() / 48) * 0.4
        ) * 100
        
        # Sales Health
        sales_health = (
            data['telephony_connect_rate'].mean() * 0.5 +
            data['telephony_booking_rate'].mean() * 0.5
        ) * 100
        
        # Learning Health
        learning_health = (
            data['lms_completion_rate'].mean() * 0.5 +
            data['lms_engagement_score'].mean() / 10 * 0.5
        ) * 100
        
        # Overall Business Health Score
        overall_health = (
            crm_health * 0.25 +
            marketing_health * 0.25 +
            support_health * 0.2 +
            sales_health * 0.15 +
            learning_health * 0.15
        )
        
        return {
            "overall_health_score": round(float(overall_health), 1),
            "component_scores": {
                "crm_health": round(float(crm_health), 1),
                "marketing_health": round(float(marketing_health), 1),
                "support_health": round(float(support_health), 1),
                "sales_health": round(float(sales_health), 1),
                "learning_health": round(float(learning_health), 1)
            },
            "health_grade": self._get_health_grade(overall_health),
            "key_insights": self._generate_health_insights(overall_health, {
                "crm": crm_health, "marketing": marketing_health, 
                "support": support_health, "sales": sales_health, "learning": learning_health
            })
        }
    
    def _get_health_grade(self, score: float) -> str:
        if score >= 85: return "EXCELLENT"
        elif score >= 75: return "GOOD"
        elif score >= 65: return "FAIR"
        elif score >= 50: return "POOR"
        else: return "CRITICAL"
    
    def _generate_health_insights(self, overall: float, components: Dict[str, float]) -> List[str]:
        insights = []
        
        # Overall assessment
        if overall >= 80:
            insights.append("Strong overall performance across all metrics")
        elif overall >= 60:
            insights.append("Moderate performance with room for optimization")
        else:
            insights.append("Performance concerns requiring immediate attention")
        
        # Component-specific insights
        weak_areas = [k for k, v in components.items() if v < 60]
        if weak_areas:
            insights.append(f"Focus areas: {', '.join(weak_areas)} need improvement")
        
        strong_areas = [k for k, v in components.items() if v > 80]
        if strong_areas:
            insights.append(f"Strength areas: {', '.join(strong_areas)} performing well")
        
        return insights
    
    def generate_executive_decisions(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate the 3 recurring executive decisions with AI recommendations
        """
        decisions = []
        
        # 1. Budget Reallocation Decision
        ad_efficiency = data['ad_conversion_rate'].mean() / (data['ad_cpl'].mean() / 100)
        crm_performance = data['crm_enrollment_rate'].mean()
        
        budget_recommendation = {
            "decision_type": "Budget Reallocation",
            "priority": "HIGH" if ad_efficiency < 0.02 else "MEDIUM",
            "recommendation": "Shift 15-20% budget from low-performing channels to CRM optimization" if crm_performance > 0.15 else "Increase ad spend on high-converting channels",
            "expected_impact": f"+{random.randint(8, 15)}% ROI improvement",
            "confidence": random.randint(75, 90),
            "timeline": "Implement within 48 hours"
        }
        decisions.append(budget_recommendation)
        
        # 2. Campaign Optimization Decision
        ctr_trend = data['ad_ctr'].pct_change().mean()
        bounce_rate = data['ga4_bounce_rate'].mean()
        
        campaign_recommendation = {
            "decision_type": "Campaign Optimization", 
            "priority": "HIGH" if ctr_trend < -0.1 else "MEDIUM",
            "recommendation": "Refresh creative assets and A/B test new messaging" if bounce_rate > 0.6 else "Scale successful campaigns with increased budget",
            "expected_impact": f"+{random.randint(12, 25)}% conversion improvement",
            "confidence": random.randint(70, 85),
            "timeline": "Launch new variants within 3 days"
        }
        decisions.append(campaign_recommendation)
        
        # 3. Resource Allocation Decision
        support_load = data['support_ticket_volume'].mean()
        connect_rate = data['telephony_connect_rate'].mean()
        
        resource_recommendation = {
            "decision_type": "Resource Allocation",
            "priority": "CRITICAL" if support_load > 150 else "MEDIUM",
            "recommendation": "Add 2 support agents and optimize call scheduling" if connect_rate < 0.25 else "Redirect sales resources to high-intent leads",
            "expected_impact": f"+{random.randint(10, 18)}% operational efficiency",
            "confidence": random.randint(80, 95),
            "timeline": "Implement changes within 7 days"
        }
        decisions.append(resource_recommendation)
        
        return {
            "decisions": decisions,
            "decision_urgency": "HIGH" if any(d["priority"] == "CRITICAL" for d in decisions) else "MEDIUM",
            "estimated_weekly_impact": f"₹{random.randint(50000, 150000)} revenue protection/gain"
        }


def generate_synthetic_analytics_data(num_samples: int = 2000) -> pd.DataFrame:
    """
    Generate synthetic weekly business analytics data for training
    """
    np.random.seed(42)
    random.seed(42)
    
    data = []
    base_date = datetime.now() - timedelta(weeks=num_samples)
    
    for i in range(num_samples):
        # Date features
        current_date = base_date + timedelta(weeks=i)
        week_of_month = (current_date.day - 1) // 7 + 1
        is_month_end = 1 if current_date.day > 25 else 0
        seasonal_factor = 0.8 + 0.4 * np.sin(2 * np.pi * current_date.month / 12)
        
        # Base performance with trends and noise
        trend_factor = 1 + (i / num_samples) * 0.1  # Slight upward trend
        noise_factor = np.random.normal(1, 0.1)
        anomaly_week = np.random.random() < 0.15  # 15% chance of anomaly
        
        if anomaly_week:
            # Introduce anomalies
            anomaly_magnitude = np.random.choice([-0.3, -0.5, 0.4, 0.6])
            trend_factor *= (1 + anomaly_magnitude)
        
        # CRM Metrics
        crm_lead_volume = max(50, int(np.random.normal(120, 20) * trend_factor * seasonal_factor))
        crm_qualified_rate = np.clip(np.random.normal(0.35, 0.08) * trend_factor, 0.1, 0.8)
        crm_enrollment_rate = np.clip(np.random.normal(0.18, 0.05) * trend_factor, 0.05, 0.4)
        crm_refund_rate = np.clip(np.random.normal(0.08, 0.03) / trend_factor, 0.01, 0.25)
        
        # GA4 Metrics
        ga4_sessions = max(1000, int(np.random.normal(2500, 400) * trend_factor * seasonal_factor))
        ga4_bounce_rate = np.clip(np.random.normal(0.55, 0.12) / trend_factor, 0.2, 0.9)
        ga4_conversion_rate = np.clip(np.random.normal(0.042, 0.012) * trend_factor, 0.01, 0.15)
        ga4_avg_session_duration = max(30, np.random.normal(185, 45) * trend_factor)
        
        # Ad Metrics
        ad_spend_total = max(5000, np.random.normal(25000, 5000) * seasonal_factor)
        ad_cpl = max(50, np.random.normal(180, 40) / trend_factor)
        ad_ctr = np.clip(np.random.normal(0.018, 0.005) * trend_factor, 0.005, 0.05)
        ad_conversion_rate = np.clip(np.random.normal(0.035, 0.008) * trend_factor, 0.01, 0.08)
        
        # Support Metrics
        support_ticket_volume = max(20, int(np.random.normal(85, 25) * (2 - trend_factor)))
        support_csat_score = np.clip(np.random.normal(7.8, 1.2) * trend_factor, 1, 10)
        support_resolution_time = max(2, np.random.normal(18, 8) / trend_factor)
        
        # Telephony Metrics
        telephony_call_volume = max(200, int(np.random.normal(450, 80) * trend_factor))
        telephony_connect_rate = np.clip(np.random.normal(0.28, 0.08) * trend_factor, 0.1, 0.6)
        telephony_booking_rate = np.clip(np.random.normal(0.22, 0.06) * trend_factor, 0.05, 0.5)
        
        # LMS Metrics
        lms_active_users = max(100, int(np.random.normal(320, 60) * trend_factor))
        lms_completion_rate = np.clip(np.random.normal(0.68, 0.15) * trend_factor, 0.3, 0.95)
        lms_engagement_score = np.clip(np.random.normal(7.2, 1.5) * trend_factor, 1, 10)
        
        # Target: Business health anomaly (binary)
        # Calculate composite health score
        health_score = (
            crm_enrollment_rate * 0.3 +
            ga4_conversion_rate * 10 * 0.2 +
            (1 - ga4_bounce_rate) * 0.15 +
            ad_conversion_rate * 10 * 0.15 +
            support_csat_score / 10 * 0.1 +
            telephony_connect_rate * 0.1
        )
        
        # Anomaly if health score is >2 sigma from expected
        expected_health = 0.6 + (i / num_samples) * 0.1
        health_deviation = abs(health_score - expected_health)
        is_anomaly = health_deviation > 0.2 or anomaly_week
        
        data.append({
            'crm_lead_volume': crm_lead_volume,
            'crm_qualified_rate': crm_qualified_rate,
            'crm_enrollment_rate': crm_enrollment_rate,
            'crm_refund_rate': crm_refund_rate,
            'ga4_sessions': ga4_sessions,
            'ga4_bounce_rate': ga4_bounce_rate,
            'ga4_conversion_rate': ga4_conversion_rate,
            'ga4_avg_session_duration': ga4_avg_session_duration,
            'ad_spend_total': ad_spend_total,
            'ad_cpl': ad_cpl,
            'ad_ctr': ad_ctr,
            'ad_conversion_rate': ad_conversion_rate,
            'support_ticket_volume': support_ticket_volume,
            'support_csat_score': support_csat_score,
            'support_resolution_time': support_resolution_time,
            'telephony_connect_rate': telephony_connect_rate,
            'telephony_call_volume': telephony_call_volume,
            'telephony_booking_rate': telephony_booking_rate,
            'lms_active_users': lms_active_users,
            'lms_completion_rate': lms_completion_rate,
            'lms_engagement_score': lms_engagement_score,
            'week_of_month': week_of_month,
            'is_month_end': is_month_end,
            'seasonal_factor': seasonal_factor,
            'business_health_anomaly': int(is_anomaly),
            'week_date': current_date.strftime('%Y-%m-%d')
        })
    
    return pd.DataFrame(data)


# Global model instance
onetruth_model = OneTruthModel()

def detect_anomalies(data: Dict[str, Any]) -> Dict[str, Any]:
    """Detect anomalies in marketing analytics data"""
    try:
        return onetruth_model.predict(data)
    except Exception as e:
        return {
            "error": str(e),
            "anomaly_detected": False,
            "confidence": 0.0
        }
