import api from './api';

/**
 * FirstTouch AI Service
 * Handles all API calls for call timing optimization and sales automation
 */
class FirstTouchService {
  constructor() {
    this.baseURL = '/api/firsttouch';
  }

  /**
   * Get system status and model information
   */
  async getStatus() {
    try {
      const response = await api.get(`${this.baseURL}/status`);
      return response.data;
    } catch (error) {
      console.error('Error fetching FirstTouch status:', error);
      throw new Error('Failed to fetch system status');
    }
  }

  /**
   * Optimize call timing for a lead - CORE FEATURE
   * @param {Object} leadProfile - Lead profile data
   * @param {Array} preferredTimeWindows - Optional time windows
   */
  async optimizeCallTiming(leadProfile, preferredTimeWindows = null) {
    try {
      const response = await api.post(`${this.baseURL}/optimize-call-timing`, {
        lead_profile: leadProfile,
        preferred_time_windows: preferredTimeWindows
      });
      return response.data;
    } catch (error) {
      console.error('Error optimizing call timing:', error);
      throw new Error('Failed to optimize call timing');
    }
  }

  /**
   * Get call performance analytics
   * @param {Object} analyticsRequest - Analytics parameters
   */
  async getCallAnalytics(analyticsRequest) {
    try {
      const response = await api.post(`${this.baseURL}/call-analytics`, analyticsRequest);
      return response.data;
    } catch (error) {
      console.error('Error fetching call analytics:', error);
      throw new Error('Failed to fetch call analytics');
    }
  }

  /**
   * Get problem analysis for business insights
   */
  async getProblemAnalysis() {
    try {
      const response = await api.get(`${this.baseURL}/problem-analysis`);
      return response.data;
    } catch (error) {
      console.error('Error fetching problem analysis:', error);
      throw new Error('Failed to fetch problem analysis');
    }
  }

  /**
   * Train the FirstTouch model (admin function)
   * @param {number} trainingSize - Number of training samples
   */
  async trainModel(trainingSize = 2000) {
    try {
      const response = await api.post(`${this.baseURL}/train`, {
        training_size: trainingSize,
        validation_split: 0.2
      });
      return response.data;
    } catch (error) {
      console.error('Error training model:', error);
      throw new Error('Failed to train model');
    }
  }

  /**
   * Evaluate model performance (admin function)
   * @param {number} sampleSize - Sample size for evaluation
   */
  async evaluateModel(sampleSize = 100) {
    try {
      const response = await api.get(`${this.baseURL}/evaluate`, {
        params: { sample_size: sampleSize }
      });
      return response.data;
    } catch (error) {
      console.error('Error evaluating model:', error);
      throw new Error('Failed to evaluate model');
    }
  }

  /**
   * Helper function to create test lead profile
   * For demo and testing purposes
   */
  createTestLead() {
    return {
      lead_id: `LEAD_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      source: 'website',
      intent_type: 'demo_request',
      urgency_level: 'high',
      geography: 'tier_1',
      device: 'desktop',
      lead_source_score: 0.85,
      lead_intent_score: 0.90,
      lead_urgency_score: 0.95,
      geography_score: 0.80,
      device_type_score: 0.75,
      time_since_inquiry_minutes: 3,
      lead_engagement_score: 0.88,
      estimated_ltv: 45000.0
    };
  }

  /**
   * Helper function to get lead source icon
   * @param {string} source - Lead source
   */
  getSourceIcon(source) {
    switch (source?.toLowerCase()) {
      case 'website': return '🌐';
      case 'social': return '📱';
      case 'referral': return '👥';
      case 'advertisement': return '📢';
      default: return '📊';
    }
  }

  /**
   * Helper function to get intent type color
   * @param {string} intentType - Intent type
   */
  getIntentColor(intentType) {
    switch (intentType?.toLowerCase()) {
      case 'demo_request': return '#4caf50';
      case 'course_inquiry': return '#ff9800';
      case 'pricing': return '#2196f3';
      case 'general_info': return '#9e9e9e';
      default: return '#757575';
    }
  }

  /**
   * Helper function to get urgency badge color
   * @param {string} urgencyLevel - Urgency level
   */
  getUrgencyColor(urgencyLevel) {
    switch (urgencyLevel?.toLowerCase()) {
      case 'high': return '#f44336';
      case 'medium': return '#ff9800';
      case 'low': return '#4caf50';
      default: return '#9e9e9e';
    }
  }

  /**
   * Helper function to format success probability
   * @param {number} probability - Success probability (0-1)
   */
  formatProbability(probability) {
    const percentage = (probability * 100).toFixed(1);
    let level, color;
    
    if (probability >= 0.7) {
      level = 'High';
      color = '#4caf50';
    } else if (probability >= 0.4) {
      level = 'Medium';
      color = '#ff9800';
    } else {
      level = 'Low';
      color = '#f44336';
    }

    return { percentage, level, color };
  }

  /**
   * Helper function to format timing recommendation
   * @param {Object} timing - Timing object
   */
  formatTiming(timing) {
    const { recommended_time, priority_level, call_window } = timing;
    
    let urgencyText, urgencyColor;
    switch (call_window) {
      case 'immediate':
        urgencyText = 'Call Now';
        urgencyColor = '#f44336';
        break;
      case 'within_15_minutes':
        urgencyText = 'Call within 15 min';
        urgencyColor = '#ff9800';
        break;
      case 'within_1_hour':
        urgencyText = 'Call within 1 hour';
        urgencyColor = '#2196f3';
        break;
      default:
        urgencyText = 'Schedule call';
        urgencyColor = '#9e9e9e';
    }

    return { urgencyText, urgencyColor, priorityLevel: priority_level };
  }

  /**
   * Create analytics request for date range
   * @param {string} startDate - Start date (YYYY-MM-DD)
   * @param {string} endDate - End date (YYYY-MM-DD)
   * @param {Object} filters - Optional filters
   */
  createAnalyticsRequest(startDate, endDate, filters = {}) {
    return {
      date_range: [startDate, endDate],
      filters: {
        agent_ids: filters.agentIds || [],
        lead_sources: filters.leadSources || [],
        geography: filters.geography || []
      },
      metrics: ['connect_rate', 'qualification_rate', 'conversion_rate']
    };
  }

  /**
   * Calculate lead priority score color
   * @param {number} score - Priority score (0-100)
   */
  getPriorityScoreColor(score) {
    if (score >= 80) return '#4caf50'; // Green
    if (score >= 60) return '#ff9800'; // Orange
    if (score >= 40) return '#2196f3'; // Blue
    return '#f44336'; // Red
  }

  /**
   * Format currency values
   * @param {number} amount - Amount in currency
   */
  formatCurrency(amount) {
    if (amount >= 100000) {
      return `₹${(amount / 100000).toFixed(1)}L`;
    }
    if (amount >= 1000) {
      return `₹${(amount / 1000).toFixed(1)}K`;
    }
    return `₹${amount}`;
  }

  /**
   * Get lead temperature based on scores
   * @param {Object} leadProfile - Lead profile
   */
  getLeadTemperature(leadProfile) {
    const avgScore = (
      leadProfile.lead_source_score +
      leadProfile.lead_intent_score + 
      leadProfile.lead_urgency_score +
      leadProfile.lead_engagement_score
    ) / 4;

    if (avgScore >= 0.8) return { temp: 'Hot', color: '#f44336' };
    if (avgScore >= 0.6) return { temp: 'Warm', color: '#ff9800' };
    return { temp: 'Cold', color: '#2196f3' };
  }
}

// Export singleton instance
const firsttouchService = new FirstTouchService();
export default firsttouchService;
