"""
Conversation Manager for CloseMore
Handles storage and retrieval of conversation data and analysis results
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from .models import (
    ConversationInput, ConversationAnalysis, NextBestAction,
    UrgencyLevel, LeadIntent, ActionType
)

@dataclass
class ConversationRecord:
    """Internal record for conversation storage"""
    conversation_id: str
    lead_id: str
    rep_id: str
    channel: str
    conversation_text: str
    analysis: Dict[str, Any]
    timestamp: datetime
    updated_at: datetime

class ConversationManager:
    """Manages conversation storage and retrieval for CloseMore"""
    
    def __init__(self, storage_path: str = "data/closemore"):
        """Initialize conversation manager with storage configuration"""
        self.storage_path = storage_path
        self.conversations_file = os.path.join(storage_path, "conversations.json")
        self.analytics_file = os.path.join(storage_path, "analytics.json")
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize storage files
        self._initialize_storage()
        
        print(f"ConversationManager initialized with storage at: {storage_path}")
    
    def _initialize_storage(self):
        """Initialize storage files if they don't exist"""
        if not os.path.exists(self.conversations_file):
            with open(self.conversations_file, 'w') as f:
                json.dump([], f)
        
        if not os.path.exists(self.analytics_file):
            with open(self.analytics_file, 'w') as f:
                json.dump({}, f)
    
    def store_conversation_analysis(
        self, 
        conversation: ConversationInput, 
        analysis: ConversationAnalysis
    ) -> str:
        """Store conversation and its analysis"""
        
        conversation_id = f"{conversation.lead_id}_{int(datetime.now().timestamp())}"
        
        # Create conversation record
        record = ConversationRecord(
            conversation_id=conversation_id,
            lead_id=conversation.lead_id,
            rep_id=conversation.rep_id,
            channel=conversation.channel.value,
            conversation_text=conversation.conversation_text,
            analysis=self._analysis_to_dict(analysis),
            timestamp=conversation.timestamp or datetime.now(),
            updated_at=datetime.now()
        )
        
        # Load existing conversations
        conversations = self._load_conversations()
        
        # Add new conversation
        conversations.append(asdict(record))
        
        # Save updated conversations
        self._save_conversations(conversations)
        
        # Update analytics
        self._update_analytics(conversation.rep_id, analysis)
        
        return conversation_id
    
    def get_conversations_for_rep(
        self, 
        rep_id: str, 
        days_back: int = 7,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get recent conversations for a sales rep"""
        
        conversations = self._load_conversations()
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Filter by rep and date
        filtered = [
            conv for conv in conversations 
            if (conv['rep_id'] == rep_id and 
                datetime.fromisoformat(conv['timestamp']) > cutoff_date)
        ]
        
        # Sort by timestamp (most recent first)
        filtered.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Apply limit if specified
        if limit:
            filtered = filtered[:limit]
        
        return filtered
    
    def get_high_priority_leads(self, rep_id: str) -> List[Dict[str, Any]]:
        """Get high priority leads for a sales rep"""
        
        conversations = self.get_conversations_for_rep(rep_id, days_back=3)
        
        high_priority = []
        for conv in conversations:
            analysis = conv['analysis']
            if (analysis.get('urgency_level') == 'high' or 
                analysis.get('conversion_probability', 0) > 0.7):
                high_priority.append({
                    'lead_id': conv['lead_id'],
                    'last_contact': conv['timestamp'],
                    'channel': conv['channel'],
                    'urgency_level': analysis.get('urgency_level'),
                    'conversion_probability': analysis.get('conversion_probability'),
                    'summary': analysis.get('summary'),
                    'next_steps': analysis.get('next_steps', [])
                })
        
        return high_priority
    
    def get_lead_history(self, lead_id: str) -> List[Dict[str, Any]]:
        """Get complete conversation history for a specific lead"""
        
        conversations = self._load_conversations()
        
        lead_conversations = [
            conv for conv in conversations 
            if conv['lead_id'] == lead_id
        ]
        
        # Sort chronologically
        lead_conversations.sort(key=lambda x: x['timestamp'])
        
        return lead_conversations
    
    def get_rep_analytics(self, rep_id: str) -> Dict[str, Any]:
        """Get analytics for a sales rep"""
        
        analytics = self._load_analytics()
        rep_analytics = analytics.get(rep_id, {})
        
        # If no stored analytics, calculate from conversations
        if not rep_analytics:
            rep_analytics = self._calculate_rep_analytics(rep_id)
            
            # Store calculated analytics
            analytics[rep_id] = rep_analytics
            self._save_analytics(analytics)
        
        return rep_analytics
    
    def get_pending_follow_ups(self, rep_id: str) -> List[Dict[str, Any]]:
        """Get leads that need follow-up based on recommended timing"""
        
        conversations = self.get_conversations_for_rep(rep_id, days_back=14)
        current_time = datetime.now()
        
        pending_follow_ups = []
        
        for conv in conversations:
            analysis = conv['analysis']
            follow_up_hours = analysis.get('recommended_follow_up_time', 24)
            last_contact = datetime.fromisoformat(conv['timestamp'])
            
            # Check if follow-up is due
            follow_up_due = last_contact + timedelta(hours=follow_up_hours)
            
            if current_time >= follow_up_due:
                pending_follow_ups.append({
                    'lead_id': conv['lead_id'],
                    'last_contact': conv['timestamp'],
                    'hours_overdue': int((current_time - follow_up_due).total_seconds() / 3600),
                    'urgency_level': analysis.get('urgency_level'),
                    'summary': analysis.get('summary'),
                    'personalization_notes': analysis.get('personalization_notes')
                })
        
        # Sort by hours overdue (most overdue first)
        pending_follow_ups.sort(key=lambda x: x['hours_overdue'], reverse=True)
        
        return pending_follow_ups
    
    def _analysis_to_dict(self, analysis: ConversationAnalysis) -> Dict[str, Any]:
        """Convert ConversationAnalysis to dictionary for storage"""
        
        # Convert to dict and handle nested models
        data = analysis.dict()
        
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        
        return data
    
    def _load_conversations(self) -> List[Dict[str, Any]]:
        """Load conversations from storage"""
        try:
            with open(self.conversations_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_conversations(self, conversations: List[Dict[str, Any]]):
        """Save conversations to storage"""
        with open(self.conversations_file, 'w') as f:
            json.dump(conversations, f, default=str, indent=2)
    
    def _load_analytics(self) -> Dict[str, Any]:
        """Load analytics from storage"""
        try:
            with open(self.analytics_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_analytics(self, analytics: Dict[str, Any]):
        """Save analytics to storage"""
        with open(self.analytics_file, 'w') as f:
            json.dump(analytics, f, default=str, indent=2)
    
    def _update_analytics(self, rep_id: str, analysis: ConversationAnalysis):
        """Update analytics for a rep based on new analysis"""
        
        analytics = self._load_analytics()
        
        if rep_id not in analytics:
            analytics[rep_id] = {
                'total_conversations': 0,
                'intent_distribution': {},
                'urgency_distribution': {},
                'avg_conversion_probability': 0,
                'avg_sentiment': 0,
                'last_updated': datetime.now().isoformat()
            }
        
        rep_data = analytics[rep_id]
        
        # Update conversation count
        rep_data['total_conversations'] += 1
        
        # Update intent distribution
        intent = analysis.detected_intent.value
        rep_data['intent_distribution'][intent] = rep_data['intent_distribution'].get(intent, 0) + 1
        
        # Update urgency distribution
        urgency = analysis.urgency_level.value
        rep_data['urgency_distribution'][urgency] = rep_data['urgency_distribution'].get(urgency, 0) + 1
        
        # Update running averages
        total = rep_data['total_conversations']
        old_avg_conv = rep_data['avg_conversion_probability']
        old_avg_sent = rep_data['avg_sentiment']
        
        rep_data['avg_conversion_probability'] = (
            (old_avg_conv * (total - 1) + analysis.conversion_probability) / total
        )
        
        rep_data['avg_sentiment'] = (
            (old_avg_sent * (total - 1) + analysis.sentiment_analysis.overall_sentiment) / total
        )
        
        rep_data['last_updated'] = datetime.now().isoformat()
        
        # Save updated analytics
        analytics[rep_id] = rep_data
        self._save_analytics(analytics)
    
    def _calculate_rep_analytics(self, rep_id: str) -> Dict[str, Any]:
        """Calculate analytics for a rep from conversation history"""
        
        conversations = self.get_conversations_for_rep(rep_id, days_back=30)
        
        if not conversations:
            return {
                'total_conversations': 0,
                'intent_distribution': {},
                'urgency_distribution': {},
                'avg_conversion_probability': 0,
                'avg_sentiment': 0,
                'last_updated': datetime.now().isoformat()
            }
        
        # Calculate distributions and averages
        intent_dist = {}
        urgency_dist = {}
        total_conv_prob = 0
        total_sentiment = 0
        
        for conv in conversations:
            analysis = conv['analysis']
            
            # Intent distribution
            intent = analysis.get('detected_intent', 'needs_more_info')
            intent_dist[intent] = intent_dist.get(intent, 0) + 1
            
            # Urgency distribution
            urgency = analysis.get('urgency_level', 'medium')
            urgency_dist[urgency] = urgency_dist.get(urgency, 0) + 1
            
            # Running totals
            total_conv_prob += analysis.get('conversion_probability', 0)
            total_sentiment += analysis.get('sentiment_analysis', {}).get('overall_sentiment', 0)
        
        total_conversations = len(conversations)
        
        return {
            'total_conversations': total_conversations,
            'intent_distribution': intent_dist,
            'urgency_distribution': urgency_dist,
            'avg_conversion_probability': total_conv_prob / total_conversations,
            'avg_sentiment': total_sentiment / total_conversations,
            'last_updated': datetime.now().isoformat()
        }

# Mock data generator for development and testing
class MockDataGenerator:
    """Generate mock conversation data for development and testing"""
    
    @staticmethod
    def generate_sample_conversations(rep_id: str, count: int = 10) -> List[ConversationInput]:
        """Generate sample conversations for testing"""
        
        sample_conversations = [
            {
                "channel": "call_transcript",
                "text": "Hi, I'm interested in your Data Science course. I'm currently working as a business analyst and want to transition to data science. Can you tell me more about the curriculum and job placement support?"
            },
            {
                "channel": "whatsapp", 
                "text": "Hello! I saw your ad about the AI/ML course. The price seems quite high at ₹1.5 lakhs. Do you have any payment plans or discounts available? Also, how long is the course duration?"
            },
            {
                "channel": "email",
                "text": "Thanks for the demo yesterday. I'm very impressed with the curriculum but I'm comparing with two other institutes. Can you share some success stories or placement statistics to help me decide?"
            },
            {
                "channel": "call_transcript",
                "text": "I missed our scheduled call yesterday, sorry about that. I had an urgent meeting. I'm still very interested in the course. Can we reschedule? I'm free this Friday afternoon."
            },
            {
                "channel": "whatsapp",
                "text": "I've been thinking about what we discussed. I'm ready to enroll but I have some concerns about the job guarantee. What exactly does it cover? Do you help with interview preparation as well?"
            }
        ]
        
        conversations = []
        for i, sample in enumerate(sample_conversations):
            conversations.append(ConversationInput(
                lead_id=f"lead_{rep_id}_{i+1:03d}",
                channel=sample["channel"],
                conversation_text=sample["text"],
                rep_id=rep_id,
                timestamp=datetime.now() - timedelta(hours=i*6),
                lead_context={"source": "mock_data", "stage": "initial_interest"}
            ))
        
        return conversations[:count]
