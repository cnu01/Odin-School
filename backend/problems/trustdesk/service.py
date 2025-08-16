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
        # Quick timeout for Bedrock to prevent long waits
        import asyncio
        
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
        
        # Wrap Bedrock call in timeout
        async def call_bedrock():
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
            
            return generated_text
        
        # Set 5-second timeout for Bedrock call
        try:
            generated_text = await asyncio.wait_for(call_bedrock(), timeout=5.0)
        except asyncio.TimeoutError:
            print("Bedrock call timed out, using fallback")
            raise Exception("Bedrock timeout")
        
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
        print(f"Bedrock analysis failed: {e}")
        raise Exception(f"Error calling Bedrock API: {str(e)}")

async def get_fallback_analysis(comment_text: str) -> dict:
    """
    Fallback analysis when Bedrock is not available
    Uses simple keyword-based analysis
    
    Args:
        comment_text: The customer comment to analyze
        
    Returns:
        Dictionary containing basic analysis results
    """
    comment_lower = comment_text.lower()
    
    # Simple sentiment analysis based on keywords
    positive_words = ['love', 'great', 'amazing', 'excellent', 'fantastic', 'awesome', 'good', 'best', 'recommend', 'thank', 'appreciate']
    negative_words = ['hate', 'terrible', 'awful', 'bad', 'worst', 'disappointed', 'frustrated', 'angry', 'refund', 'complaint']
    urgent_words = ['urgent', 'immediate', 'asap', 'emergency', 'help', 'problem', 'issue', 'error', 'broken', 'not working']
    question_words = ['how', 'what', 'when', 'where', 'why', 'can', 'should', 'would', 'could', '?']
    
    # Count occurrences
    positive_count = sum(1 for word in positive_words if word in comment_lower)
    negative_count = sum(1 for word in negative_words if word in comment_lower)
    urgent_count = sum(1 for word in urgent_words if word in comment_lower)
    question_count = sum(1 for word in question_words if word in comment_lower)
    
    # Determine sentiment
    if positive_count > negative_count:
        sentiment = "Positive"
        urgency_score = 2
        summary = f"Positive feedback expressing satisfaction with the service"
    elif negative_count > positive_count:
        sentiment = "Negative"
        urgency_score = 7
        summary = f"Negative feedback expressing dissatisfaction or concerns"
    else:
        sentiment = "Neutral"
        urgency_score = 5
        summary = f"Neutral comment requiring review"
    
    # Adjust for urgency
    if urgent_count > 0:
        urgency_score = max(urgency_score, 8)
        summary = f"Urgent issue requiring immediate attention"
    
    # Detect questions
    if question_count > 0 and urgent_count == 0:
        urgency_score = 5
        summary = f"Customer inquiry requiring informational response"
    
    # Generate appropriate response
    if sentiment == "Positive":
        suggested_reply = "Thank you so much for your wonderful feedback! We're thrilled to hear about your positive experience with our courses."
    elif sentiment == "Negative":
        suggested_reply = "Thank you for your feedback. We take all concerns seriously and would like to address this personally. Please contact our support team for immediate assistance."
    elif urgent_count > 0:
        suggested_reply = "We're sorry for the inconvenience! Our support team is looking into this issue. Please contact us directly for immediate assistance."
    else:
        suggested_reply = "Thank you for reaching out! Our team will review your message and get back to you shortly."
    
    return {
        "sentiment": sentiment,
        "urgency_score": urgency_score,
        "is_sensitive": negative_count > 2 or urgent_count > 1,
        "suggested_reply": suggested_reply,
        "summary": summary
    }

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
            "suggested_reply": bedrock_result.get("draft_reply", "Thank you for your feedback."),
            "summary": bedrock_result.get("summary", "Comment analysis completed")  # Add summary to legacy format
        }
        
        return legacy_result
        
    except Exception as e:
        # Fallback analysis without AWS dependencies
        print(f"Bedrock analysis failed: {e}")
        return await get_fallback_analysis(comment_text)

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
        # Get AI analysis (which includes fallback)
        ai_result = await get_ai_analysis(comment_text)
        
        # Create and return AnalyzedComment model with proper summary
        analyzed_comment = AnalyzedComment(
            original_comment=comment_text,
            sentiment=ai_result.get("sentiment", "Neutral"),
            urgency_score=ai_result.get("urgency_score", 5),
            is_sensitive=ai_result.get("is_sensitive", False),
            suggested_reply=ai_result.get("suggested_reply", "Thank you for your feedback. We appreciate your input."),
            reasoning=ai_result.get("summary", "Comment analysis completed")  # Use summary from analysis
        )
        
        return analyzed_comment
        
    except Exception as e:
        # Return a fallback response in case of complete service failure
        return AnalyzedComment(
            original_comment=comment_text,
            sentiment="Neutral",
            urgency_score=5,
            is_sensitive=False,
            suggested_reply="Thank you for your feedback. We're currently experiencing technical difficulties with our analysis service, but we'll review your comment manually and get back to you soon.",
            reasoning="Analysis service temporarily unavailable"
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
