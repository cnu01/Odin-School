"""
Base ML Model class for all AI systems - MongoDB Integration
"""
import pickle
import json
import os
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

logger = logging.getLogger(__name__)

def get_database():
    """Get database instance - import here to avoid circular imports"""
    try:
        from database import get_database as _get_database
        return _get_database()
    except ImportError:
        logger.warning("Database not available for metadata storage")
        return None

class BaseMLModel:
    """Base class for all ML models in Odin School AI systems - MongoDB version"""
    
    def __init__(self, model_name: str, model_type: str = "classification"):
        self.model_name = model_name
        self.model_type = model_type  # "classification" or "regression"
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = []
        self.is_trained = False
        self.training_metadata = {}
        
        # Model storage paths - updated for Odin-School
        self.model_dir = "/Users/batman/Movies/odinschool/Odin-School/ml/models"
        self.model_path = os.path.join(self.model_dir, f"{model_name}_model.pkl")
        self.scaler_path = os.path.join(self.model_dir, f"{model_name}_scaler.pkl")
        self.metadata_path = os.path.join(self.model_dir, f"{model_name}_metadata.json")
        
        # Ensure model directory exists
        os.makedirs(self.model_dir, exist_ok=True)
        
        logger.info(f"Initialized {model_name} ML model with MongoDB support")
    
    def prepare_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Prepare features for training or prediction"""
        # This method should be overridden by specific model implementations
        raise NotImplementedError("Subclasses must implement prepare_features method")
    
    async def train(self, training_data: List[Dict[str, Any]], target_column: str) -> Dict[str, Any]:
        """Train the ML model"""
        try:
            logger.info(f"Starting training for {self.model_name} model")
            
            if len(training_data) < 10:
                raise ValueError(f"Not enough training data. Need at least 10 samples, got {len(training_data)}")
            
            # Prepare features and targets
            X = []
            y = []
            
            for record in training_data:
                features = self.prepare_features(record)
                target = record.get(target_column)
                
                if features is not None and target is not None:
                    X.append(features)
                    y.append(target)
            
            if len(X) == 0:
                raise ValueError("No valid training samples found")
            
            X = np.array(X)
            y = np.array(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y if self.model_type == "classification" else None
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Encode labels for classification
            if self.model_type == "classification":
                y_train_encoded = self.label_encoder.fit_transform(y_train)
                y_test_encoded = self.label_encoder.transform(y_test)
            else:
                y_train_encoded = y_train
                y_test_encoded = y_test
            
            # Train the model (to be implemented by subclasses)
            self.model = self._create_model()
            self.model.fit(X_train_scaled, y_train_encoded)
            
            # Evaluate
            y_pred = self.model.predict(X_test_scaled)
            
            if self.model_type == "classification":
                y_pred_original = self.label_encoder.inverse_transform(y_pred)
                accuracy = accuracy_score(y_test, y_pred_original)
                
                metrics = {
                    "accuracy": accuracy,
                    "classification_report": classification_report(y_test, y_pred_original, output_dict=True),
                    "training_samples": len(X_train),
                    "test_samples": len(X_test),
                    "features_count": X.shape[1]
                }
            else:
                from sklearn.metrics import mean_squared_error, r2_score
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                metrics = {
                    "mse": mse,
                    "rmse": np.sqrt(mse),
                    "r2_score": r2,
                    "training_samples": len(X_train),
                    "test_samples": len(X_test),
                    "features_count": X.shape[1]
                }
            
            # Save training metadata
            self.training_metadata = {
                "model_name": self.model_name,
                "model_type": self.model_type,
                "trained_at": datetime.now().isoformat(),
                "training_data_size": len(training_data),
                "feature_columns": self.feature_columns,
                "metrics": metrics
            }
            
            self.is_trained = True
            
            # Save model
            self.save_model()
            
            # Store training metadata in MongoDB
            await self._save_metadata_to_db()
            
            logger.info(f"Training completed for {self.model_name}. Metrics: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Training failed for {self.model_name}: {str(e)}")
            raise
    
    async def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make predictions using the trained model"""
        try:
            if not self.is_trained and not self.load_model():
                raise ValueError(f"Model {self.model_name} is not trained")
            
            # Prepare features
            features = self.prepare_features(data)
            if features is None:
                raise ValueError("Failed to prepare features for prediction")
            
            # Scale features
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # Make prediction
            prediction = self.model.predict(features_scaled)[0]
            
            # Get prediction probabilities for classification
            if self.model_type == "classification" and hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(features_scaled)[0]
                prediction_original = self.label_encoder.inverse_transform([prediction])[0]
                
                # Create probability dict
                prob_dict = {}
                for i, class_label in enumerate(self.label_encoder.classes_):
                    prob_dict[str(class_label)] = float(probabilities[i])
                
                return {
                    "prediction": prediction_original,
                    "confidence": float(max(probabilities)),
                    "probabilities": prob_dict,
                    "model_name": self.model_name,
                    "prediction_timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "prediction": float(prediction),
                    "model_name": self.model_name,
                    "prediction_timestamp": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Prediction failed for {self.model_name}: {str(e)}")
            raise
    
    def save_model(self):
        """Save trained model to disk"""
        try:
            if self.model is not None:
                joblib.dump(self.model, self.model_path)
                joblib.dump(self.scaler, self.scaler_path)
                
                # Save label encoder for classification models
                if self.model_type == "classification":
                    label_encoder_path = os.path.join(self.model_dir, f"{self.model_name}_label_encoder.pkl")
                    joblib.dump(self.label_encoder, label_encoder_path)
                
                with open(self.metadata_path, 'w') as f:
                    json.dump(self.training_metadata, f, indent=2)
                
                logger.info(f"Model {self.model_name} saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save model {self.model_name}: {str(e)}")
            raise
    
    def load_model(self) -> bool:
        """Load trained model from disk"""
        try:
            if (os.path.exists(self.model_path) and 
                os.path.exists(self.scaler_path) and 
                os.path.exists(self.metadata_path)):
                
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                
                # Load label encoder for classification models
                if self.model_type == "classification":
                    label_encoder_path = os.path.join(self.model_dir, f"{self.model_name}_label_encoder.pkl")
                    if os.path.exists(label_encoder_path):
                        self.label_encoder = joblib.load(label_encoder_path)
                
                with open(self.metadata_path, 'r') as f:
                    self.training_metadata = json.load(f)
                
                self.feature_columns = self.training_metadata.get("feature_columns", [])
                self.is_trained = True
                logger.info(f"Model {self.model_name} loaded successfully")
                return True
            
            logger.warning(f"Model files not found for {self.model_name}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {str(e)}")
            return False
    
    async def _save_metadata_to_db(self):
        """Save model metadata to MongoDB"""
        try:
            db = get_database()
            if db is not None:
                collection = db["model_metadata"]
                metadata_doc = {
                    "_id": self.model_name,
                    "model_name": self.model_name,
                    "model_type": self.model_type,
                    "is_trained": self.is_trained,
                    "training_metadata": self.training_metadata,
                    "updated_at": datetime.now()
                }
                await collection.replace_one(
                    {"_id": self.model_name}, 
                    metadata_doc, 
                    upsert=True
                )
                logger.info(f"Model metadata saved to MongoDB for {self.model_name}")
        except Exception as e:
            logger.warning(f"Failed to save metadata to MongoDB: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and metadata"""
        return {
            "model_name": self.model_name,
            "model_type": self.model_type,
            "is_trained": self.is_trained,
            "metadata": self.training_metadata,
            "model_files_exist": (
                os.path.exists(self.model_path) and 
                os.path.exists(self.scaler_path) and 
                os.path.exists(self.metadata_path)
            )
        }
    
    def _create_model(self):
        """Create the ML model instance - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _create_model method")
