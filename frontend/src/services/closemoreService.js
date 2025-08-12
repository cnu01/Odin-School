import api from './api';

/**
 * CloseMore API Service
 * Handles all API calls for conversation management and sales analysis
 */
class CloseMoreService {
  
  /**
   * Analyze a conversation using RAG-enhanced AI
   * @param {Object} conversationData - Conversation data to analyze
   * @returns {Promise} Analysis result
   */
  async analyzeConversation(conversationData) {
    try {
      const response = await api.post('/api/closemore/analyze-rag', {
        lead_id: conversationData.lead_id || conversationData.customerName || `lead_${Date.now()}`,
        channel: this.mapChannelType(conversationData.channel),
        conversation_text: conversationData.content || conversationData.conversation_text,
        rep_id: conversationData.rep_id || 'current_rep',
        use_rag: true,
        knowledge_categories: ['objection_handling', 'product_info', 'sales_strategies'],
        timestamp: new Date().toISOString(),
        lead_context: {
          stage: conversationData.stage,
          priority: conversationData.priority,
          previous_contacts: conversationData.conversationCount || 1
        }
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error analyzing conversation:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Get all conversations with filtering options
   * @param {Object} filters - Filter options (stage, priority, channel)
   * @returns {Promise} Conversations list
   */
  async getConversations(filters = {}) {
    try {
      // For now, we'll use mock data since the backend doesn't have a conversations list endpoint yet
      const response = await this.getMockConversations(filters);
      
      return {
        success: true,
        data: response
      };
    } catch (error) {
      console.error('Error fetching conversations:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Generate next best action for a conversation
   * @param {Object} conversationData - Conversation data
   * @returns {Promise} Next best action recommendation
   */
  async generateNextAction(conversationData) {
    try {
      // First analyze the conversation to get insights
      const analysisResult = await this.analyzeConversation(conversationData);
      
      if (analysisResult.success) {
        // Extract next steps from analysis
        const analysis = analysisResult.data;
        const nextAction = {
          action_type: this.mapToActionType(analysis.detected_intent),
          suggested_message: analysis.next_steps?.[0] || 'Follow up with lead',
          reason: analysis.summary,
          priority_score: Math.round(analysis.conversion_probability * 100),
          urgency_level: analysis.urgency_level,
          estimated_time_minutes: this.estimateActionTime(analysis.detected_intent),
          expected_outcome: this.getExpectedOutcome(analysis.detected_intent),
          personalization_notes: analysis.personalization_notes
        };
        
        return {
          success: true,
          data: nextAction
        };
      } else {
        throw new Error(analysisResult.error);
      }
    } catch (error) {
      console.error('Error generating next action:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Get conversations data from available endpoints
   * @returns {Promise} Array of conversation objects
   */
  async getConversations() {
    try {
      const [highPriorityResponse, pendingFollowUpsResponse] = await Promise.all([
        api.get('/api/closemore/high-priority-leads?rep_id=current_rep'),
        api.get('/api/closemore/pending-follow-ups?rep_id=current_rep')
      ]);
      
      const conversations = [];
      
      // Process high priority leads
      if (highPriorityResponse.data.leads) {
        conversations.push(...highPriorityResponse.data.leads.map(lead => ({
          id: lead.lead_id,
          customerName: lead.customer_name || lead.lead_id,
          customerAvatar: (lead.customer_name || lead.lead_id).split('_').map(n => n[0]).join('').toUpperCase(),
          channel: lead.channel || 'email',
          stage: lead.stage || 'discovery',
          priority: lead.priority || 'high',
          lastContact: lead.last_contact || 'Recently',
          winProbability: lead.win_probability || 75,
          sentiment: lead.sentiment || 'positive',
          aiSummary: lead.ai_summary || 'High priority lead requiring immediate attention',
          nextAction: lead.next_action || 'Follow up required',
          actionReason: lead.action_reason || 'High conversion potential',
          requiresAction: true,
          responseTime: Math.random() * 5 // Will be replaced with actual data
        })));
      }
      
      // Process pending follow-ups (different structure)
      if (pendingFollowUpsResponse.data.follow_ups) {
        conversations.push(...pendingFollowUpsResponse.data.follow_ups.map(followUp => ({
          id: followUp.lead_id,
          customerName: followUp.customer_name || followUp.lead_id,
          customerAvatar: (followUp.customer_name || followUp.lead_id).split('_').map(n => n[0]).join('').toUpperCase(),
          channel: followUp.channel || 'email',
          stage: followUp.stage || 'follow_up',
          priority: followUp.priority || 'medium',
          lastContact: followUp.last_contact || 'Recently',
          winProbability: followUp.win_probability || 50,
          sentiment: followUp.sentiment || 'neutral',
          aiSummary: followUp.ai_summary || 'Pending follow-up action required',
          nextAction: followUp.next_action || 'Send follow-up message',
          actionReason: followUp.action_reason || 'Maintaining engagement',
          requiresAction: false,
          responseTime: Math.random() * 5 // Will be replaced with actual data
        })));
      }
      
      // If no real data, add some mock conversations for demo
      if (conversations.length === 0) {
        return this.getMockConversations();
      }
      
      return conversations;
    } catch (error) {
      console.error('Error fetching conversations:', error);
      // Return fallback mock data
      return this.getMockConversations();
    }
  }

  /**
   * Get daily actions for a sales rep
   * @param {string} repId - Sales rep ID
   * @param {Object} options - Options for filtering actions
   * @returns {Promise} Daily actions summary
   */
  async getDailyActions(repId = 'current_rep', options = {}) {
    try {
      const response = await api.post('/api/closemore/daily-actions', {
        rep_id: repId,
        include_low_priority: options.includeLowPriority || false,
        max_actions: options.maxActions || 10,
        focus_area: options.focusArea
      });
      
      // Transform the API response to match frontend expectations
      const data = response.data;
      const dailyActions = [{
        rep: repId,
        avatar: repId.split('_').map(n => n[0]).join('').toUpperCase(),
        pendingActions: data.total_actions || 0,
        highPriority: data.high_priority_count || 0,
        completedToday: Math.floor(Math.random() * 10), // Mock for now
        winRate: Math.floor(Math.random() * 30 + 60), // Mock 60-90%
        avgResponseTime: `${(Math.random() * 3 + 1).toFixed(1)} hours`,
        actions: data.actions || []
      }];
      
      return dailyActions;
    } catch (error) {
      console.error('Error fetching daily actions:', error);
      // Return mock data as fallback
      return this.getMockDailyActions();
    }
  }

  /**
   * Get rep performance metrics
   * @param {string} repId - Sales rep ID
   * @returns {Promise} Performance metrics
   */
  async getRepMetrics(repId) {
    try {
      const response = await api.get(`/api/closemore/rep-metrics?rep_id=${repId}`);
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error fetching rep metrics:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Search sales knowledge base
   * @param {string} query - Search query
   * @param {Object} options - Search options
   * @returns {Promise} Search results
   */
  async searchKnowledge(query, options = {}) {
    try {
      const response = await api.post('/api/closemore/knowledge/search', {
        query: query,
        doc_types: options.docTypes,
        categories: options.categories,
        top_k: options.limit || 5,
        min_similarity: options.minSimilarity || 0.3
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error searching knowledge base:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Submit conversation feedback
   * @param {string} conversationId - Conversation ID
   * @param {Object} feedback - Feedback data
   * @returns {Promise} Submission result
   */
  async submitFeedback(conversationId, feedback) {
    try {
      // This would be the actual API call
      // For now, we'll simulate success
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      return {
        success: true,
        data: {
          message: 'Feedback submitted successfully',
          conversationId,
          feedback
        }
      };
    } catch (error) {
      console.error('Error submitting feedback:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  // Helper methods for data mapping and processing

  /**
   * Map frontend channel names to backend enum values
   */
  mapChannelType(channel) {
    const channelMap = {
      'WhatsApp': 'whatsapp',
      'Phone': 'call_transcript',
      'Email': 'email',
      'SMS': 'sms',
      'Chat': 'chat'
    };
    return channelMap[channel] || 'chat';
  }

  /**
   * Map detected intent to action type
   */
  mapToActionType(intent) {
    const actionMap = {
      'ready_to_book': 'book_meeting',
      'needs_more_info': 'send_resources',
      'price_sensitive': 'price_discussion',
      'comparing_options': 'competitor_comparison',
      'not_interested': 'send_follow_up',
      'scheduling_conflict': 'schedule_nudge',
      'technical_questions': 'send_demo',
      'job_support_concerns': 'send_resources'
    };
    return actionMap[intent] || 'send_follow_up';
  }

  /**
   * Estimate time required for different action types
   */
  estimateActionTime(intent) {
    const timeMap = {
      'ready_to_book': 15,
      'needs_more_info': 20,
      'price_sensitive': 25,
      'comparing_options': 30,
      'not_interested': 10,
      'scheduling_conflict': 15,
      'technical_questions': 35,
      'job_support_concerns': 25
    };
    return timeMap[intent] || 20;
  }

  /**
   * Get expected outcome for different intents
   */
  getExpectedOutcome(intent) {
    const outcomeMap = {
      'ready_to_book': 'Meeting scheduled within 24 hours',
      'needs_more_info': 'Lead engagement and education',
      'price_sensitive': 'Price objection addressed',
      'comparing_options': 'Competitive advantage established',
      'not_interested': 'Re-engagement or qualification',
      'scheduling_conflict': 'Alternative meeting time secured',
      'technical_questions': 'Technical concerns resolved',
      'job_support_concerns': 'Career support confidence built'
    };
    return outcomeMap[intent] || 'Continued engagement';
  }

  /**
   * Mock data for development (simulates real API responses)
   * This will be replaced with real API calls once backend conversation endpoints are ready
   */
  async getMockConversations(filters = {}) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    const mockConversations = [
      {
        id: 1,
        customerName: 'Rahul Sharma',
        customerAvatar: 'RS',
        lastContact: '2 hours ago',
        channel: 'WhatsApp',
        stage: 'discovery',
        priority: 'high',
        nextAction: 'Send pricing comparison with Data Science vs AI course',
        actionReason: 'Customer asked about ROI differences between programs',
        sentiment: 'positive',
        objections: ['pricing', 'time_commitment'],
        meetingScheduled: false,
        aiSummary: 'Interested in Data Science course. Concerned about time commitment due to current job. Needs pricing comparison.',
        winProbability: 75,
        lastActionDate: '2024-01-15',
        conversationCount: 4,
        analysis: {
          detected_intent: 'comparing_options',
          intent_confidence: 0.85,
          conversion_probability: 0.75,
          urgency_level: 'high',
          next_steps: ['Send pricing comparison', 'Schedule discovery call'],
          knowledge_used: [
            { title: 'Data Science vs AI Course Comparison', doc_type: 'product_info', relevance_score: 0.92 },
            { title: 'Time Management for Working Professionals', doc_type: 'objection_handling', relevance_score: 0.78 }
          ]
        }
      },
      {
        id: 2,
        customerName: 'Priya Patel',
        customerAvatar: 'PP',
        lastContact: '5 hours ago',
        channel: 'Phone',
        stage: 'proposal',
        priority: 'high',
        nextAction: 'Follow up on scholarship application status',
        actionReason: 'Customer submitted scholarship form, awaiting response',
        sentiment: 'neutral',
        objections: ['financial_constraints'],
        meetingScheduled: true,
        aiSummary: 'Applied for scholarship. High motivation but financial constraints. Follow-up needed on application.',
        winProbability: 65,
        lastActionDate: '2024-01-14',
        conversationCount: 6,
        analysis: {
          detected_intent: 'price_sensitive',
          intent_confidence: 0.90,
          conversion_probability: 0.65,
          urgency_level: 'high',
          next_steps: ['Check scholarship status', 'Discuss payment plans'],
          knowledge_used: [
            { title: 'Scholarship Program Guidelines', doc_type: 'process_info', relevance_score: 0.95 },
            { title: 'Financial Support Options', doc_type: 'sales_strategies', relevance_score: 0.82 }
          ]
        }
      },
      {
        id: 3,
        customerName: 'Amit Kumar',
        customerAvatar: 'AK',
        lastContact: '1 day ago',
        channel: 'Email',
        stage: 'negotiation',
        priority: 'medium',
        nextAction: 'Schedule final call to address placement concerns',
        actionReason: 'Customer has placement-related questions before finalizing enrollment',
        sentiment: 'cautious',
        objections: ['placement_guarantee', 'course_relevance'],
        meetingScheduled: false,
        aiSummary: 'Ready to enroll but needs placement assurance. Wants to speak with alumni.',
        winProbability: 80,
        lastActionDate: '2024-01-13',
        conversationCount: 8,
        analysis: {
          detected_intent: 'job_support_concerns',
          intent_confidence: 0.88,
          conversion_probability: 0.80,
          urgency_level: 'medium',
          next_steps: ['Connect with alumni', 'Share placement statistics', 'Schedule enrollment call'],
          knowledge_used: [
            { title: 'Placement Success Stories', doc_type: 'case_studies', relevance_score: 0.91 },
            { title: 'Alumni Network Benefits', doc_type: 'product_info', relevance_score: 0.85 }
          ]
        }
      },
      {
        id: 4,
        customerName: 'Sneha Singh',
        customerAvatar: 'SS',
        lastContact: '3 hours ago',
        channel: 'WhatsApp',
        stage: 'nurture',
        priority: 'low',
        nextAction: 'Send case study of successful career transition',
        actionReason: 'Customer expressed doubt about career change feasibility',
        sentiment: 'uncertain',
        objections: ['career_change_risk', 'age_concerns'],
        meetingScheduled: false,
        aiSummary: 'Interested but worried about career change at 35. Needs success stories from similar backgrounds.',
        winProbability: 40,
        lastActionDate: '2024-01-15',
        conversationCount: 2,
        analysis: {
          detected_intent: 'needs_more_info',
          intent_confidence: 0.75,
          conversion_probability: 0.40,
          urgency_level: 'low',
          next_steps: ['Share career transition stories', 'Provide age-diverse success examples', 'Offer consultation'],
          knowledge_used: [
            { title: 'Career Change Success at 35+', doc_type: 'case_studies', relevance_score: 0.93 },
            { title: 'Age Diversity in Tech', doc_type: 'market_insights', relevance_score: 0.79 }
          ]
        }
      }
    ];

    // Apply filters
    let filteredConversations = mockConversations;

    if (filters.stage && filters.stage !== 'all') {
      filteredConversations = filteredConversations.filter(c => c.stage === filters.stage);
    }
    if (filters.priority && filters.priority !== 'all') {
      filteredConversations = filteredConversations.filter(c => c.priority === filters.priority);
    }
    if (filters.channel && filters.channel !== 'all') {
      filteredConversations = filteredConversations.filter(c => c.channel === filters.channel);
    }

    return filteredConversations;
  }

  /**
   * Get mock daily actions data
   * @returns {Array} Mock daily actions
   */
  getMockDailyActions() {
    return [
      {
        rep: 'Ananya Gupta',
        avatar: 'AG',
        pendingActions: 12,
        highPriority: 5,
        completedToday: 8,
        winRate: 68,
        avgResponseTime: '2.3 hours',
      },
      {
        rep: 'Vikram Singh',
        avatar: 'VS',
        pendingActions: 9,
        highPriority: 3,
        completedToday: 11,
        winRate: 72,
        avgResponseTime: '1.8 hours',
      },
      {
        rep: 'Kavitha Rao',
        avatar: 'KR',
        pendingActions: 15,
        highPriority: 7,
        completedToday: 6,
        winRate: 65,
        avgResponseTime: '3.1 hours',
      },
    ];
  }
}

// Export singleton instance
export default new CloseMoreService();
