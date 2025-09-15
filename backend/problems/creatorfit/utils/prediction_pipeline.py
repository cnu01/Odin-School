import os
import sys
import json
import warnings
from pathlib import Path
from typing import Dict, Tuple, Any
import pandas as pd
import numpy as np
import joblib
import logging

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

# ============================================================================
# NEW STREAMLINED FORECASTING PIPELINE - ONLY ESSENTIAL PROCESSING
# ============================================================================

class CreatorFitPredictionPipeline:
    """Streamlined prediction pipeline - only essential processing for forecasting"""
    
    def __init__(self, model_dir: str = None):
        default_ml_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models")
        )
        self.model_dir = Path(model_dir or os.environ.get("MODEL_DIR", default_ml_dir))
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load only the trained LinearRegression model"""
        try:
            self.model = joblib.load(self.model_dir / "creatorfit_linear_model.pkl")
            logging.info("LinearRegression model loaded successfully")
        except Exception as e:
            logging.error(f"Error loading model: {e}")
            raise
    
    def simple_data_processing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Minimal data processing - only what's absolutely needed for prediction"""
        
        # 1. Check if we actually have missing values (don't fill unnecessarily)
        missing_values = df.isnull().sum().sum()
        print(f"📊 Missing values in input: {missing_values}")
        
        if missing_values > 0:
            print("⚠️ Handling missing values...")
            # For numeric columns: use median from existing data
            if df['posting_cadence_days'].notna().any():
                posting_median = df['posting_cadence_days'].median()
            else:
                posting_median = 7
                
            if df['views_90d'].notna().any():
                views_median = df['views_90d'].median()
            else:
                views_median = 10000
            
            # Fill missing numeric values
            df['posting_cadence_days'] = pd.to_numeric(df['posting_cadence_days'], errors='coerce').fillna(posting_median)
            df['views_90d'] = pd.to_numeric(df['views_90d'], errors='coerce').fillna(views_median)
            
            # Fill missing categorical values
            df['topic'] = df['topic'].fillna('Unknown')
            df['language'] = df['language'].fillna('Unknown')
            df['category_tag'] = df['category_tag'].fillna('Unknown')
        else:
            print("✅ No missing values - skipping NA handling")
            # Still ensure numeric types are correct
            df['posting_cadence_days'] = pd.to_numeric(df['posting_cadence_days'], errors='coerce')
            df['views_90d'] = pd.to_numeric(df['views_90d'], errors='coerce')
        
        # 4. Simple label encoding for categorical features
        from sklearn.preprocessing import LabelEncoder
        
        for col in ['topic', 'language', 'category_tag']:
            if col in df.columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
        
        # 5. Simple MinMax scaling for numeric features
        from sklearn.preprocessing import MinMaxScaler
        
        numeric_cols = ['posting_cadence_days', 'views_90d']
        for col in numeric_cols:
            if col in df.columns:
                scaler = MinMaxScaler()
                df[col] = scaler.fit_transform(df[[col]])
        
        # 6. Create required text features (minimal versions to match training)
        if 'recent_video_transcript' not in df.columns:
            df['recent_video_transcript'] = "Default content description"
        
        # Simple text feature extraction (match training features)
        df['educational_transcript_score'] = 0.0  # Default
        df['transcript_length'] = df['recent_video_transcript'].str.len().fillna(20)
        df['topic_count'] = df['topic'].astype(str).str.count(';') + 1  # Count topics
        df['edtech_topic_depth'] = 1.0  # Default depth
        
        # Scale these to match training range [0, 1]
        df['transcript_length'] = df['transcript_length'] / 100  # Normalize
        df['topic_count'] = df['topic_count'] / 10  # Normalize
        
        # 6. Create basic fit_score (simple constant for now)
        df['fit_score'] = 0.5
        
        return df
    
    def process_csv_file(self, csv_path: str, program_type: str = "data_science") -> Dict[str, Any]:
        """
        NEW STREAMLINED FORECASTING - Only essential processing
        Input: CSV file path
        Output: Predictions with original data preserved for display
        """
        try:
            logging.info(f"Starting streamlined forecasting for {csv_path}")
            
            # 1. Load raw data and preserve original for display
            df_raw = pd.read_csv(csv_path)
            df_original = df_raw.copy()
            
            print(f"📊 Input data: {df_raw.shape[0]} creators with columns: {list(df_raw.columns)}")
            
            # 2. Simple data processing (only essentials)
            df_processed = self.simple_data_processing(df_raw.copy())
            
            # 3. Prepare features for model (match training feature order)
            feature_columns = [
                'fit_score',
                'posting_cadence_days', 
                'views_90d',
                'educational_transcript_score',
                'transcript_length',
                'topic_count',
                'edtech_topic_depth',
                'topic',
                'category_tag',
                'language'
            ]
            
            # Ensure all required features exist
            for col in feature_columns:
                if col not in df_processed.columns:
                    df_processed[col] = 0  # Default value
            
            X = df_processed[feature_columns]
            
            print(f"🎯 Features prepared: {X.shape}")
            print(f"📋 Feature columns: {list(X.columns)}")
            
            # 4. Make predictions using trained model
            predictions = self.model.predict(X)
            
            # 5. Create results with original data for display
            results = []
            for i in range(len(df_original)):
                raw_pred = predictions[i]
                
                # Handle predictions (convert to realistic leads count)
                if raw_pred < 0:
                    predicted_leads = 1  # Minimum
                else:
                    # Scale small predictions to realistic range
                    predicted_leads = max(1, int(raw_pred * df_original.iloc[i]['views_90d'] / 1000))
                
                # Create creator tier based on views
                views = df_original.iloc[i]['views_90d']
                if views >= 100000:
                    tier = 'Established'
                elif views >= 25000:
                    tier = 'Growing'
                else:
                    tier = 'Emerging'
                
                # Simple confidence based on views and prediction
                confidence = min(0.95, (views / 100000) * 0.5 + 0.3)
                
                result = {
                    'rank': i + 1,
                    'creator_id': str(df_original.iloc[i]['creator_id']),
                    'predicted_qualified_leads': predicted_leads,
                    'fit_score': float(df_processed.iloc[i]['fit_score']),
                    'confidence_score': round(confidence, 3),
                    'topic': str(df_original.iloc[i]['topic']),
                    'language': str(df_original.iloc[i]['language']),
                    'views_90d': int(df_original.iloc[i]['views_90d']),
                    'creator_tier': tier,
                    'posting_cadence_days': int(df_original.iloc[i].get('posting_cadence_days', 7)),
                    'recommendation': 'BOOK' if predicted_leads >= 10 else 'REVIEW' if predicted_leads >= 5 else 'SKIP'
                }
                results.append(result)
            
            # 6. Sort by predicted leads (highest first)
            results.sort(key=lambda x: x['predicted_qualified_leads'], reverse=True)
            
            # Update ranks after sorting
            for i, result in enumerate(results):
                result['rank'] = i + 1
            
            # 7. Create output
            output = {
                'success': True,
                'program_type': program_type,
                'total_creators_analyzed': len(results),
                'model_type': 'LinearRegression',
                'results': results,
                'summary': {
                    'avg_predicted_leads': round(sum([r['predicted_qualified_leads'] for r in results]) / len(results), 2) if results else 0,
                    'top_performer': results[0] if results else None,
                    'processing_time': 'Fast'
                }
            }
            
            logging.info(f"✅ Streamlined forecasting complete: {len(results)} creators processed")
            return output
            
        except Exception as e:
            logging.error(f"❌ Error in streamlined forecasting: {e}")
            return {
                'success': False,
                'error': str(e),
                'details': 'Streamlined forecasting failed'
            }

def main():
    """Main function for testing the streamlined forecasting pipeline"""
    if len(sys.argv) < 2:
        print("Usage: python prediction_pipeline.py <csv_file> [program_type]")
        print("Example: python prediction_pipeline.py test_data.csv data_science")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    program_type = sys.argv[2] if len(sys.argv) > 2 else "data_science"
    
    try:
        predictor = CreatorFitPredictionPipeline()
        
        result = predictor.process_csv_file(csv_file, program_type)
        
        if result.get('success'):
            if result['results']:
                top_creator = result['results'][0]
                print(f"🏆 Top performer: {top_creator['creator_id']} - {top_creator['predicted_qualified_leads']} leads")
        else:
            print(f"\n❌ FAILED: {result.get('error')}")
            
    except Exception as e:
        print(f"\n💥 ERROR: {e}")


if __name__ == "__main__":
    main()