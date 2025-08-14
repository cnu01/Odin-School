"""
Amazon Bedrock service for CloseMore sales conversation analysis
Provides AI-powered conversation analysis and action planning using Claude-v2
"""

import boto3
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
from .models import (
    ConversationInput, ConversationAnalysis, NextBestAction, 
    SentimentScore, ObjectionAnalysis, LeadIntent, ActionType, 
    UrgencyLevel, DailyActionsSummary
)

class ClosemoreBedrockService:
    """Amazon Bedrock service for sales conversation analysis and action planning"""
    
    def __init__(self):
        """Initialize Bedrock client and configuration"""
        try:
            # Check if we should use fallback mode
            use_fallback = os.getenv('USE_BEDROCK_FALLBACK', 'false').lower() == 'true'
            if use_fallback:
                print("Using Bedrock fallback mode - AI analysis will use local fallbacks")
                self.bedrock_client = None
            else:
                # Try to initialize with timeout
                self.bedrock_client = boto3.client(
                    'bedrock-runtime',
                    region_name=os.getenv('AWS_REGION', 'us-east-1'),
                    # Add timeout configuration
                    config=boto3.session.Config(
                        connect_timeout=5,  # 5 second connection timeout
                        read_timeout=10,    # 10 second read timeout
                        retries={'max_attempts': 0}  # No retries for faster failure
                    )
                )
                print("CloseMore Bedrock service initialized successfully")
            
            self.model_id = "anthropic.claude-v2"
            self.max_tokens = 2000
            
        except Exception as e:
            print(f"Warning: Bedrock client initialization failed: {e}")
            print("Falling back to local analysis mode")
            self.bedrock_client = None
    
    def _create_conversation_analysis_prompt(self, conversation: ConversationInput) -> str:
        """Create detailed prompt for conversation analysis"""
        
        current_time = datetime.now()
        
        prompt = f"""
You are an expert sales coach and conversation analyst for Odin School, a leading EdTech company specializing in professional tech courses.

COMPANY CONTEXT:
- Odin School offers career-focused technology courses (Data Science, Software Development, AI/ML, Digital Marketing)
- Target audience: Working professionals seeking career advancement
- Key value props: Industry-relevant curriculum, job placement support, flexible learning, expert mentors
- Price range: ₹50,000 - ₹2,50,000 depending on course and duration
- Success metrics: 85% job placement rate, 40% salary increase average

SALES PLAYBOOK CONTEXT:
- Primary goal: Book qualified demo calls and convert to enrollments
- Common objections: Price concerns, time constraints, course relevance, job guarantee skepticism
- Ideal customer: 2-5 years experience, motivated for career growth, ready to invest in upskilling
- Red flags: Unrealistic expectations, no time commitment, purely price-focused

CONVERSATION TO ANALYZE:
- Lead ID: {conversation.lead_id}
- Sales Rep: {conversation.rep_id}
- Channel: {conversation.channel}
- Timestamp: {conversation.timestamp or current_time}
- Content: "{conversation.conversation_text}"

ANALYSIS FRAMEWORK:
Analyze this conversation comprehensively and return ONLY a valid JSON response with these exact keys:

1. CONVERSATION SUMMARY
   - "summary": One-sentence overview of the conversation
   - "detailed_summary": 2-3 sentence detailed analysis of key discussion points

2. INTENT DETECTION
   - "detected_intent": Primary intent from: ["ready_to_book", "needs_more_info", "price_sensitive", "comparing_options", "not_interested", "scheduling_conflict", "technical_questions", "job_support_concerns"]
   - "intent_confidence": Confidence score 0.0-1.0

3. SENTIMENT ANALYSIS
   - "sentiment_analysis": {{
       "overall_sentiment": Score from -1.0 to 1.0 (-1=very negative, 0=neutral, 1=very positive),
       "confidence": Confidence in sentiment analysis 0.0-1.0,
       "emotional_indicators": List of detected emotions/feelings
     }}

4. OBJECTION ANALYSIS
   - "objections": List of objection objects, each with:
     {{
       "objection_text": "Exact objection raised",
       "objection_category": "price/time/relevance/support/quality/other",
       "severity": "high/medium/low",
       "suggested_response": "Recommended response strategy"
     }}

5. TOPIC ANALYSIS
   - "key_topics": List of main topics discussed (max 5)

6. ACTION PLANNING
   - "next_steps": List of immediate actions rep should take
   - "recommended_follow_up_time": Hours until next contact (number)
   - "conversion_probability": Likelihood of conversion 0.0-1.0
   - "urgency_level": "high/medium/low"
   - "personalization_notes": Key insights for personalizing future interactions

SCORING GUIDELINES:
- High urgency: Ready to decide, time-sensitive, high engagement
- Medium urgency: Interested but needs nurturing, minor objections
- Low urgency: Early stage, low engagement, major barriers

- High conversion probability (0.8+): Strong intent, minor objections, good fit
- Medium conversion probability (0.4-0.7): Some interest, manageable objections
- Low conversion probability (0.0-0.3): Major barriers, poor fit, low interest

Return ONLY the JSON object, no additional text or formatting.
"""
        return prompt
    
    def _create_daily_actions_prompt(self, rep_id: str, conversations_data: List[Dict], max_actions: int) -> str:
        """Create prompt for daily action planning"""
        
        conversations_summary = json.dumps(conversations_data, indent=2)
        
        prompt = f"""
You are a sales manager creating an optimized daily action plan for sales rep {rep_id} at Odin School.

BUSINESS OBJECTIVES:
- Increase meeting booking rate by 15%
- Reduce no-show rate by 20%
- Improve win rate by 10-20% within 45 days
- Maximize rep productivity and focus

RECENT CONVERSATION ANALYSES:
{conversations_summary}

ACTION PRIORITIZATION FRAMEWORK:
1. HIGH PRIORITY (80-100 points): Ready to convert, time-sensitive, high value
2. MEDIUM PRIORITY (50-79 points): Nurturing needed, manageable objections
3. LOW PRIORITY (0-49 points): Early stage, low probability, long-term nurturing

AVAILABLE ACTION TYPES:
- "send_follow_up": Personalized follow-up message
- "schedule_nudge": Reminder for upcoming meetings/deadlines
- "book_meeting": Direct attempt to schedule demo/consultation
- "price_discussion": Address pricing concerns specifically
- "competitor_comparison": Provide competitive analysis
- "send_demo": Share demo videos or trial access
- "send_resources": Educational content, case studies, testimonials
- "update_crm": Update lead status and notes
- "escalate_to_manager": Senior involvement needed

GENERATE DAILY ACTIONS:
Create a prioritized list of {max_actions} actions maximum. For each action, provide a JSON object with:

{{
  "lead_id": "Lead identifier",
  "action_type": "One of the available action types",
  "suggested_message": "Personalized, specific message or action to take",
  "reason": "Clear business justification for this action",
  "priority_score": "Number 0-100 based on conversion potential and urgency",
  "urgency_level": "high/medium/low",
  "estimated_time_minutes": "Realistic time estimate for completion",
  "expected_outcome": "Specific expected result",
  "follow_up_reminder": "ISO datetime for next reminder (if applicable)",
  "tags": ["action", "categorization", "tags"]
}}

PERSONALIZATION REQUIREMENTS:
- Reference specific conversation details
- Address individual objections and concerns  
- Use rep's historical success patterns
- Include specific next steps and timelines

Return ONLY a JSON array of action objects, no additional text.
"""
        return prompt
    
    async def analyze_conversation_with_bedrock(self, conversation: ConversationInput) -> ConversationAnalysis:
        """Analyze conversation using Amazon Bedrock Claude-v2"""
        
        if not self.bedrock_client:
            print("Bedrock client not available, using fallback analysis")
            return self._create_fallback_analysis(conversation)
        
        try:
            prompt = self._create_conversation_analysis_prompt(conversation)
            
            # Prepare request for Claude-v2
            request_body = {
                "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": self.max_tokens,
                "temperature": 0.1,
                "stop_sequences": ["\n\nHuman:"]
            }
            
            # Call Bedrock
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            ai_response = response_body.get('completion', '').strip()
            
            # Clean and parse JSON response
            ai_response = self._clean_json_response(ai_response)
            analysis_data = json.loads(ai_response)
            
            # Convert to structured response
            return self._convert_to_conversation_analysis(analysis_data, conversation.lead_id)
            
        except Exception as e:
            print(f"Bedrock analysis error: {e}")
            return self._create_fallback_analysis(conversation)
    
    async def generate_daily_actions_with_bedrock(
        self, 
        rep_id: str, 
        conversations_data: List[Dict], 
        max_actions: int = 10
    ) -> DailyActionsSummary:
        """Generate daily actions using Amazon Bedrock"""
        
        if not self.bedrock_client:
            print("Bedrock client not available, using fallback daily actions")
            return self._create_fallback_daily_actions(rep_id)
        
        try:
            prompt = self._create_daily_actions_prompt(rep_id, conversations_data, max_actions)
            
            request_body = {
                "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": self.max_tokens,
                "temperature": 0.2,
                "stop_sequences": ["\n\nHuman:"]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            ai_response = response_body.get('completion', '').strip()
            
            # Clean and parse JSON response
            ai_response = self._clean_json_response(ai_response)
            actions_data = json.loads(ai_response)
            
            # Convert to structured response
            actions = [self._convert_to_next_best_action(action) for action in actions_data]
            
            # Sort by priority score
            actions.sort(key=lambda x: x.priority_score, reverse=True)
            
            # Calculate summary metrics
            return DailyActionsSummary(
                total_actions=len(actions),
                high_priority_count=len([a for a in actions if a.urgency_level == UrgencyLevel.HIGH]),
                estimated_total_time=sum(a.estimated_time_minutes for a in actions),
                conversion_opportunities=len([a for a in actions if a.priority_score > 70]),
                actions=actions[:max_actions]
            )
            
        except Exception as e:
            print(f"Bedrock daily actions error: {e}")
            return self._create_fallback_daily_actions(rep_id)
    
    def _clean_json_response(self, response: str) -> str:
        """Clean AI response to extract valid JSON"""
        # Remove markdown code blocks
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*$', '', response)
        
        # Find JSON object/array boundaries
        if response.strip().startswith('['):
            # Array response
            start = response.find('[')
            end = response.rfind(']') + 1
        else:
            # Object response
            start = response.find('{')
            end = response.rfind('}') + 1
        
        if start != -1 and end != -1:
            return response[start:end].strip()
        
        return response.strip()
    
    def _convert_to_conversation_analysis(self, data: Dict, lead_id: str) -> ConversationAnalysis:
        """Convert AI response to ConversationAnalysis model"""
        
        # Process objections
        objections = []
        for obj_data in data.get('objections', []):
            if isinstance(obj_data, dict):
                objections.append(ObjectionAnalysis(
                    objection_text=obj_data.get('objection_text', ''),
                    objection_category=obj_data.get('objection_category', 'other'),
                    severity=UrgencyLevel(obj_data.get('severity', 'medium')),
                    suggested_response=obj_data.get('suggested_response', '')
                ))
            else:
                # Handle simple string objections
                objections.append(ObjectionAnalysis(
                    objection_text=str(obj_data),
                    objection_category='other',
                    severity=UrgencyLevel.MEDIUM,
                    suggested_response='Address this concern directly'
                ))
        
        # Process sentiment
        sentiment_data = data.get('sentiment_analysis', {})
        sentiment = SentimentScore(
            overall_sentiment=sentiment_data.get('overall_sentiment', 0.0),
            confidence=sentiment_data.get('confidence', 0.0),
            emotional_indicators=sentiment_data.get('emotional_indicators', [])
        )
        
        # Handle personalization_notes - ensure it's a string
        personalization_notes = data.get('personalization_notes', '')
        if isinstance(personalization_notes, list):
            personalization_notes = '; '.join(str(note) for note in personalization_notes)
        elif not isinstance(personalization_notes, str):
            personalization_notes = str(personalization_notes)
        
        return ConversationAnalysis(
            lead_id=lead_id,
            summary=data.get('summary', ''),
            detailed_summary=data.get('detailed_summary', ''),
            detected_intent=LeadIntent(data.get('detected_intent', 'needs_more_info')),
            intent_confidence=data.get('intent_confidence', 0.0),
            objections=objections,
            sentiment_analysis=sentiment,
            key_topics=data.get('key_topics', []),
            next_steps=data.get('next_steps', []),
            recommended_follow_up_time=data.get('recommended_follow_up_time', 24),
            conversion_probability=data.get('conversion_probability', 0.5),
            urgency_level=UrgencyLevel(data.get('urgency_level', 'medium')),
            personalization_notes=personalization_notes
        )
    
    def _convert_to_next_best_action(self, data: Dict) -> NextBestAction:
        """Convert AI response to NextBestAction model"""
        
        follow_up = None
        if data.get('follow_up_reminder'):
            try:
                follow_up = datetime.fromisoformat(data['follow_up_reminder'].replace('Z', '+00:00'))
            except:
                follow_up = datetime.now() + timedelta(hours=24)
        
        return NextBestAction(
            lead_id=data.get('lead_id', ''),
            action_type=ActionType(data.get('action_type', 'send_follow_up')),
            suggested_message=data.get('suggested_message', ''),
            reason=data.get('reason', ''),
            priority_score=data.get('priority_score', 50),
            urgency_level=UrgencyLevel(data.get('urgency_level', 'medium')),
            estimated_time_minutes=data.get('estimated_time_minutes', 15),
            expected_outcome=data.get('expected_outcome', ''),
            follow_up_reminder=follow_up,
            tags=data.get('tags', [])
        )
    
    def _create_fallback_analysis(self, conversation: ConversationInput) -> ConversationAnalysis:
        """Create fallback analysis when Bedrock is unavailable"""
        
        # Simple keyword-based analysis as fallback
        text = conversation.conversation_text.lower()
        
        # Detect intent based on keywords
        if any(word in text for word in ['book', 'schedule', 'demo', 'meeting', 'ready']):
            intent = LeadIntent.READY_TO_BOOK
            conversion_prob = 0.8
        elif any(word in text for word in ['price', 'cost', 'expensive', 'cheap']):
            intent = LeadIntent.PRICE_SENSITIVE
            conversion_prob = 0.6
        elif any(word in text for word in ['compare', 'competition', 'other']):
            intent = LeadIntent.COMPARING_OPTIONS
            conversion_prob = 0.5
        else:
            intent = LeadIntent.NEEDS_MORE_INFO
            conversion_prob = 0.4
        
        return ConversationAnalysis(
            lead_id=conversation.lead_id,
            summary="Conversation analysis performed with fallback system",
            detailed_summary="Detailed analysis unavailable - using keyword-based detection",
            detected_intent=intent,
            intent_confidence=0.6,
            objections=[],
            sentiment_analysis=SentimentScore(
                overall_sentiment=0.0,
                confidence=0.5,
                emotional_indicators=[]
            ),
            key_topics=[],
            next_steps=["Follow up within 24 hours", "Address any concerns raised"],
            recommended_follow_up_time=24,
            conversion_probability=conversion_prob,
            urgency_level=UrgencyLevel.MEDIUM,
            personalization_notes="Manual review recommended for detailed analysis"
        )
    
    def _create_fallback_daily_actions(self, rep_id: str) -> DailyActionsSummary:
        """Create fallback daily actions when Bedrock is unavailable"""
        
        actions = [
            NextBestAction(
                lead_id=f"lead_{rep_id}_001",
                action_type=ActionType.SEND_FOLLOW_UP,
                suggested_message="Follow up on recent conversation",
                reason="Maintain engagement with prospects",
                priority_score=75,
                urgency_level=UrgencyLevel.MEDIUM,
                estimated_time_minutes=15,
                expected_outcome="Continued engagement",
                follow_up_reminder=datetime.now() + timedelta(hours=24),
                tags=["fallback", "general"]
            )
        ]
        
        return DailyActionsSummary(
            total_actions=1,
            high_priority_count=0,
            estimated_total_time=15,
            conversion_opportunities=0,
            actions=actions
        )
