import api from './api';

/**
 * TrustDesk API Service
 * Handles all API calls for brand reputation and comment management
 */
class TrustDeskService {
  
  /**
   * Analyze a comment using AI
   * @param {Object} commentData - Comment data to analyze
   * @returns {Promise} Analysis result
   */
  async analyzeComment(commentData) {
    try {
      // Use shorter timeout for comment analysis to prevent long waits
      const response = await api.post('/api/trustdesk/analyze', {
        comment_text: commentData.content,
        customer_name: commentData.author || 'Anonymous',
        platform: commentData.platform || 'manual_input',
        comment_type: 'general'
      }, {
        timeout: 8000 // 8 second timeout for comment analysis
      });
      
      // Transform the response to match frontend expectations
      const data = response.data;
      return {
        success: true,
        data: {
          sentiment: data.sentiment,
          category: this._categorizeFromSentiment(data.sentiment, data.urgency_score),
          priority: this._mapUrgencyToPriority(data.urgency_score),
          confidence: 0.85, // Default confidence since legacy endpoint doesn't provide it
          summary: data.reasoning || 'Comment analyzed successfully',
          suggested_response: data.suggested_reply
        }
      };
    } catch (error) {
      console.error('Error analyzing comment:', error);
      
      // If it's a timeout error, provide immediate local analysis
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        return this._getLocalAnalysis(commentData.content);
      }
      
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Provide immediate local analysis when API times out
   * @param {string} commentText - Comment text to analyze
   * @returns {Object} Local analysis result
   */
  _getLocalAnalysis(commentText) {
    const text = commentText.toLowerCase();
    
    // Simple keyword-based analysis
    const positiveWords = ['love', 'great', 'amazing', 'excellent', 'fantastic', 'awesome', 'good', 'best', 'recommend', 'thank'];
    const negativeWords = ['hate', 'terrible', 'awful', 'bad', 'worst', 'disappointed', 'frustrated', 'angry', 'refund'];
    const urgentWords = ['urgent', 'immediate', 'help', 'problem', 'issue', 'error', 'broken', 'not working'];
    const questionWords = ['how', 'what', 'when', 'where', 'why', 'can', 'should', 'would', '?'];
    
    const positiveCount = positiveWords.filter(word => text.includes(word)).length;
    const negativeCount = negativeWords.filter(word => text.includes(word)).length;
    const urgentCount = urgentWords.filter(word => text.includes(word)).length;
    const questionCount = questionWords.filter(word => text.includes(word)).length;
    
    let sentiment, category, priority, summary;
    
    if (positiveCount > negativeCount) {
      sentiment = 'positive';
      category = 'positive';
      priority = 'low';
      summary = 'Positive feedback expressing satisfaction';
    } else if (negativeCount > positiveCount) {
      sentiment = 'negative';
      category = 'negative';
      priority = 'high';
      summary = 'Negative feedback expressing concerns';
    } else {
      sentiment = 'neutral';
      category = 'question';
      priority = 'medium';
      summary = 'Neutral comment requiring review';
    }
    
    if (urgentCount > 0) {
      priority = 'urgent';
      category = 'urgent';
      summary = 'Urgent issue requiring immediate attention';
    } else if (questionCount > 0 && urgentCount === 0) {
      category = 'question';
      summary = 'Customer inquiry requiring response';
    }
    
    return {
      success: true,
      data: {
        sentiment,
        category,
        priority,
        confidence: 0.65, // Lower confidence for local analysis
        summary,
        suggested_response: this._getQuickResponse(category)
      }
    };
  }

  /**
   * Get quick response template based on category
   * @param {string} category - Comment category
   * @returns {string} Quick response template
   */
  _getQuickResponse(category) {
    const responses = {
      positive: "Thank you so much for your wonderful feedback! We're thrilled to hear about your positive experience.",
      negative: "Thank you for your feedback. We take all concerns seriously and would like to address this personally. Please contact our support team.",
      urgent: "We're sorry for the inconvenience! Our support team is looking into this issue. Please contact us directly for immediate assistance.",
      question: "Thank you for reaching out! Our team will review your question and get back to you shortly."
    };
    
    return responses[category] || responses.question;
  }

  /**
   * Helper method to categorize based on sentiment and urgency
   */
  _categorizeFromSentiment(sentiment, urgencyScore) {
    if (urgencyScore >= 8) return 'urgent';
    if (sentiment === 'negative') return 'negative';
    if (sentiment === 'positive') return 'positive';
    return 'question';
  }

  /**
   * Helper method to map urgency score to priority
   */
  _mapUrgencyToPriority(urgencyScore) {
    if (urgencyScore >= 8) return 'urgent';
    if (urgencyScore >= 5) return 'medium';
    return 'low';
  }

  /**
   * Get all comments with filtering options
   * @param {Object} filters - Filter options (platform, priority, sentiment)
   * @returns {Promise} Comments list
   */
  async getComments(filters = {}) {
    try {
      const params = new URLSearchParams();
      
      if (filters.platform && filters.platform !== 'all') {
        params.append('platform', filters.platform);
      }
      if (filters.priority && filters.priority !== 'all') {
        params.append('priority', filters.priority);
      }
      if (filters.sentiment && filters.sentiment !== 'all') {
        params.append('sentiment', filters.sentiment);
      }
      if (filters.status && filters.status !== 'all') {
        params.append('status', filters.status);
      }
      
      // For now, we'll use mock data since the backend doesn't have a comments endpoint yet
      // This simulates the API call structure
      const response = await this.getMockComments(filters);
      
      return {
        success: true,
        data: response
      };
    } catch (error) {
      console.error('Error fetching comments:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Generate AI response for a comment
   * @param {string} commentText - Original comment text
   * @param {string} category - Comment category (positive, negative, question, urgent)
   * @returns {Promise} Generated response
   */
  async generateResponse(commentText, category) {
    try {
      const response = await api.post('/api/trustdesk/analyze-rag', {
        text: commentText,
        use_rag: true,
        include_context: true
      });
      
      return {
        success: true,
        data: {
          draft_reply: response.data.draft_reply,
          confidence_score: response.data.confidence_score,
          knowledge_sources: response.data.knowledge_sources
        }
      };
    } catch (error) {
      console.error('Error generating response:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Submit response to a comment
   * @param {string} commentId - Comment ID
   * @param {string} response - Response text
   * @returns {Promise} Submission result
   */
  async submitResponse(commentId, response) {
    try {
      // This would be the actual API call
      // For now, we'll simulate success
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      return {
        success: true,
        data: {
          message: 'Response submitted successfully',
          commentId,
          response
        }
      };
    } catch (error) {
      console.error('Error submitting response:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Submit feedback on a response
   * @param {string} commentText - Original comment
   * @param {string} reply - Reply that was used
   * @param {number} rating - Effectiveness rating (1-5)
   * @returns {Promise} Feedback submission result
   */
  async submitFeedback(commentText, reply, rating) {
    try {
      const response = await api.post('/api/trustdesk/feedback', {
        comment: commentText,
        reply: reply,
        rating: rating
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error submitting feedback:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Search knowledge base
   * @param {string} query - Search query
   * @param {Object} options - Search options
   * @returns {Promise} Search results
   */
  async searchKnowledge(query, options = {}) {
    try {
      const response = await api.post('/api/trustdesk/search', {
        query: query,
        category: options.category,
        top_k: options.limit || 5
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
   * Get knowledge base statistics
   * @returns {Promise} Statistics data
   */
  async getKnowledgeStats() {
    try {
      const response = await api.get('/api/trustdesk/stats');
      
      return {
        success: true,
        data: response.data.knowledge_base_stats
      };
    } catch (error) {
      console.error('Error fetching knowledge stats:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Mock data for development (simulates real API responses)
   * This will be replaced with real API calls once backend is ready
   */
  async getMockComments(filters = {}) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    const mockComments = [
      {
        id: 1,
        platform: 'YouTube',
        author: 'TechLearner2024',
        avatar: 'TL',
        content: 'Just completed the Data Science course from APEX AI. Amazing experience! The instructors are top-notch and the projects are industry-relevant. Highly recommend!',
        timestamp: '2 hours ago',
        sentiment: 'positive',
        priority: 'low',
        category: 'positive',
        replies: 12,
        likes: 45,
        status: 'new',
        videoTitle: 'Data Science Career Guide 2024',
        analysis: {
          urgency: 'Low',
          is_sensitive: false,
          summary: 'Positive review praising course quality and relevance.',
          confidence_score: 0.95
        }
      },
      {
        id: 2,
        platform: 'Instagram',
        author: 'career_switcher_raj',
        avatar: 'CR',
        content: 'Is the Full Stack course worth it? I\'m from a non-tech background and wondering if 6 months is enough to land a job. Anyone here switched careers successfully?',
        timestamp: '4 hours ago',
        sentiment: 'neutral',
        priority: 'high',
        category: 'question',
        replies: 0,
        likes: 8,
        status: 'new',
        postTitle: 'Career Change Success Stories',
        analysis: {
          urgency: 'Medium',
          is_sensitive: false,
          summary: 'Career switcher asking about course effectiveness and job prospects.',
          confidence_score: 0.88
        }
      },
      {
        id: 3,
        platform: 'YouTube',
        author: 'SkepticalCoder',
        avatar: 'SC',
        content: 'The course content seems outdated. React 18 features are missing and the deployment section doesn\'t cover modern practices. Expected better for the price.',
        timestamp: '6 hours ago',
        sentiment: 'negative',
        priority: 'urgent',
        category: 'negative',
        replies: 0,
        likes: 23,
        status: 'new',
        videoTitle: 'React.js Complete Course',
        analysis: {
          urgency: 'High',
          is_sensitive: true,
          summary: 'Negative feedback about outdated course content and missing modern features.',
          confidence_score: 0.92
        }
      },
      {
        id: 4,
        platform: 'Facebook',
        author: 'Priya Sharma',
        avatar: 'PS',
        content: 'Can someone help me with the payment process? I\'m trying to enroll but the payment page is not loading properly.',
        timestamp: '8 hours ago',
        sentiment: 'neutral',
        priority: 'urgent',
        category: 'urgent',
        replies: 0,
        likes: 2,
        status: 'new',
        postTitle: 'Course Enrollment Issue',
        analysis: {
          urgency: 'High',
          is_sensitive: false,
          summary: 'Technical issue with payment process preventing enrollment.',
          confidence_score: 0.98
        }
      },
      {
        id: 5,
        platform: 'Twitter',
        author: '@devgirl_mumbai',
        avatar: 'DG',
        content: 'Thank you @APEXAI for the amazing AI course! Got placed at a fintech startup with 40% salary hike. Your career support team is incredible! 🚀',
        timestamp: '1 day ago',
        sentiment: 'positive',
        priority: 'low',
        category: 'positive',
        replies: 8,
        likes: 156,
        status: 'responded',
        postTitle: 'Success Story Tweet',
        analysis: {
          urgency: 'Low',
          is_sensitive: false,
          summary: 'Success story with job placement and salary increase.',
          confidence_score: 0.97
        }
      }
    ];

    // Apply filters
    let filteredComments = mockComments;

    if (filters.platform && filters.platform !== 'all') {
      filteredComments = filteredComments.filter(c => c.platform === filters.platform);
    }
    if (filters.priority && filters.priority !== 'all') {
      filteredComments = filteredComments.filter(c => c.priority === filters.priority);
    }
    if (filters.sentiment && filters.sentiment !== 'all') {
      filteredComments = filteredComments.filter(c => c.sentiment === filters.sentiment);
    }
    if (filters.status && filters.status !== 'all') {
      filteredComments = filteredComments.filter(c => c.status === filters.status);
    }

    return filteredComments;
  }
}

// Export singleton instance
export default new TrustDeskService();
