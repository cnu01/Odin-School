import api from './api';

/**
 * ReferMore AI Service - Clean version with only essential methods
 * Handles core ML-driven referral optimization functionality
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
   * Get top referral candidates from database with ML scoring
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
   * Generate AI-personalized message for a candidate
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
   * Get analytics summary with ML-driven insights
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
   * Get AI-powered problem analysis for business insights
   * @param {boolean} forceRefresh - Bypass cache and generate fresh analysis
   */
  async getProblemAnalysis(forceRefresh = false) {
    try {
      const response = await api.get(`${this.baseURL}/problem-analysis`, {
        params: { force_refresh: forceRefresh }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching problem analysis:', error);
      throw new Error('Failed to fetch problem analysis');
    }
  }

  /**
   * Get dashboard data (combined metrics and analysis)
   * @param {boolean} forceRefresh - Bypass cache and generate fresh analysis
   */
  async getDashboardData(forceRefresh = false) {
    try {
      const response = await api.get(`${this.baseURL}/dashboard-data`, {
        params: { force_refresh: forceRefresh }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw new Error('Failed to fetch dashboard data');
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
