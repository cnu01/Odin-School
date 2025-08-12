import os
import tempfile
from pathlib import Path
from typing import Dict, Any

from .models import PredictionResponse, AnalysisRequest, ErrorResponse

class CreatorFitService:
    """Simple service for CreatorFit CSV analysis and lead forecasting"""
    
    def __init__(self):
        # No database needed - everything runs from trained models
        pass
    
    async def analyze_csv(self, csv_content: bytes, program_type: str = "data_science", 
                         campaign_budget: float = 100000) -> Dict[str, Any]:
        """
        Analyze CSV file using our existing ML pipeline
        This integrates with the prediction_pipeline.py we built yesterday
        """
        try:
            # Save uploaded CSV to temporary file
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as temp_file:
                temp_file.write(csv_content)
                temp_csv_path = temp_file.name
            
            # Import and run our existing prediction pipeline
            try:
                # Add necessary paths to Python path
                import sys
                project_root = Path(__file__).parent.parent.parent
                creatorfit_path = str(Path(__file__).parent)
                
                if str(project_root) not in sys.path:
                    sys.path.append(str(project_root))
                if creatorfit_path not in sys.path:
                    sys.path.append(creatorfit_path)
                
                # Import our existing pipeline
                from problems.creatorfit.frontend.prediction_pipeline import CreatorFitPredictionPipeline
                
                # Initialize predictor with correct model path (uses our trained models)
                # Use absolute path to models directory
                models_path = Path(__file__).parent.parent.parent / "models"
                print(f"DEBUG: Loading models from: {models_path}")
                print(f"DEBUG: Models directory exists: {models_path.exists()}")
                if models_path.exists():
                    print(f"DEBUG: Model files: {list(models_path.glob('*.pkl'))}")
                
                predictor = CreatorFitPredictionPipeline(model_dir=str(models_path))
                
                # Run prediction pipeline
                result = predictor.process_csv_file(temp_csv_path, program_type)
                
                # No database saving needed
                
                return result
                
            except ImportError as e:
                # Fallback to basic processing if ML pipeline not available
                print(f"DEBUG: Import error: {e}")
                return {
                    'success': False,
                    'error': f'ML pipeline not available: {str(e)}',
                    'details': 'Please ensure the prediction pipeline is properly set up'
                }
            except Exception as e:
                # Catch any other errors during pipeline execution
                print(f"DEBUG: Pipeline execution error: {e}")
                return {
                    'success': False,
                    'error': f'Pipeline execution failed: {str(e)}',
                    'details': 'Check the debug output for more information'
                }
            
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_csv_path)
                except:
                    pass
                    
        except Exception as e:
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}',
                'details': 'Check CSV format and try again'
            }
    
    async def forecast_leads(self, creator_data: Dict[str, Any], program_type: str = "data_science") -> Dict[str, Any]:
        """
        Forecast qualified leads for a specific creator
        """
        try:
            # Create temporary CSV with single creator data
            import pandas as pd
            df = pd.DataFrame([creator_data])
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
                df.to_csv(temp_file, index=False)
                temp_csv_path = temp_file.name
            
            # Use our existing pipeline for single creator prediction
            try:
                # Add necessary paths to Python path
                import sys
                project_root = Path(__file__).parent.parent.parent
                creatorfit_path = str(Path(__file__).parent)
                
                if str(project_root) not in sys.path:
                    sys.path.append(str(project_root))
                if creatorfit_path not in sys.path:
                    sys.path.append(creatorfit_path)
                
                from problems.creatorfit.frontend.prediction_pipeline import CreatorFitPredictionPipeline
                # Use absolute path to models directory
                models_path = Path(__file__).parent.parent.parent / "models"
                print(f"DEBUG: Loading models from: {models_path}")
                print(f"DEBUG: Models directory exists: {models_path.exists()}")
                if models_path.exists():
                    print(f"DEBUG: Model files: {list(models_path.glob('*.pkl'))}")
                
                predictor = CreatorFitPredictionPipeline(model_dir=str(models_path))
                result = predictor.process_csv_file(temp_csv_path, program_type)
                
                return result
                
            except ImportError as e:
                print(f"DEBUG: Import error in forecast: {e}")
                return {
                    'success': False,
                    'error': f'Prediction pipeline not available: {str(e)}'
                }
            except Exception as e:
                print(f"DEBUG: Pipeline execution error in forecast: {e}")
                return {
                    'success': False,
                    'error': f'Pipeline execution failed: {str(e)}',
                    'details': 'Check the debug output for more information'
                }
            
            finally:
                try:
                    os.unlink(temp_csv_path)
                except:
                    pass
                    
        except Exception as e:
            return {
                'success': False,
                'error': f'Lead forecasting failed: {str(e)}'
            }
    

