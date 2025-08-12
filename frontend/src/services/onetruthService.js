import api from './api';

const ONETRUTH_BASE_URL = '/api/onetruth';

export const onetruthService = {
  // Dashboard and Analytics
  async getDashboard(timeRange = '7d', includeAnomalies = true) {
    try {
      const response = await api.get(`${ONETRUTH_BASE_URL}/dashboard`, {
        params: { time_range: timeRange, include_anomalies: includeAnomalies }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch dashboard: ${error.response?.data?.detail || error.message}`);
    }
  },

  async getAnalytics(sampleSize = 500) {
    try {
      const response = await api.get(`${ONETRUTH_BASE_URL}/analytics`, {
        params: { sample_size: sampleSize }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch analytics: ${error.response?.data?.detail || error.message}`);
    }
  },

  // Anomaly Detection
  async detectAnomalies(timeRange = '7d') {
    try {
      const response = await api.get(`${ONETRUTH_BASE_URL}/anomalies`, {
        params: { time_range: timeRange }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to detect anomalies: ${error.response?.data?.detail || error.message}`);
    }
  },

  // Executive Intelligence
  async getExecutiveBrief(useLLM = false, horizonDays = 7) {
    try {
      const response = await api.post(`${ONETRUTH_BASE_URL}/executive-brief`, {
        use_llm: useLLM,
        horizon_days: horizonDays,
        include_decisions: true
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to generate executive brief: ${error.response?.data?.detail || error.message}`);
    }
  },

  async getExecutiveDecisions() {
    try {
      const response = await api.get(`${ONETRUTH_BASE_URL}/decisions`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch executive decisions: ${error.response?.data?.detail || error.message}`);
    }
  },

  // Model Operations
  async trainModel(size = 2000) {
    try {
      const response = await api.post(`${ONETRUTH_BASE_URL}/train`, { size });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to train model: ${error.response?.data?.detail || error.message}`);
    }
  },

  async evaluateModel(sampleSize = 10) {
    try {
      const response = await api.get(`${ONETRUTH_BASE_URL}/evaluate`, {
        params: { sample_size: sampleSize }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to evaluate model: ${error.response?.data?.detail || error.message}`);
    }
  },

  // Data Management
  async seedDatabase(size = 2000) {
    try {
      const response = await api.post(`${ONETRUTH_BASE_URL}/seed`, { size });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to seed database: ${error.response?.data?.detail || error.message}`);
    }
  },

  async verifyDataConsistency(systems = ['CRM', 'GA4', 'Ads', 'Support', 'Telephony', 'LMS'], timeRangeDays = 7) {
    try {
      const response = await api.post(`${ONETRUTH_BASE_URL}/verify`, {
        systems,
        time_range_days: timeRangeDays
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to verify data: ${error.response?.data?.detail || error.message}`);
    }
  },

  // Analytics Outcome Tracking
  async recordAnalyticsOutcome(outcome) {
    try {
      const response = await api.post(`${ONETRUTH_BASE_URL}/record-outcome`, outcome);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to record outcome: ${error.response?.data?.detail || error.message}`);
    }
  },

  // System Status
  async getSystemStatus() {
    try {
      const response = await api.get(`${ONETRUTH_BASE_URL}/status`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get system status: ${error.response?.data?.detail || error.message}`);
    }
  }
};

export default onetruthService;
