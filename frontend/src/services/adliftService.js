import api from './api';

/**
 * AdLift Marketing Optimization Service
 * Handles all API calls for ad performance analysis and optimization
 */
class AdLiftService {
  constructor() {
    this.baseURL = '/api/adlift';
  }

  /**
   * Get system health status
   */
  async getHealthStatus() {
    try {
      const response = await api.get(`${this.baseURL}/health`);
      return response.data;
    } catch (error) {
      console.error('Error fetching AdLift health status:', error);
      throw new Error('Failed to fetch health status');
    }
  }

  /**
   * Analyze CSV file with ad performance data - CORE FEATURE
   * @param {File} csvFile - CSV file containing ad performance data
   */
  async analyzeCSVFile(csvFile) {
    try {
      // Validate file before sending
      if (!csvFile) {
        throw new Error('No file selected');
      }
      
      if (!csvFile.name.toLowerCase().endsWith('.csv')) {
        throw new Error('Please select a CSV file');
      }
      
      if (csvFile.size === 0) {
        throw new Error('CSV file is empty');
      }
      
      if (csvFile.size > 10 * 1024 * 1024) { // 10MB limit
        throw new Error('CSV file is too large (max 10MB)');
      }

      // Validate CSV format by reading first few lines
      const text = await this.readFileAsText(csvFile);
      const lines = text.split('\n').filter(line => line.trim());
      
      if (lines.length < 2) {
        throw new Error('CSV must have at least a header row and one data row');
      }
      
      // Check for required columns
      const header = lines[0].toLowerCase();
      const requiredColumns = [
        'date', 'campaign', 'ad_group', 'headline', 'description',
        'keywords', 'audience_segment', 'placement', 'impressions',
        'clicks', 'spend', 'leads', 'qualified_leads', 'ctr', 'cpc',
        'cvr', 'qualified_rate'
      ];
      
      const missingColumns = requiredColumns.filter(col => !header.includes(col));
      if (missingColumns.length > 0) {
        throw new Error(`Missing required columns: ${missingColumns.join(', ')}`);
      }

      const formData = new FormData();
      formData.append('file', csvFile);

      const response = await api.post(`${this.baseURL}/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data;
    } catch (error) {
      console.error('Error analyzing CSV file:', error);
      
      // Provide user-friendly error messages
      let userMessage = error.message;
      if (error.response?.data?.message) {
        userMessage = error.response.data.message;
      } else if (error.message.includes('Network Error')) {
        userMessage = 'Unable to connect to the analysis server. Please try again.';
      } else if (error.message.includes('timeout')) {
        userMessage = 'Analysis is taking too long. Please try with a smaller file.';
      }
      
      throw new Error(userMessage);
    }
  }

  /**
   * Helper to read file as text for validation
   * @param {File} file - File to read
   */
  readFileAsText(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsText(file);
    });
  }

  /**
   * Create sample CSV data for demo purposes
   */
  createSampleCSVData() {
    const sampleData = [
      {
        date: '2025-01-01',
        campaign: 'Data Science Q1',
        ad_group: 'Career Switch',
        headline: 'Become a Data Scientist in 6 Months',
        description: 'Transform your career with our comprehensive program',
        keywords: 'data science course, career change, bootcamp',
        audience_segment: 'Working Professionals',
        placement: 'Google Search',
        impressions: 10000,
        clicks: 250,
        spend: 1500,
        leads: 25,
        qualified_leads: 15,
        CTR: 0.025,
        CPC: 6.0,
        CVR: 0.10,
        qualified_rate: 0.60
      },
      {
        date: '2025-01-02',
        campaign: 'Data Science Q1',
        ad_group: 'Career Switch',
        headline: 'Master Data Science - Job Guaranteed',
        description: 'Learn Python, ML, and get hired in 6 months',
        keywords: 'data science jobs, machine learning, python',
        audience_segment: 'Working Professionals',
        placement: 'Google Search',
        impressions: 8500,
        clicks: 340,
        spend: 2040,
        leads: 34,
        qualified_leads: 22,
        CTR: 0.040,
        CPC: 6.0,
        CVR: 0.10,
        qualified_rate: 0.65
      },
      {
        date: '2025-01-03',
        campaign: 'AI/ML Bootcamp',
        ad_group: 'Recent Graduates',
        headline: 'AI Engineer in 4 Months',
        description: 'Start your AI career with hands-on projects',
        keywords: 'ai engineer, machine learning engineer, artificial intelligence',
        audience_segment: 'Recent Graduates',
        placement: 'Facebook Ads',
        impressions: 15000,
        clicks: 450,
        spend: 1800,
        leads: 36,
        qualified_leads: 18,
        CTR: 0.030,
        CPC: 4.0,
        CVR: 0.08,
        qualified_rate: 0.50
      }
    ];

    return sampleData;
  }

  /**
   * Generate sample CSV file for download/testing
   */
  generateSampleCSV() {
    const data = this.createSampleCSVData();
    const headers = Object.keys(data[0]);
    
    // Helper function to properly escape CSV values
    const escapeCsvValue = (value) => {
      if (value === null || value === undefined) return '';
      const str = String(value);
      if (str.includes(',') || str.includes('"') || str.includes('\n')) {
        return '"' + str.replace(/"/g, '""') + '"';
      }
      return str;
    };
    
    let csvContent = headers.join(',') + '\n';
    data.forEach(row => {
      csvContent += headers.map(header => escapeCsvValue(row[header])).join(',') + '\n';
    });
    
    return csvContent;
  }

  /**
   * Helper function to format performance metrics
   * @param {Object} metrics - Performance metrics
   */
  formatMetrics(metrics) {
    return {
      ctr: `${(metrics.CTR * 100).toFixed(2)}%`,
      cpc: `₹${metrics.CPC?.toFixed(2) || 0}`,
      cvr: `${(metrics.CVR * 100).toFixed(2)}%`,
      cpql: `₹${metrics.CPQL?.toFixed(2) || 0}`,
      qpi: (metrics.QPI * 1000).toFixed(3) // QPI in per mille
    };
  }

  /**
   * Helper function to get performance level color
   * @param {string} metric - Metric name (CTR, CPQL, QPI)
   * @param {number} value - Metric value
   */
  getPerformanceColor(metric, value) {
    switch (metric.toLowerCase()) {
      case 'ctr':
        if (value >= 0.035) return '#4caf50'; // Green - Good
        if (value >= 0.020) return '#ff9800'; // Orange - Average
        return '#f44336'; // Red - Poor
      
      case 'cpql':
        if (value <= 100) return '#4caf50'; // Green - Good
        if (value <= 200) return '#ff9800'; // Orange - Average
        return '#f44336'; // Red - Poor
      
      case 'qpi':
        if (value >= 0.005) return '#4caf50'; // Green - Good
        if (value >= 0.002) return '#ff9800'; // Orange - Average
        return '#f44336'; // Red - Poor
      
      default:
        return '#9e9e9e';
    }
  }

  /**
   * Helper function to determine fatigue status
   * @param {Object} campaign - Campaign data
   */
  getFatigueStatus(campaign) {
    const daysLive = campaign.days_live || 0;
    const performanceDrop = campaign.performance_drop || 0;

    if (daysLive >= 10 && performanceDrop >= 0.20) {
      return { status: 'Fatigued', color: '#f44336', icon: '⚠️' };
    } else if (daysLive >= 7 && performanceDrop >= 0.10) {
      return { status: 'Warning', color: '#ff9800', icon: '⚡' };
    } else {
      return { status: 'Fresh', color: '#4caf50', icon: '✅' };
    }
  }

  /**
   * Helper function to get decision recommendation color
   * @param {string} decision - Decision type (pause, keep, replace)
   */
  getDecisionColor(decision) {
    switch (decision?.toLowerCase()) {
      case 'pause':
        return '#f44336'; // Red
      case 'keep':
        return '#4caf50'; // Green
      case 'replace':
        return '#ff9800'; // Orange
      case 'monitor':
        return '#2196f3'; // Blue
      default:
        return '#9e9e9e';
    }
  }

  /**
   * Helper function to format currency
   * @param {number} amount - Amount in currency
   */
  formatCurrency(amount) {
    if (amount >= 100000) {
      return `₹${(amount / 100000).toFixed(1)}L`;
    }
    if (amount >= 1000) {
      return `₹${(amount / 1000).toFixed(1)}K`;
    }
    return `₹${amount?.toFixed(2) || 0}`;
  }

  /**
   * Helper function to get audience segment icon
   * @param {string} segment - Audience segment
   */
  getAudienceIcon(segment) {
    switch (segment?.toLowerCase()) {
      case 'working professionals':
        return '💼';
      case 'recent graduates':
        return '🎓';
      case 'career changers':
        return '🔄';
      case 'students':
        return '📚';
      default:
        return '👥';
    }
  }

  /**
   * Helper function to get placement icon
   * @param {string} placement - Ad placement
   */
  getPlacementIcon(placement) {
    switch (placement?.toLowerCase()) {
      case 'google search':
        return '🔍';
      case 'facebook ads':
        return '📘';
      case 'linkedin ads':
        return '💼';
      case 'youtube ads':
        return '📺';
      case 'instagram ads':
        return '📸';
      default:
        return '📢';
    }
  }

  /**
   * Calculate improvement potential
   * @param {Object} analysis - Analysis results
   */
  calculateImprovementPotential(analysis) {
    if (!analysis?.expected_impact) {
      // Default fallback values
      return {
        ctrImprovement: '25%',
        cpqlReduction: '20%',
        qualifiedLeadsIncrease: '30%',
        timeline: '30 days'
      };
    }

    return {
      ctrImprovement: analysis.expected_impact.ctr_improvement,
      cpqlReduction: analysis.expected_impact.cpql_reduction,
      qualifiedLeadsIncrease: analysis.expected_impact.qualified_leads_improvement,
      timeline: analysis.expected_impact.timeline
    };
  }

  /**
   * Process analysis results for frontend display
   * @param {Object} analysisData - Raw analysis data from backend
   */
  processAnalysisResults(analysisData) {
    if (!analysisData?.data) {
      return null;
    }

    const data = analysisData.data;
    
    return {
      performanceVariance: data.performance_variance || {},
      rootCauses: data.root_causes || [],
      campaignDecisions: data.campaign_decisions || {},
      fatigueDetection: data.fatigue_detection || [],
      expectedImpact: data.expected_impact || {},
      variantsCount: data.variants_count || 0,
      decisionsCount: data.decisions_count || 0,
      // Additional calculated metrics
      improvementPotential: this.calculateImprovementPotential(data),
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Create mock analysis results for demo purposes
   */
  createMockAnalysisResults() {
    return {
      success: true,
      message: "Analysis completed successfully",
      data: {
        performance_variance: {
          ctr_range: "0.7% to 3.8%",
          cpql_variance: "2-4x variation",
          qpi_average: 0.003,
          total_campaigns: 24
        },
        root_causes: [
          {
            name: "Copy-Intent Mismatch",
            description: "Low CTR with high impressions indicates copy doesn't match user intent",
            case_count: 8,
            evidence: [
              { metric: "avg_ctr", value: 0.012, benchmark: 0.025 },
              { metric: "impressions", value: 50000, note: "High visibility, low engagement" }
            ]
          },
          {
            name: "Weak Qualification Process",
            description: "Good CTR but high CPQL suggests weak lead qualification",
            case_count: 5,
            evidence: [
              { metric: "avg_cpql", value: 280, benchmark: 120 },
              { metric: "qualification_rate", value: 0.45, benchmark: 0.65 }
            ]
          }
        ],
        campaign_decisions: {
          pause_count: 6,
          keep_count: 12,
          monitor_count: 6
        },
        fatigue_detection: [
          {
            campaign: "Data Science Career Switch",
            days_live: 12,
            performance_drop: 0.25,
            original_ctr: 0.032,
            current_ctr: 0.024,
            status: "needs_rotation"
          }
        ],
        expected_impact: {
          ctr_improvement: "25%",
          cpql_reduction: "20%",
          timeline: "30 days",
          qualified_leads_improvement: "30%",
          cac_reduction: "18%"
        },
        variants_count: 45,
        decisions_count: 24
      }
    };
  }
}

// Export singleton instance
const adliftService = new AdLiftService();
export default adliftService;
