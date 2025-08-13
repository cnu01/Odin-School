import api from './api';

/**
 * ReferMore AI Service
 * Handles all API calls for referral optimization and management
 */
class RefermoreService {
  constructor() {
    this.baseURL = '/api/refermore';
  }

  /**
   * Get system status and model information
   */
  async getStatus() {
    try {
      const response = await api.get(`${this.baseURL}/status`);
      return response.data;
    } catch (error) {
      console.error('Error fetching Refermore status:', error);
      throw new Error('Failed to fetch system status');
    }
  }

  /**
   * Score referral propensity for a single profile
   * @param {Object} profile - User profile data
   */
  async scoreReferralPropensity(profile) {
    try {
      const response = await api.post(`${this.baseURL}/score`, profile);
      return response.data;
    } catch (error) {
      console.error('Error scoring referral propensity:', error);
      throw new Error('Failed to score referral propensity');
    }
  }

  /**
   * Get top referral candidates
   * @param {number} limit - Number of candidates to return
   * @param {number} threshold - Minimum score threshold (0.0-1.0)
   */
  async getCandidates(limit = 20, threshold = 0.6) {
    try {
      const response = await api.get(`${this.baseURL}/candidates`, {
        params: { limit, threshold }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching referral candidates:', error);
      throw new Error('Failed to fetch referral candidates');
    }
  }

  /**
   * Generate personalized referral message
   * @param {Object} profile - User profile data
   * @param {string} messageType - Type of message to generate
   */
  async generateMessage(profile, messageType = 'referral_invite') {
    try {
      const response = await api.post(`${this.baseURL}/message`, {
        profile,
        message_type: messageType
      });
      return response.data;
    } catch (error) {
      console.error('Error generating message:', error);
      throw new Error('Failed to generate personalized message');
    }
  }

  /**
   * Generate personalized message for a candidate
   * @param {Object} profile - User profile data
   */
  async personalizeMessage(profile) {
    try {
      const response = await api.post(`${this.baseURL}/messages/personalize`, profile);
      return response.data;
    } catch (error) {
      console.error('Error personalizing message:', error);
      throw new Error('Failed to personalize message');
    }
  }

  /**
   * Track referral events
   * @param {Object} event - Event tracking data
   */
  async trackEvent(event) {
    try {
      const response = await api.post(`${this.baseURL}/referrals/track`, event);
      return response.data;
    } catch (error) {
      console.error('Error tracking referral event:', error);
      throw new Error('Failed to track referral event');
    }
  }

  /**
   * Get analytics summary
   * @param {number} sampleSize - Sample size for analytics
   */
  async getAnalytics(sampleSize = 500) {
    try {
      const response = await api.get(`${this.baseURL}/analytics`, {
        params: { sample_size: sampleSize }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching analytics:', error);
      throw new Error('Failed to fetch analytics data');
    }
  }

  /**
   * Get detailed analytics insights
   * @param {Object} params - Analytics parameters
   */
  async getAnalyticsInsights(params = {}) {
    try {
      const response = await api.post(`${this.baseURL}/analytics/insights`, {
        sample_size: params.sampleSize || 500,
        use_llm: params.useLLM || false,
        horizon_days: params.horizonDays || 7
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching analytics insights:', error);
      throw new Error('Failed to fetch analytics insights');
    }
  }

  /**
   * Get progress message for a referrer
   * @param {Object} params - Progress message parameters
   */
  async getProgressMessage(params) {
    try {
      const response = await api.post(`${this.baseURL}/messages/progress`, {
        referrer_id: params.referrerId,
        name: params.name,
        use_llm: params.useLLM || false
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching progress message:', error);
      throw new Error('Failed to fetch progress message');
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
   * Get dashboard data (combined metrics and analysis)
   */
  async getDashboardData() {
    try {
      const response = await api.get(`${this.baseURL}/dashboard-data`);
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw new Error('Failed to fetch dashboard data');
    }
  }

  /**
   * Train the referral model (admin function)
   * @param {number} size - Training data size
   */
  async trainModel(size = 2000) {
    try {
      const response = await api.post(`${this.baseURL}/train`, null, {
        params: { size }
      });
      return response.data;
    } catch (error) {
      console.error('Error training model:', error);
      throw new Error('Failed to train referral model');
    }
  }

  /**
   * Evaluate model performance (admin function)
   * @param {number} sampleSize - Evaluation sample size
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
   * Helper function to format propensity score for display
   * @param {number} score - Raw propensity score (0-100)
   */
  formatPropensityScore(score) {
    if (score >= 70) return { level: 'High', color: '#4caf50', badge: 'success' };
    if (score >= 40) return { level: 'Medium', color: '#ff9800', badge: 'warning' };
    return { level: 'Low', color: '#f44336', badge: 'error' };
  }

  /**
   * Helper function to format currency values
   * @param {number} amount - Amount in INR
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
   * Helper function to get insights badge color
   * @param {string} severity - Severity level
   */
  getInsightsBadgeColor(severity) {
    switch (severity?.toLowerCase()) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  }
}

// Export singleton instance
const refermoreService = new RefermoreService();
export default refermoreService;
