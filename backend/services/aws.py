import boto3
import json
import os
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
import logging
from typing import Optional, Dict, Any

load_dotenv()
logger = logging.getLogger(__name__)

class AWSService:
    """Base AWS service class for all AWS integrations"""
    
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-west-2")
        self.session = self._create_session()
    
    def _create_session(self) -> boto3.Session:
        """Create AWS session with credentials"""
        try:
            # Try to create session with environment variables or default credentials
            session = boto3.Session(
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=self.region
            )
            # Test the credentials
            sts = session.client('sts')
            sts.get_caller_identity()
            logger.info("AWS credentials configured successfully")
            return session
        except (ClientError, NoCredentialsError) as e:
            logger.warning(f"AWS credentials not configured: {e}")
            # Return a session anyway for testing - services will handle auth errors
            return boto3.Session(region_name=self.region)
    
    def is_configured(self) -> bool:
        """Check if AWS is properly configured"""
        try:
            access_key = os.getenv('AWS_ACCESS_KEY_ID')
            secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            
            if not access_key or not secret_key:
                return False
                
            sts = self.session.client('sts')
            sts.get_caller_identity()
            return True
        except Exception:
            return False

class BedrockService(AWSService):
    """AWS Bedrock service for LLM interactions"""
    
    def __init__(self):
        super().__init__()
        self.bedrock_runtime = None
        self.model_id = os.getenv("CLAUDE_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Bedrock runtime client"""
        try:
            self.bedrock_runtime = self.session.client(
                'bedrock-runtime',
                region_name=os.getenv("BEDROCK_REGION", "us-west-2")
            )
            logger.info("Bedrock client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
    
    async def generate_text(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """Generate text using Claude via Bedrock"""
        if not self.bedrock_runtime:
            logger.error("Bedrock client not initialized")
            return None
        
        try:
            # Format prompt for Claude 3 (new format)
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "top_p": 0.9,
            }
            
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract content from Claude 3 response format
            if 'content' in response_body and len(response_body['content']) > 0:
                return response_body['content'][0]['text']
            else:
                return response_body.get('completion', '').strip()
            
        except Exception as e:
            logger.error(f"Bedrock API error: {e}")
            return None
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text using Claude"""
        prompt = f"""Analyze the sentiment of the following text and provide a detailed response in JSON format:

Text: "{text}"

Please provide the analysis in this exact JSON format:
{{
    "sentiment": "positive|negative|neutral",
    "confidence": 0.85,
    "emotions": ["joy", "excitement"],
    "key_phrases": ["great experience", "highly recommend"],
    "overall_score": 0.8
}}"""
        
        response = await self.generate_text(prompt, max_tokens=500)
        if response:
            try:
                # Extract JSON from response
                import json
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    return json.loads(response[json_start:json_end])
            except Exception as e:
                logger.error(f"Failed to parse sentiment analysis: {e}")
        
        # Return default response if analysis fails
        return {
            "sentiment": "neutral",
            "confidence": 0.5,
            "emotions": [],
            "key_phrases": [],
            "overall_score": 0.5
        }

# Global service instances
aws_service = AWSService()
bedrock_service = BedrockService()
bedrock_client = bedrock_service  # Alias for backward compatibility

# Service status check
def get_aws_status() -> Dict[str, bool]:
    """Get status of all AWS services"""
    return {
        "aws_configured": aws_service.is_configured(),
        "bedrock_available": bedrock_service.bedrock_runtime is not None,
        "mock_mode": False
    }

# Service getters
def get_bedrock_service():
    """Get Bedrock service"""
    return bedrock_service
