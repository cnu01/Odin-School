import api from './api';

/**
 * HotLead API Service
 * Handles all API calls for lead scoring, prioritization, and management
 */
class HotLeadService {
  
  /**
   * Ingest a new lead with ML-powered scoring
   * @param {Object} leadData - Lead data to ingest
   * @returns {Promise} Lead ingestion result
   */
  async ingestLead(leadData) {
    try {
      const response = await api.post('/api/hotlead/ingest', {
        email: leadData.email,
        phone: leadData.phone,
        source: leadData.source,
        utm_source: leadData.utm_source,
        utm_medium: leadData.utm_medium,
        utm_campaign: leadData.utm_campaign,
        page_views: leadData.page_views || 1,
        time_on_site: leadData.time_on_site || 30,
        course_pages_viewed: leadData.course_pages_viewed || 0,
        downloads_count: leadData.downloads_count || 0,
        form_submissions: leadData.form_submissions || 1,
        demo_requests: leadData.demo_requests || 0,
        location: leadData.location,
        device: leadData.device || 'desktop',
        first_name: leadData.first_name,
        last_name: leadData.last_name,
        company: leadData.company,
        job_title: leadData.job_title,
        experience_level: leadData.experience_level,
        is_return_visitor: leadData.is_return_visitor || false,
        additional_data: leadData.additional_data || {}
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error ingesting lead:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Get prioritized leads queue
   * @param {Object} options - Query options
   * @returns {Promise} Priority queue response
   */
  async getPriorityQueue(options = {}) {
    try {
      const params = new URLSearchParams();
      if (options.limit) params.append('limit', options.limit);
      if (options.min_score) params.append('min_score', options.min_score);
      if (options.status_filter) params.append('status_filter', options.status_filter);
      if (options.source_filter) params.append('source_filter', options.source_filter);

      const response = await api.get(`/api/hotlead/priority-queue?${params.toString()}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error fetching priority queue:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message,
        data: this.getMockPriorityQueue() // Fallback to mock data
      };
    }
  }

  /**
   * Score an individual lead (legacy endpoint)
   * @param {Object} leadInput - Lead input data
   * @returns {Promise} Scored lead result
   */
  async scoreLead(leadInput) {
    try {
      const response = await api.post('/api/hotlead/score', {
        source: leadInput.source,
        pageviews: leadInput.pageviews,
        device: leadInput.device,
        geography: leadInput.geography,
        form_fields: leadInput.form_fields
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error scoring lead:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Train the HotLead ML model
   * @param {number} size - Training data size
   * @returns {Promise} Training result
   */
  async trainModel(size = 2000) {
    try {
      const response = await api.post(`/api/hotlead/train?size=${size}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error training model:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Get HotLead system status
   * @returns {Promise} System status
   */
  async getSystemStatus() {
    try {
      const response = await api.get('/api/hotlead/status');
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error fetching system status:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Get model information
   * @returns {Promise} Model info
   */
  async getModelInfo() {
    try {
      const response = await api.get('/api/hotlead/model-info');
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error fetching model info:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Update lead contact status
   * @param {Object} updateData - Contact update data
   * @returns {Promise} Update result
   */
  async updateContactStatus(updateData) {
    try {
      const response = await api.post('/api/hotlead/contact/update', {
        lead_id: updateData.lead_id,
        contacted_by: updateData.contacted_by,
        contact_method: updateData.contact_method,
        notes: updateData.notes,
        outcome: updateData.outcome,
        next_action: updateData.next_action
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error updating contact status:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Generate AI-powered outreach message
   * @param {Object} requestData - Outreach request data
   * @returns {Promise} Generated message
   */
  async generateOutreachMessage(requestData) {
    try {
      const response = await api.post('/api/hotlead/messages/outreach', {
        lead_id: requestData.lead_id,
        rep_name: requestData.rep_name,
        contact_method: requestData.contact_method || 'email',
        personalization_data: requestData.personalization_data || {}
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error generating outreach message:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Explain why a lead is prioritized
   * @param {string} leadId - Lead ID
   * @returns {Promise} Lead explanation
   */
  async explainLeadPriority(leadId) {
    try {
      const response = await api.post('/api/hotlead/insights/why-this-lead', {
        lead_id: leadId
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error explaining lead priority:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Seed database with training data
   * @param {number} size - Number of leads to generate
   * @returns {Promise} Seeding result
   */
  async seedDatabase(size = 2000) {
    try {
      const response = await api.post(`/api/hotlead/seed?size=${size}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error seeding database:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Test lead prediction with sample data
   * @param {Object} testData - Test parameters
   * @returns {Promise} Test prediction result
   */
  async testPrediction(testData = {}) {
    try {
      const params = new URLSearchParams();
      if (testData.source) params.append('source', testData.source);
      if (testData.page_views) params.append('page_views', testData.page_views);
      if (testData.time_on_site) params.append('time_on_site', testData.time_on_site);
      if (testData.demo_requests) params.append('demo_requests', testData.demo_requests);

      const response = await api.get(`/api/hotlead/test-prediction?${params.toString()}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error testing prediction:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Get lead analytics (placeholder)
   * @returns {Promise} Analytics data
   */
  async getAnalytics() {
    try {
      const response = await api.get('/api/hotlead/analytics');
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error fetching analytics:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message,
        data: this.getMockAnalytics()
      };
    }
  }

  /**
   * Get mock priority queue data for fallback
   * @returns {Object} Mock priority queue data
   */
  getMockPriorityQueue() {
    return {
      total_priority_leads: 12,
      leads: [
        {
          lead_id: 'LEAD_20250812_001',
          email: 'rahul.sharma@gmail.com',
          source: 'organic',
          priority_score: 89,
          is_priority: true,
          lead_temperature: '🔥 HOT',
          conversion_probability: 0.89,
          assigned_rep: 'alice',
          status: 'new',
          created_at: new Date().toISOString(),
          phone: '+91 98765 43210',
          location: 'Mumbai, India',
          page_views: 12,
          course_pages_viewed: 5,
          downloads_count: 3,
          demo_requests: 1,
          time_on_site: 420,
          device: 'desktop',
          is_return_visitor: true
        },
        {
          lead_id: 'LEAD_20250812_002',
          email: 'priya.patel@outlook.com',
          source: 'referral',
          priority_score: 85,
          is_priority: true,
          lead_temperature: '🔥 HOT',
          conversion_probability: 0.85,
          assigned_rep: 'bob',
          status: 'contacted',
          created_at: new Date(Date.now() - 3600000).toISOString(),
          phone: '+91 87654 32109',
          location: 'Bangalore, India',
          page_views: 8,
          course_pages_viewed: 4,
          downloads_count: 2,
          demo_requests: 1,
          time_on_site: 320,
          device: 'desktop',
          is_return_visitor: false
        },
        {
          lead_id: 'LEAD_20250812_003',
          email: 'amit.kumar@yahoo.com',
          source: 'paid_search',
          priority_score: 76,
          is_priority: true,
          lead_temperature: '🟡 WARM',
          conversion_probability: 0.76,
          assigned_rep: 'charlie',
          status: 'meeting_booked',
          created_at: new Date(Date.now() - 7200000).toISOString(),
          phone: '+91 76543 21098',
          location: 'Delhi, India',
          page_views: 15,
          course_pages_viewed: 6,
          downloads_count: 4,
          demo_requests: 2,
          time_on_site: 580,
          device: 'mobile',
          is_return_visitor: true
        }
      ],
      queue_summary: {
        total_in_queue: 12,
        uncontacted: 8,
        avg_score: 83.5
      }
    };
  }

  /**
   * Get mock analytics data for fallback
   * @returns {Object} Mock analytics data
   */
  getMockAnalytics() {
    return {
      analytics_summary: "HotLead AI-driven prioritization performance analysis",
      current_metrics: {
        total_leads_today: 47,
        priority_leads: 12,
        avg_score: 73.2,
        conversion_rate: 18.5,
        speed_to_contact: '14.2 minutes'
      },
      source_performance: [
        { source: 'referral', leads: 8, conversion_rate: 45.2, avg_score: 87.3 },
        { source: 'organic', leads: 15, conversion_rate: 22.1, avg_score: 78.1 },
        { source: 'paid_search', leads: 12, conversion_rate: 16.8, avg_score: 71.5 },
        { source: 'social_media', leads: 12, conversion_rate: 8.9, avg_score: 58.2 }
      ],
      solutions_ranked_by_impact: [
        {
          solution: "Faster response to referral leads",
          impact: "25% conversion boost",
          difficulty: "Low"
        },
        {
          solution: "Improve organic lead qualification",
          impact: "15% efficiency gain",
          difficulty: "Medium"
        }
      ],
      success_metrics_tracking: {
        meeting_booking_rate: 35.7,
        no_show_reduction: 12.3,
        win_rate_improvement: 8.9
      }
    };
  }
  /**
   * Get problem analysis and business insights - REQUIRED BY REFERENCE
   * @returns {Promise} Problem analysis data
   */
  async getProblemAnalysis() {
    try {
      const response = await api.get('/api/hotlead/problem-analysis');
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error fetching problem analysis:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Get dashboard data including problems and metrics - ENHANCED
   * @returns {Promise} Dashboard data
   */
  async getDashboardData() {
    try {
      const response = await api.get('/api/hotlead/dashboard-data');
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message
      };
    }
  }

  /**
   * Helper: Format lead temperature with color
   * @param {string} temperature - Lead temperature
   */
  getTemperatureColor(temperature) {
    switch (temperature?.toLowerCase()) {
      case 'hot':
        return '#f44336'; // Red
      case 'warm':
        return '#ff9800'; // Orange
      case 'cold':
        return '#2196f3'; // Blue
      default:
        return '#9e9e9e'; // Gray
    }
  }

  /**
   * Helper: Format priority score with level
   * @param {number} score - Priority score
   */
  getPriorityLevel(score) {
    if (score >= 80) return { level: 'Critical', color: '#f44336' };
    if (score >= 60) return { level: 'High', color: '#ff9800' };
    if (score >= 40) return { level: 'Medium', color: '#2196f3' };
    return { level: 'Low', color: '#4caf50' };
  }

  /**
   * Helper: Get source icon
   * @param {string} source - Lead source
   */
  getSourceIcon(source) {
    switch (source?.toLowerCase()) {
      case 'organic':
      case 'seo':
        return '🔍';
      case 'paid_search':
      case 'google_ads':
        return '📢';
      case 'social_media':
      case 'facebook':
      case 'linkedin':
        return '📱';
      case 'referral':
        return '👥';
      case 'email':
        return '📧';
      case 'website_form':
        return '🌐';
      default:
        return '📊';
    }
  }

  /**
   * Create sample lead for testing - REFERENCE COMPLIANT
   */
  createSampleLead() {
    return {
      email: 'student@example.com',
      phone: '+91-9876543210',
      source: 'website_form',
      utm_source: 'google',
      utm_medium: 'cpc',
      utm_campaign: 'data_science_2025',
      page_views: 8,
      time_on_site: 245.5,
      course_pages_viewed: 3,
      downloads_count: 2,
      form_submissions: 1,
      demo_requests: 1,
      location: 'Bangalore',
      device: 'desktop',
      referrer_url: 'https://google.com/search',
      first_name: 'John',
      last_name: 'Doe',
      company: 'Tech Solutions',
      job_title: 'Software Engineer',
      experience_level: 'intermediate',
      is_return_visitor: false
    };
  }
}

// Export singleton instance
export default new HotLeadService();
