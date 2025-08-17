import api from './api';

/**
 * PriceSense AI Service - Pricing Optimization with Segment-Aware Recommendations
 * Handles all API calls for pricing optimization, plan recommendations, and messaging
 */
class PriceSenseService {
  constructor() {
    this.baseURL = '/api/pricesense';
  }

  /**
   * Get system status and model information
   */
  async getStatus() {
    try {
      const response = await api.get(`${this.baseURL}/status`);
      return response.data;
    } catch (error) {
      console.error('Error fetching PriceSense status:', error);
      throw new Error('Failed to fetch system status');
    }
  }

  /**
   * Get AI-powered problem analysis for pricing optimization
   * @param {boolean} forceRefresh - Force refresh of analysis
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
   * Get AI-first solutions for pricing optimization
   */
  async getProposedSolutions() {
    try {
      const response = await api.get(`${this.baseURL}/solutions`);
      return response.data;
    } catch (error) {
      console.error('Error fetching proposed solutions:', error);
      throw new Error('Failed to fetch proposed solutions');
    }
  }

  /**
   * Get comprehensive dashboard data for Live Demo
   * @param {string} timeRange - Time range for data (e.g., "7d", "30d")
   * @param {boolean} includeAnomalies - Include anomaly detection
   */
  async getDashboardData(timeRange = "7d", includeAnomalies = true) {
    try {
      const response = await api.get(`${this.baseURL}/dashboard-data`, {
        params: { time_range: timeRange, include_anomalies: includeAnomalies }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw new Error('Failed to fetch dashboard data');
    }
  }

  /**
   * Optimize plan selection for user segments
   * @param {Array} segments - Array of UserSegment objects
   */
  async optimizePlanSelection(segments) {
    try {
      const response = await api.post(`${this.baseURL}/optimize`, segments);
      return response.data;
    } catch (error) {
      console.error('Error optimizing plan selection:', error);
      throw new Error('Failed to optimize plan selection');
    }
  }

  /**
   * Get pricing recommendations
   * @param {number} limit - Number of recommendations to return
   * @param {number} threshold - Minimum optimization score threshold
   */
  async getRecommendations(limit = 20, threshold = 70.0) {
    try {
      const response = await api.get(`${this.baseURL}/recommendations`, {
        params: { limit, threshold }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      throw new Error('Failed to fetch pricing recommendations');
    }
  }

  /**
   * Generate personalized pricing message
   * @param {Object} segment - User segment data
   * @param {string} messageType - Type of message to generate
   */
  async generateMessage(segment, messageType = 'pricing_offer') {
    try {
      const response = await api.post(`${this.baseURL}/message`, {
        segment,
        message_type: messageType
      });
      return response.data;
    } catch (error) {
      console.error('Error generating pricing message:', error);
      throw new Error('Failed to generate pricing message');
    }
  }

  /**
   * Personalize pricing message for a segment
   * @param {Object} segment - User segment data
   */
  async personalizeMessage(segment) {
    try {
      const response = await api.post(`${this.baseURL}/messages/personalize`, segment);
      return response.data;
    } catch (error) {
      console.error('Error personalizing message:', error);
      throw new Error('Failed to personalize message');
    }
  }

  /**
   * Track plan performance events
   * @param {Object} event - Performance tracking event
   */
  async trackPerformance(event) {
    try {
      const response = await api.post(`${this.baseURL}/performance/track`, event);
      return response.data;
    } catch (error) {
      console.error('Error tracking performance:', error);
      throw new Error('Failed to track performance');
    }
  }

  /**
   * Get analytics data
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
   * Get comprehensive analytics summary
   * @param {number} sampleSize - Sample size for analytics
   */
  async getAnalyticsSummary(sampleSize = 500) {
    try {
      const response = await api.get(`${this.baseURL}/analytics/summary`, {
        params: { sample_size: sampleSize }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching analytics summary:', error);
      throw new Error('Failed to fetch analytics summary');
    }
  }

  /**
   * Get plan performance analytics
   * @param {Object} params - Analytics parameters
   */
  async getPlanAnalytics(params = {}) {
    try {
      const response = await api.post(`${this.baseURL}/analytics/plan-performance`, {
        plan_ids: params.planIds || [],
        segment_filter: params.segmentFilter,
        time_range_days: params.timeRangeDays || 30
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching plan analytics:', error);
      throw new Error('Failed to fetch plan analytics');
    }
  }

  /**
   * Get segment insights
   * @param {Object} params - Insights parameters
   */
  async getSegmentInsights(params = {}) {
    try {
      const response = await api.post(`${this.baseURL}/segments/insights`, {
        sample_size: params.sampleSize || 500,
        use_llm: params.useLLM || false,
        focus_segments: params.focusSegments || []
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching segment insights:', error);
      throw new Error('Failed to fetch segment insights');
    }
  }

  /**
   * Get problem analysis for business insights
   * @param {boolean} forceRefresh - Force refresh of analysis
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
   * Get comprehensive dashboard data for Live Demo
   * @param {string} timeRange - Time range for data (e.g., "7d", "30d")
   * @param {boolean} includeAnomalies - Include anomaly detection
   */
  async getDashboardData(timeRange = "7d", includeAnomalies = true) {
    try {
      const response = await api.get(`${this.baseURL}/dashboard-data`, {
        params: { time_range: timeRange, include_anomalies: includeAnomalies }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw new Error('Failed to fetch dashboard data');
    }
  }

  /**
   * Train the pricing model (admin function)
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
      throw new Error('Failed to train pricing model');
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
   * Helper function to format optimization score for display
   * @param {number} score - Raw optimization score (0-100)
   */
  formatOptimizationScore(score) {
    if (score >= 75) return { level: 'High', color: '#4caf50', badge: 'success' };
    if (score >= 50) return { level: 'Medium', color: '#ff9800', badge: 'warning' };
    return { level: 'Low', color: '#f44336', badge: 'error' };
  }

  /**
   * Helper function to format currency values (Indian Rupees)
   * @param {number} amount - Amount in INR
   */
  formatCurrency(amount) {
    if (amount >= 10000000) {
      return `₹${(amount / 10000000).toFixed(1)}Cr`;
    }
    if (amount >= 100000) {
      return `₹${(amount / 100000).toFixed(1)}L`;
    }
    if (amount >= 1000) {
      return `₹${(amount / 1000).toFixed(1)}K`;
    }
    return `₹${amount}`;
  }

  /**
   * Helper function to get segment type icon
   * @param {string} segmentType - Segment type
   */
  getSegmentIcon(segmentType) {
    switch (segmentType?.toLowerCase()) {
      case 'geographic': return '🌏';
      case 'traffic_source': return '🚦';
      case 'device': return '📱';
      case 'price_sensitivity': return '💰';
      default: return '👥';
    }
  }

  /**
   * Helper function to get pricing level color
   * @param {string} level - Pricing level (high/medium/low)
   */
  getPricingLevelColor(level) {
    switch (level?.toLowerCase()) {
      case 'high': return '#4caf50';
      case 'medium': return '#ff9800';
      case 'low': return '#f44336';
      default: return '#9e9e9e';
    }
  }

  /**
   * Helper function to create default segment for testing
   */
  createTestSegment() {
    return {
      source_score: 0.8,
      geography_score: 0.7,
      device_score: 0.9,
      prior_engagement_score: 0.6,
      plan_upfront_amount: 10000,
      plan_total_amount: 25000,
      plan_duration_months: 6,
      plan_monthly_payment: 4500,
      plan_interest_rate: 5.0,
      scholarship_eligible: 1,
      scholarship_discount_pct: 20,
      competitor_price_ratio: 0.95,
      seasonality_factor: 1.1,
      demand_pressure: 1.2,
      price_sensitivity_score: 0.4,
      urgency_score: 0.7,
      income_tier_score: 0.8,
      similar_segment_success: 0.65,
      churn_risk_score: 0.25,
      user_id: 'TEST_USER',
      source: 'organic',
      geography: 'metro_tier1',
      device: 'desktop'
    };
  }

  /**
   * Calculate price elasticity impact
   * @param {number} currentPrice - Current price
   * @param {number} newPrice - New price  
   * @param {number} elasticity - Price elasticity coefficient
   */
  calculateElasticityImpact(currentPrice, newPrice, elasticity = 0.65) {
    const priceChange = (newPrice - currentPrice) / currentPrice;
    const demandChange = -elasticity * priceChange;
    return {
      priceChangePercent: priceChange * 100,
      demandChangePercent: demandChange * 100,
      revenueMultiplier: (1 + priceChange) * (1 + demandChange)
    };
  }
}

// Export singleton instance
const pricesenseService = new PriceSenseService();
export default pricesenseService;
