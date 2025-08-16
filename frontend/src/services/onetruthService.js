import api from './api';

/**
 * OneTruth AI Service - Marketing Analytics with Unified Business Intelligence
 * Handles all API calls for marketing analytics unification and executive decision support
 */
class OnetruthService {
  constructor() {
    this.baseURL = '/api/onetruth';
  }

  /**
   * Get system status and model information
   */
  async getStatus() {
    try {
      const response = await api.get(`${this.baseURL}/status`);
      return response.data;
    } catch (error) {
      console.error('Error fetching OneTruth status:', error);
      throw new Error('Failed to fetch system status');
    }
  }

  /**
   * Get AI-powered problem analysis for marketing analytics
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
   * Get AI-first solutions for marketing analytics problems
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
   * Get unified analytics dashboard
   * @param {string} timeRange - Time range for analytics
   * @param {boolean} includeAnomalies - Include anomaly detection
   */
  async getUnifiedDashboard(timeRange = "7d", includeAnomalies = true) {
    try {
      const response = await api.get(`${this.baseURL}/dashboard`, {
        params: { time_range: timeRange, include_anomalies: includeAnomalies }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching unified dashboard:', error);
      throw new Error('Failed to fetch unified dashboard');
    }
  }

  /**
   * Detect business anomalies across integrated systems
   * @param {string} timeRange - Time range for anomaly detection
   */
  async detectAnomalies(timeRange = "7d") {
    try {
      const response = await api.get(`${this.baseURL}/anomalies`, {
        params: { time_range: timeRange }
      });
      return response.data;
    } catch (error) {
      console.error('Error detecting anomalies:', error);
      throw new Error('Failed to detect anomalies');
    }
  }

  /**
   * Generate AI-powered executive brief
   * @param {boolean} useLLM - Use AI for enhanced insights
   * @param {number} horizonDays - Analysis horizon in days
   */
  async generateExecutiveBrief(useLLM = true, horizonDays = 7) {
    try {
      const response = await api.post(`${this.baseURL}/executive-brief`, {
        use_llm: useLLM,
        horizon_days: horizonDays
      });
      return response.data;
    } catch (error) {
      console.error('Error generating executive brief:', error);
      throw new Error('Failed to generate AI-powered executive brief');
    }
  }

  /**
   * Get executive decision recommendations
   */
  async getExecutiveDecisions() {
    try {
      const response = await api.get(`${this.baseURL}/decisions`);
      return response.data;
    } catch (error) {
      console.error('Error fetching executive decisions:', error);
      throw new Error('Failed to fetch executive decisions');
    }
  }

  /**
   * Verify data consistency across business systems
   * @param {Array} systems - List of systems to verify
   * @param {number} timeRangeDays - Time range for verification
   */
  async verifyDataConsistency(systems = ["CRM", "GA4", "Ad Platforms", "Support", "Telephony", "LMS"], timeRangeDays = 7) {
    try {
      const response = await api.post(`${this.baseURL}/data-verification`, {
        systems,
        time_range_days: timeRangeDays
      });
      return response.data;
    } catch (error) {
      console.error('Error verifying data consistency:', error);
      throw new Error('Failed to verify data consistency');
    }
  }

  /**
   * Get analytics performance metrics
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
   * Train the OneTruth ML model (admin function)
   * @param {number} size - Training data size
   */
  async trainModel(size = 2000) {
    try {
      const response = await api.post(`${this.baseURL}/train`, {
        size
      });
      return response.data;
    } catch (error) {
      console.error('Error training model:', error);
      throw new Error('Failed to train OneTruth model');
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
   * Seed database with analytics data (admin function)
   * @param {number} size - Number of records to seed
   */
  async seedData(size = 2000) {
    try {
      const response = await api.post(`${this.baseURL}/seed`, {
        size
      });
      return response.data;
    } catch (error) {
      console.error('Error seeding data:', error);
      throw new Error('Failed to seed analytics data');
    }
  }

  /**
   * Helper function to format health scores
   * @param {number} score - Health score (0-100)
   */
  formatHealthScore(score) {
    if (score >= 80) return { level: 'Excellent', color: '#4caf50', badge: 'success' };
    if (score >= 60) return { level: 'Good', color: '#ff9800', badge: 'warning' };
    if (score >= 40) return { level: 'Fair', color: '#f44336', badge: 'error' };
    return { level: 'Poor', color: '#9e9e9e', badge: 'default' };
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
   * Helper function to format percentages
   * @param {number} value - Decimal value (0-1)
   */
  formatPercentage(value) {
    return `${(value * 100).toFixed(1)}%`;
  }

  /**
   * Helper function to get anomaly severity color
   * @param {number} anomalyScore - Anomaly score (0-1)
   */
  getAnomalySeverityColor(anomalyScore) {
    if (anomalyScore >= 0.8) return 'error';
    if (anomalyScore >= 0.5) return 'warning';
    return 'info';
  }
}

// Export singleton instance
const onetruthService = new OnetruthService();
export default onetruthService;
