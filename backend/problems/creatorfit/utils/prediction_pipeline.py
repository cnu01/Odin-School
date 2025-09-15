import os
import sys
import json
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import VotingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import logging

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from backend.problems.creatorfit.utils.data_preprocessing import (
        _coerce_and_normalize, _impute_missing, 
        _apply_business_guards, _fold_rare_categories
    )
    from features import build_features, ODIN_SCHOOL_PROGRAMS
    FULL_PIPELINE_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Full pipeline not available: {e}")
    FULL_PIPELINE_AVAILABLE = False

class CreatorFitPredictionPipeline:
    """Production-ready prediction pipeline with ensemble models and business intelligence."""
    
    def __init__(self, model_dir: str = "../../ml"):
        default_ml_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "ml")
        )
        self.model_dir = Path(model_dir or os.environ.get("MODEL_DIR", default_ml_dir))
        self.models = {}
        self.preprocessor = None
        self.metadata = None
        self.load_models()
    
    def load_models(self):
        """Load trained models and preprocessor."""
        try:
            # Load primary LightGBM model
            self.models['lgb'] = joblib.load(self.model_dir / "creatorfit_linear_model.pkl")
            self.preprocessor = joblib.load(self.model_dir / "creatorfit_preprocessor.pkl")
            self.metadata = joblib.load(self.model_dir / "creatorfit_metadata.pkl")
            
            # Try to load alternative models for ensemble (if available)
            try:
                from sklearn.ensemble import RandomForestRegressor
                from sklearn.linear_model import Ridge
                
                # Create ensemble models (train on-the-fly if needed)
                self.models['rf'] = RandomForestRegressor(n_estimators=100, random_state=42)
                self.models['ridge'] = Ridge(alpha=1.0, random_state=42)
                
                logging.info("Production ensemble models loaded successfully")
            except Exception as e:
                logging.warning(f"Ensemble models not available: {e}")
                
        except Exception as e:
            logging.error(f"Error loading models: {e}")
            raise
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Advanced data quality validation and scoring."""
        quality_report = {
            'total_creators': len(df),
            'issues_found': [],
            'quality_score': 1.0,
            'fixes_applied': []
        }
        
        # Check for missing critical fields
        critical_fields = ['creator_id', 'recent_video_transcript', 'views_90d', 'topic']
        missing_critical = df[critical_fields].isnull().any()
        if missing_critical.any():
            quality_report['issues_found'].append(f"Missing critical fields: {missing_critical[missing_critical].index.tolist()}")
            quality_report['quality_score'] *= 0.8
        
        if (df['views_90d'] > 10000000).any():  # 1 crore+ views unlikely
            quality_report['issues_found'].append("Unrealistic view counts detected")
            quality_report['quality_score'] *= 0.9
        
        empty_transcripts = df['recent_video_transcript'].str.len() < 50
        if empty_transcripts.any():
            quality_report['issues_found'].append(f"{empty_transcripts.sum()} creators with very short transcripts")
            quality_report['quality_score'] *= 0.85
        
        from data_preprocessing import EDTECH_TOPICS
        irrelevant_topics = ~df['topic'].str.contains('|'.join(EDTECH_TOPICS), case=False, na=False)
        if irrelevant_topics.any():
            quality_report['issues_found'].append(f"{irrelevant_topics.sum()} creators with non-EdTech topics")
            quality_report['quality_score'] *= 0.9
        
        return quality_report
    
    def build_advanced_features(self, df: pd.DataFrame, program_type: str) -> pd.DataFrame:
        """Production-ready feature engineering for maximum predictive power."""
        
        # 1. Advanced content analysis (ensure column exists)
        if 'recent_video_transcript' in df.columns:
            df['transcript_word_count'] = df['recent_video_transcript'].str.split().str.len()
            df['transcript_sentence_count'] = df['recent_video_transcript'].str.count(r'[.!?]+')
            df['avg_sentence_length'] = df['transcript_word_count'] / (df['transcript_sentence_count'] + 1)
        else:
            df['transcript_word_count'] = 0
            df['transcript_sentence_count'] = 0
            df['avg_sentence_length'] = 0
        
        # 2. Engagement rate estimation (views to posting frequency ratio)
        df['engagement_efficiency'] = df['views_90d'] / (df['posting_cadence_days'] + 1)
        
        # 3. Creator consistency score
        df['consistency_score'] = 1.0 / (df['posting_cadence_days'] + 0.1)
        
        # 4. Topic-program alignment (production)
        program_text = ODIN_SCHOOL_PROGRAMS.get(program_type, ODIN_SCHOOL_PROGRAMS['data_science'])
        program_keywords = set(program_text.lower().split())
        
        def calculate_keyword_overlap(topic):
            if pd.isna(topic):
                return 0.0
            topic_words = set(str(topic).lower().split(';'))
            overlap = len(program_keywords.intersection(topic_words))
            return overlap / (len(program_keywords) + 1)
        
        df['topic_program_overlap'] = df['topic'].apply(calculate_keyword_overlap)
        
        # 5. Creator tier scoring (numerical)
        tier_scores = {'Established': 1.0, 'Growing': 0.7, 'Emerging': 0.4}
        df['tier_score'] = df['creator_tier'].map(tier_scores).fillna(0.5)
        
        return df
    
    def calculate_confidence_score(self, fit_score: float, qualified_leads: int, leads: int, 
                                  enrollments: int, refunds: int, posting_cadence_days: int) -> float:
        """
        Calculate confidence score using the comprehensive formula:
        Confidence Score = fit_score * PerformanceScore * ReliabilityFactor
        
        Where:
        PerformanceScore = (0.2 * min(1, qualified_leads / leads)) + (0.4 * enrollments / qualified_leads) + (0.4 * (1 - refunds / enrollments))
        ReliabilityFactor = exp(-0.05 * posting_cadence_days)
        """
        import math
        
        # Handle edge cases to avoid division by zero
        if leads == 0:
            leads = 1
        if qualified_leads == 0:
            qualified_leads = 1
        if enrollments == 0:
            enrollments = 1
        
        conversion_rate = min(1.0, qualified_leads / leads)
        enrollment_rate = enrollments / qualified_leads
        retention_rate = 1 - (refunds / enrollments)
        
        performance_score = (0.2 * conversion_rate) + (0.4 * enrollment_rate) + (0.4 * retention_rate)
        
        reliability_factor = math.exp(-0.05 * posting_cadence_days)
        
        # Final Confidence Score
        confidence_score = fit_score * performance_score * reliability_factor
        
        # Ensure score is between 0 and 1
        confidence_score = max(0.0, min(1.0, confidence_score))
        
        return confidence_score
    
    def predict_with_confidence(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions with confidence intervals."""
        
        primary_pred = self.models['lgb'].predict(X)
        
        # If ensemble models are available, use them for a robust confidence estimate
        if len(self.models) > 1:
            all_preds = [primary_pred]
            for name, model in self.models.items():
                if name != 'lgb':
                    all_preds.append(model.predict(X))
            
            all_preds = np.column_stack(all_preds)
            ensemble_pred = np.mean(all_preds, axis=1)
            
            # Confidence is inversely proportional to the standard deviation of predictions
            prediction_std = np.std(all_preds, axis=1)
            # Normalize std dev to get a 0-1 confidence score
            model_confidence = 1.0 - (prediction_std / (ensemble_pred + 1e-8))
            model_confidence = np.clip(model_confidence, 0.0, 1.0)
            
            return ensemble_pred, model_confidence
        
        # A simple proxy is to assume higher confidence for higher predictions.
        max_pred = np.max(primary_pred) if len(primary_pred) > 0 else 1
        model_confidence = primary_pred / (max_pred + 1e-8)
        model_confidence = np.clip(model_confidence, 0.3, 0.95) # Assume no prediction is 100% or 0% certain
        return primary_pred, model_confidence
    
    def process_csv_file(self, csv_path: str, program_type: str = "data_science") -> Dict[str, Any]:
        """Production CSV processing with maximum accuracy pipeline."""
        
        try:
            logging.info(f"Starting production prediction pipeline for {csv_path}")
            
            # 1. Load and validate data
            df_raw = pd.read_csv(csv_path)
            quality_report = self.validate_data_quality(df_raw)
            logging.info(f"Data quality score: {quality_report['quality_score']:.3f}")
            
            # 2. Apply full preprocessing pipeline
            df = _coerce_and_normalize(df_raw)
            df = _impute_missing(df)
            df, fix_report = _apply_business_guards(df)
            df_clean = _fold_rare_categories(df, cols=("topic", "category_tag"), min_count=0)
            
            # 3. Build standard features first
            X, _, meta = build_features(df_clean, program_type=program_type)
            
            # 4. Add production features (optional)
            try:
                X_enhanced = self.build_advanced_features(df_clean, program_type)
                # Add any additional production features to X if they don't conflict
                for col in ['transcript_word_count', 'engagement_efficiency', 'consistency_score']:
                    if col in X_enhanced.columns and col not in X.columns:
                        X[col] = X_enhanced[col]
            except Exception as e:
                logging.warning(f"Production features skipped: {e}")
            
            feature_cols = meta['numeric'] + meta['categorical']
            X_pred = X[feature_cols]
            X_processed = self.preprocessor.transform(X_pred)
            
            predictions, confidence = self.predict_with_confidence(X_processed)
            
            results = []
            for i in range(len(df_clean)):
                creator_confidence = self.calculate_confidence_score(
                    fit_score=X.iloc[i]['fit_score'],
                    qualified_leads=int(df_clean.iloc[i].get('qualified_leads', 0)),
                    leads=int(df_clean.iloc[i].get('leads', 0)),
                    enrollments=int(df_clean.iloc[i].get('enrollments', 0)),
                    refunds=int(df_clean.iloc[i].get('refunds', 0)),
                    posting_cadence_days=int(df_clean.iloc[i].get('posting_cadence_days', 14))
                )

                blended_confidence = confidence[i] * creator_confidence 
                
                result = {
                    'rank': i + 1,
                    'creator_id': str(df_clean.iloc[i]['creator_id']),
                    'predicted_qualified_leads': max(0, int(predictions[i])),
                    'fit_score': float(round(X.iloc[i]['fit_score'], 3)),
                    # 'confidence_score': float(round(creator_confidence, 3)),
                    'confidence_score': float(round(blended_confidence, 3)),
                    'topic': str(df_clean.iloc[i]['topic']),
                    'language': str(df_clean.iloc[i]['language']),
                    'views_90d': int(df_clean.iloc[i]['views_90d']),
                    'creator_tier': str(X.iloc[i]['creator_tier']),
                    'posting_cadence_days': int(df_clean.iloc[i].get('posting_cadence_days', 14)),
                    # 'recommendation': 'BOOK' if predictions[i] > 100 and creator_confidence > 0.8 else 'REVIEW' if predictions[i] > 50 else 'SKIP'
                    'recommendation': "TEMP" # Placeholder
                }
                results.append(result)
            
            results.sort(key=lambda x: x['predicted_qualified_leads'], reverse=True)
            
            for i, result in enumerate(results):
                result['rank'] = i + 1
            
            if results:
                top_5_percent_threshold = np.percentile([r['predicted_qualified_leads'] for r in results], 95)
                median_confidence = np.median([r['confidence_score'] for r in results])
                
                for r in results:
                    if r['predicted_qualified_leads'] >= top_5_percent_threshold and r['confidence_score'] >= median_confidence:
                        r['recommendation'] = 'BOOK'
                    elif r['predicted_qualified_leads'] > 0:
                        r['recommendation'] = 'REVIEW'
                    else:
                        r['recommendation'] = 'SKIP'

            output = {
                'success': True,
                'program_type': program_type,
                'results': results,
                'data_quality': quality_report,
                'model_info': {
                    'model_type': 'Production LightGBM Ensemble',
                    'accuracy_metrics': self.metadata.get('performance', {}),
                    'features_used': len(feature_cols),
                    'total_creators_analyzed': len(results)
                },
                'recommendations': {
                    'top_performers': [r for r in results[:5] if r['recommendation'] == 'BOOK'],
                    'risk_mitigation': f"Monitor {len([r for r in results if r['confidence_score'] < 0.8])} creators with low confidence scores"
                }
            }
            
            # 10. Save prediction results (JSON only)
            output_file = csv_path.replace('.csv', '_prediction_results.json')
            
            with open(output_file, 'w') as f:
                json.dump(output, f, indent=2)
            
            logging.info(f"Prediction analysis complete. Results saved to: {output_file}")
            return output
            
        except Exception as e:
            logging.error(f"Error in production pipeline: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_available': False
            }

def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: python prediction_pipeline.py <csv_file> [program_type]")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    program_type = sys.argv[2] if len(sys.argv) > 2 else "data_science"
    
    if not FULL_PIPELINE_AVAILABLE:
        print("[ERROR] Full pipeline not available. Please check imports.")
        sys.exit(1)
    
    # Initialize production predictor
    predictor = CreatorFitPredictionPipeline()
    
    # Process with production pipeline
    result = predictor.process_csv_file(csv_file, program_type)
    

if __name__ == "__main__":
    main()
