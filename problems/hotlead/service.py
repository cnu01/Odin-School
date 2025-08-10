import httpx
import os
import json
from dotenv import load_dotenv
from .models import LeadInput, ScoredLead

# Load environment variables
load_dotenv()

async def get_lead_analysis_from_ai(lead_input: LeadInput) -> dict:
    """
    Call external AI service for lead analysis and scoring
    
    Args:
        lead_input: LeadInput object containing lead data
        
    Returns:
        Dictionary containing AI analysis results
    """
    api_key = os.getenv("AI_API_KEY")
    
    if not api_key:
        raise ValueError("AI_API_KEY not found in environment variables")
    
    # Convert lead input data to a string for the prompt
    lead_data_str = json.dumps(lead_input.model_dump(), indent=2)
    
    # Construct detailed, multi-part prompt for LLM
    prompt = f"""
You are an expert sales analyst for Odin School, an EdTech company. Your task is to analyze a new lead and return a JSON object with a priority score and routing action.

**Contextual Rules:**
- Lead-to-paid conversion varies 3-5x by source. Treat leads from sources containing 'Campaign', 'LinkedIn', or 'Referral' as high-value. [cite: 18]
- Leads with high pageviews (e.g., more than 5) show strong interest.
- The goal is to contact high-priority leads in under 5 minutes. [cite: 27]

**Lead Data to Analyze:**
{lead_data_str}

**Your Task:**
Based on all the information, return ONLY a valid JSON object with three keys:
1. "score": An integer from 0 to 100.
2. "reason": A short, one-sentence explanation for the score. [cite: 25]
3. "priority_routing_action": A string with one of these exact values: "Immediate: Route to Tier 1 Sales", "Priority: Add to 1-hour callback queue", or "Standard: Add to general queue".
"""
    
    # API request payload for OpenAI
    payload = {
        "model": "gpt-3.5-turbo",
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
            # Make API call to OpenAI
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            ai_response = response.json()
            
            # Extract the content from AI response
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

async def score_lead_with_ai(lead_input: LeadInput) -> ScoredLead:
    """
    Score a lead using AI analysis
    
    Args:
        lead_input: LeadInput object containing lead data
        
    Returns:
        ScoredLead with AI-generated score and routing action
    """
    try:
        # Get AI analysis
        ai_result = await get_lead_analysis_from_ai(lead_input)
        
        # Extract priority and routing_action from the combined field
        priority_routing = ai_result.get("priority_routing_action", "Standard: Add to general queue")
        
        # Parse priority and routing action
        if "Immediate" in priority_routing:
            priority = "urgent"
            routing_action = "immediate_followup"
        elif "Priority" in priority_routing:
            priority = "high"
            routing_action = "priority_queue"
        else:
            priority = "medium"
            routing_action = "sales_qualified"
        
        # Create and return ScoredLead model with new structure
        scored_lead = ScoredLead(
            lead_input=lead_input,
            score=ai_result.get("score", 50),  # Default to medium score
            reason=ai_result.get("reason", "Lead analyzed based on available data."),
            priority=priority,
            routing_action=routing_action
        )
        
        return scored_lead
        
    except Exception as e:
        # Return a fallback response in case of AI service failure
        fallback_score = 30  # Conservative default score
        fallback_reason = f"Fallback scoring due to service issue: {str(e)}"
        
        return ScoredLead(
            lead_input=lead_input,
            score=fallback_score,
            reason=fallback_reason,
            priority="low",
            routing_action="nurture_campaign"
        )

class HotLeadService:
    """Service class for HotLead operations - implement your business logic here"""
    
    def __init__(self):
        # Initialize any database connections, etc.
        pass
    
    async def score_lead(self, lead_input: LeadInput) -> ScoredLead:
        """
        Score a lead using AI analysis
        
        Args:
            lead_input: LeadInput containing lead data
            
        Returns:
            ScoredLead with AI analysis and routing recommendation
        """
        return await score_lead_with_ai(lead_input)
