import httpx
import os
import json
from dotenv import load_dotenv
from .models import AnalyzedComment

# Load environment variables
load_dotenv()

async def get_ai_analysis(comment_text: str) -> dict:
    """
    Call external AI service for comment analysis
    
    Args:
        comment_text: The customer comment to analyze
        
    Returns:
        Dictionary containing AI analysis results
    """
    api_key = os.getenv("AI_API_KEY")
    
    if not api_key:
        raise ValueError("AI_API_KEY not found in environment variables")
    
    # Construct detailed prompt for structured response
    prompt = f"""Analyze the following customer comment and return a JSON object with four keys: 
'sentiment' (string: "Positive", "Negative", "Neutral", or "Question"), 
'urgency_score' (integer: 0-10), 
'is_sensitive' (boolean), 
and 'suggested_reply' (a string drafted in a helpful and empathetic brand voice).

Comment: "{comment_text}"

Please respond only with valid JSON format."""

    # API request payload
    payload = {
        "model": "gpt-3.5-turbo",  # Adjust based on your AI provider
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # OpenAI API endpoint
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            ai_response = response.json()
            
            # Extract the content from AI response
            # Adjust parsing based on your AI provider's response format
            content = ai_response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            
            # Parse the JSON response from AI
            analysis_result = json.loads(content)
            
            return analysis_result
            
        except httpx.RequestError as e:
            raise Exception(f"Error calling AI API: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Error parsing AI response: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error in AI analysis: {str(e)}")

async def process_comment_with_ai(comment_text: str) -> AnalyzedComment:
    """
    Process a customer comment using AI analysis
    
    Args:
        comment_text: The customer comment to analyze
        
    Returns:
        AnalyzedComment model with AI insights
    """
    try:
        # Get AI analysis
        ai_result = await get_ai_analysis(comment_text)
        
        # Create and return AnalyzedComment model
        analyzed_comment = AnalyzedComment(
            original_comment=comment_text,
            sentiment=ai_result.get("sentiment", "Neutral"),
            urgency_score=ai_result.get("urgency_score", 5),
            is_sensitive=ai_result.get("is_sensitive", False),
            suggested_reply=ai_result.get("suggested_reply", "Thank you for your feedback. We appreciate your input.")
        )
        
        return analyzed_comment
        
    except Exception as e:
        # Return a fallback response in case of AI service failure
        return AnalyzedComment(
            original_comment=comment_text,
            sentiment="Neutral",
            urgency_score=5,
            is_sensitive=False,
            suggested_reply=f"Thank you for your feedback. We're currently experiencing technical difficulties with our analysis service, but we'll review your comment manually and get back to you soon. Error: {str(e)}"
        )

class TrustdeskService:
    """Service class for Trustdesk operations"""
    
    def __init__(self):
        # Initialize any database connections, etc.
        pass
    
    async def analyze_comment(self, comment_text: str) -> AnalyzedComment:
        """
        Analyze a customer comment using AI
        
        Args:
            comment_text: The customer comment to analyze
            
        Returns:
            AnalyzedComment with AI insights
        """
        return await process_comment_with_ai(comment_text)
