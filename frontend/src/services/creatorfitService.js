import api from './api';

class CreatorFitService {
  constructor() {
    this.baseURL = '/api/creatorfit';
  }

  // Comprehensive creator analysis with business intelligence
  async analyzeCreators(file, programType = 'data_science', campaignBudget = 100000) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('program_type', programType);
      formData.append('campaign_budget', campaignBudget);

      const response = await api.post(`${this.baseURL}/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // Extended timeout for ML processing
      });

      return response.data;
    } catch (error) {
      console.error('Error analyzing creators:', error);
      throw new Error(
        error.response?.data?.detail || 
        error.response?.data?.error || 
        'Failed to analyze creators'
      );
    }
  }

  // Lead forecasting with booking recommendations
  async forecastLeads(file, programType = 'data_science') {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('program_type', programType);

      const response = await api.post(`${this.baseURL}/forecast`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // Extended timeout for ML processing
      });

      return response.data;
    } catch (error) {
      console.error('Error forecasting leads:', error);
      throw new Error(
        error.response?.data?.detail || 
        error.response?.data?.error || 
        'Failed to forecast leads'
      );
    }
  }

  // Get available program types
  async getPrograms() {
    try {
      const response = await api.get(`${this.baseURL}/programs`);
      return response.data;
    } catch (error) {
      console.error('Error fetching programs:', error);
      throw new Error('Failed to fetch available programs');
    }
  }

  // Health check for CreatorFit service
  async healthCheck() {
    try {
      const response = await api.get(`${this.baseURL}/health`);
      return response.data;
    } catch (error) {
      console.error('CreatorFit health check failed:', error);
      throw new Error('CreatorFit service unavailable');
    }
  }

  // Utility method to validate CSV file
  validateCSVFile(file) {
    const errors = [];
    
    // Check file type
    if (!file.name.toLowerCase().endsWith('.csv')) {
      errors.push('File must be a CSV file');
    }
    
    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      errors.push('File size must be less than 10MB');
    }
    
    // Check if file is empty
    if (file.size === 0) {
      errors.push('File cannot be empty');
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Format creator results for display
  formatCreatorResults(results) {
    if (!Array.isArray(results)) return [];

    return results.map(creator => ({
      ...creator,
      formattedLeads: creator.predicted_qualified_leads?.toLocaleString() || '0',
      formattedViews: creator.views_90d?.toLocaleString() || '0',
      formattedFitScore: `${(creator.fit_score * 100).toFixed(1)}%`,
      formattedConfidence: `${(creator.confidence_score * 100).toFixed(1)}%`,
      statusColor: this.getStatusColor(creator.recommendation),
      statusIcon: this.getStatusIcon(creator.recommendation)
    }));
  }

  // Get status color for recommendations
  getStatusColor(recommendation) {
    switch (recommendation) {
      case 'BOOK': return 'success';
      case 'REVIEW': return 'warning';
      case 'SKIP': return 'error';
      default: return 'default';
    }
  }

  // Get status icon for recommendations
  getStatusIcon(recommendation) {
    switch (recommendation) {
      case 'BOOK': return 'check_circle';
      case 'REVIEW': return 'schedule';
      case 'SKIP': return 'cancel';
      default: return 'help';
    }
  }
}

export default new CreatorFitService();
