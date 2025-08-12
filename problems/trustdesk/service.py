import boto3
import json
import os
from dotenv import load_dotenv
from .models import AnalyzedComment, CommentRequest, AIAnalysisResponse

# Load environment variables
load_dotenv()

# BEDROCK CLIENT SETUP
# Create a global boto3 client for the Bedrock Runtime service
bedrock_client = boto3.client(
    'bedrock-runtime',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

async def get_bedrock_analysis(comment_text: str) -> dict:
    """
    Call Amazon Bedrock Claude model for comment analysis
    
    Args:
        comment_text: The customer comment to analyze
        
    Returns:
        Dictionary containing AI analysis results from Bedrock
    """
    try:
        # Construct the detailed prompt for Claude model
        prompt = f"""You are 'TrustDesk', an AI brand reputation analyst for Odin School, an online education platform. Your task is to analyze a user's comment and provide a structured analysis to help the human support team.

Your tone must be professional, empathetic, and helpful.

**BRAND VOICE GUIDE:**
- **DO:** Acknowledge the user's feelings, be reassuring, and guide them toward official support channels.
- **DO NOT:** Make specific financial promises (e.g., "you will get a refund"), admit legal fault, or argue with the user.

**YOUR TASK:**
Analyze the user's comment provided below. Based on your analysis, you must return ONLY a single, valid JSON object with the following four keys and nothing else:

1.  `"urgency"`: Classify the urgency. Must be one of: 'High', 'Medium', or 'Low'.
2.  `"is_sensitive"`: A boolean (true/false) indicating if the comment contains sensitive topics like threats, legal action, or serious accusations.
3.  `"summary"`: A concise, one-sentence summary of the user's main point.
4.  `"draft_reply"`: Draft a safe, empathetic, on-brand reply. If the comment is negative, acknowledge their experience without admitting fault and guide them to a support contact. If it's a simple question, provide a helpful, generic answer.

Here is the user comment:
---
{comment_text}
---"""

        # Prepare the request body for Bedrock Claude model
        request_body = {
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": 1000,
            "temperature": 0.1,
            "top_k": 250,
            "top_p": 1,
            "stop_sequences": ["\n\nHuman:"]
        }
        
        # Invoke the Bedrock model
        response = bedrock_client.invoke_model(
            body=json.dumps(request_body),
            modelId='anthropic.claude-v2',
            accept='application/json',
            contentType='application/json'
        )
        
        # Parse the response from Bedrock
        response_body = json.loads(response.get('body').read())
        generated_text = response_body.get('completion', '').strip()
        
        # Extract and parse JSON from the generated text
        try:
            # Claude sometimes includes extra text, so we need to extract just the JSON
            if '{' in generated_text and '}' in generated_text:
                start_idx = generated_text.find('{')
                end_idx = generated_text.rfind('}') + 1
                json_str = generated_text[start_idx:end_idx]
                analysis_result = json.loads(json_str)
            else:
                raise ValueError("No valid JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback response if JSON parsing fails
            analysis_result = {
                "urgency": "Medium",
                "is_sensitive": False,
                "summary": "Unable to parse AI response, manual review required.",
                "draft_reply": "Thank you for your feedback. We've received your message and our team will review it shortly. For immediate assistance, please contact our support team."
            }
        
        return analysis_result
        
    except Exception as e:
        # Handle any errors during the Bedrock API call
        raise Exception(f"Error calling Bedrock API: {str(e)}")

async def get_ai_analysis(comment_text: str) -> dict:
    """
    Legacy wrapper function for backward compatibility
    Calls the new Bedrock analysis function
    
    Args:
        comment_text: The customer comment to analyze
        
    Returns:
        Dictionary containing AI analysis results
    """
    try:
        # Get Bedrock analysis
        bedrock_result = await get_bedrock_analysis(comment_text)
        
        # Convert Bedrock response to legacy format for backward compatibility
        urgency_score_map = {"High": 8, "Medium": 5, "Low": 2}
        sentiment_map = {
            "High": "Negative" if bedrock_result.get("is_sensitive", False) else "Neutral",
            "Medium": "Neutral", 
            "Low": "Positive"
        }
        
        legacy_result = {
            "sentiment": sentiment_map.get(bedrock_result.get("urgency", "Medium"), "Neutral"),
            "urgency_score": urgency_score_map.get(bedrock_result.get("urgency", "Medium"), 5),
            "is_sensitive": bedrock_result.get("is_sensitive", False),
            "suggested_reply": bedrock_result.get("draft_reply", "Thank you for your feedback.")
        }
        
        return legacy_result
        
    except Exception as e:
        raise Exception(f"Error in AI analysis: {str(e)}")

async def analyze_comment(comment_request: CommentRequest) -> AIAnalysisResponse:
    """
    New Bedrock-compatible comment analysis function
    
    Args:
        comment_request: CommentRequest containing the text to analyze
        
    Returns:
        AIAnalysisResponse with Bedrock analysis results
    """
    try:
        # Get analysis from Bedrock
        analysis_result = await get_bedrock_analysis(comment_request.text)
        
        # Return structured response
        return AIAnalysisResponse(**analysis_result)
        
    except Exception as e:
        # Return fallback response in case of service failure
        return AIAnalysisResponse(
            urgency="Medium",
            is_sensitive=False,
            summary="Error in analysis, manual review required.",
            draft_reply=f"Thank you for your feedback. We're currently experiencing technical difficulties but will review your comment manually. Error: {str(e)}"
        )

async def process_comment_with_ai(comment_text: str) -> AnalyzedComment:
    """
    Legacy function for backward compatibility
    Process a customer comment using AI analysis (now powered by Bedrock)
    
    Args:
        comment_text: The customer comment to analyze
        
    Returns:
        AnalyzedComment model with AI insights
    """
    try:
        # Get AI analysis using legacy format
        ai_result = await get_ai_analysis(comment_text)
        
        # Create and return AnalyzedComment model
        analyzed_comment = AnalyzedComment(
            original_comment=comment_text,
            sentiment=ai_result.get("sentiment", "Neutral"),
            urgency_score=ai_result.get("urgency_score", 5),
            is_sensitive=ai_result.get("is_sensitive", False),
            suggested_reply=ai_result.get("suggested_reply", "Thank you for your feedback. We appreciate your input."),
            reasoning="Analysis powered by Amazon Bedrock Claude model"
        )
        
        return analyzed_comment
        
    except Exception as e:
        # Return a fallback response in case of AI service failure
        return AnalyzedComment(
            original_comment=comment_text,
            sentiment="Neutral",
            urgency_score=5,
            is_sensitive=False,
            suggested_reply=f"Thank you for your feedback. We're currently experiencing technical difficulties with our analysis service, but we'll review your comment manually and get back to you soon. Error: {str(e)}",
            reasoning="Fallback response due to service error"
        )

class TrustdeskService:
    """Service class for Trustdesk operations - now powered by Amazon Bedrock"""
    
    def __init__(self):
        # Initialize any database connections, etc.
        pass
    
    async def analyze_comment(self, comment_text: str) -> AnalyzedComment:
        """
        Legacy method: Analyze a customer comment using AI (Bedrock)
        
        Args:
            comment_text: The customer comment to analyze
            
        Returns:
            AnalyzedComment with AI insights
        """
        return await process_comment_with_ai(comment_text)
    
    async def analyze_comment_bedrock(self, comment_request: CommentRequest) -> AIAnalysisResponse:
        """
        New method: Analyze a comment using Bedrock directly
        
        Args:
            comment_request: CommentRequest containing the text to analyze
            
        Returns:
            AIAnalysisResponse with Bedrock analysis
        """
        return await analyze_comment(comment_request)
