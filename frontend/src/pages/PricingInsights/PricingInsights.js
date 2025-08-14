import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Slider,
  Switch,
  FormControlLabel,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  LinearProgress,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Psychology,
  AttachMoney,
  School,
  People,
  Timer,
  Lightbulb,
  Assessment,
  AutoFixHigh,
  LocationOn,
  PhoneAndroid,
  Computer,
  WorkOutline,
  Refresh as RefreshIcon,
  Send as SendIcon,
  ContentCopy as ContentCopyIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
} from 'recharts';
import pricesenseService from '../../services/pricesenseService';

// Enhanced pricing data with segment analysis
const courseData = [
  {
    id: 1,
    name: 'Full Stack Development',
    currentPrice: 89999,
    suggestedPrice: 94999,
    enrollments: 342,
    revenue: 3078000,
    completionRate: 87,
    satisfaction: 4.6,
    demandScore: 95,
    competitorAvg: 92000,
    priceElasticity: 0.65,
  },
  {
    id: 2,
    name: 'Data Science Mastery',
    currentPrice: 79999,
    suggestedPrice: 84999,
    enrollments: 298,
    revenue: 2384000,
    completionRate: 89,
    satisfaction: 4.7,
    demandScore: 92,
    competitorAvg: 81000,
    priceElasticity: 0.72,
  },
  {
    id: 3,
    name: 'AI & Machine Learning',
    currentPrice: 99999,
    suggestedPrice: 89999,
    enrollments: 156,
    revenue: 1560000,
    completionRate: 82,
    satisfaction: 4.4,
    demandScore: 78,
    competitorAvg: 87000,
    priceElasticity: 0.89,
  },
  {
    id: 4,
    name: 'Product Management',
    currentPrice: 69999,
    suggestedPrice: 74999,
    enrollments: 189,
    revenue: 1323000,
    completionRate: 91,
    satisfaction: 4.8,
    demandScore: 88,
    competitorAvg: 72000,
    priceElasticity: 0.58,
  },
];

const demandTrendData = [
  { month: 'Jan', fullStack: 280, dataScience: 240, aiMl: 120, productMgmt: 160 },
  { month: 'Feb', fullStack: 310, dataScience: 270, aiMl: 135, productMgmt: 175 },
  { month: 'Mar', fullStack: 295, dataScience: 285, aiMl: 140, productMgmt: 180 },
  { month: 'Apr', fullStack: 340, dataScience: 300, aiMl: 150, productMgmt: 185 },
  { month: 'May', fullStack: 342, dataScience: 298, aiMl: 156, productMgmt: 189 },
];

const priceOptimizationScenarios = [
  {
    scenario: 'Conservative (+5%)',
    fullStack: { price: 94499, enrollments: 325, revenue: 3071000 },
    dataScience: { price: 83999, enrollments: 285, revenue: 2394000 },
    aiMl: { price: 94999, enrollments: 145, revenue: 1377000 },
  },
  {
    scenario: 'Aggressive (+10%)',
    fullStack: { price: 98999, enrollments: 310, revenue: 3069000 },
    dataScience: { price: 87999, enrollments: 275, revenue: 2420000 },
    aiMl: { price: 89999, enrollments: 156, revenue: 1404000 },
  },
  {
    scenario: 'Market Penetration (-5%)',
    fullStack: { price: 85499, enrollments: 365, revenue: 3121000 },
    dataScience: { price: 75999, enrollments: 320, revenue: 2432000 },
    aiMl: { price: 84999, enrollments: 168, revenue: 1428000 },
  },
];

// Segment-based pricing problems (12 key issues from PDF)
const pricingProblems = [
  "Geographic segments show 35% price sensitivity variation (Mumbai vs Tier-2 cities)",
  "Mobile users convert 40% less on higher-priced plans due to payment friction", 
  "Organic traffic has 2x higher willingness to pay vs paid traffic",
  "Scholarship messaging unclear - 68% don't understand eligibility criteria",
  "EMI options buried - only 23% of users see payment plans upfront",
  "Working professionals need different pricing than fresh graduates",
  "Course bundling confuses users - 45% abandon during plan selection",
  "Social proof missing on pricing page - no testimonials from similar backgrounds",
  "Comparison fatigue - 5+ plan options cause 28% drop-off",
  "Regional income disparities not reflected in pricing strategy",
  "Discount timing inconsistent - creates wait-and-see behavior",
  "No personalization based on previous course completions or engagement"
];

// AI-driven solutions for segment optimization (2 key solutions from PDF)
const aiSolutions = [
  {
    name: "Dynamic Segment-Based Pricing",
    description: "AI automatically adjusts plan presentation based on user segment (source, location, device, engagement)",
    features: [
      "Geographic price optimization (Metro vs Tier-2/3 pricing)",
      "Source-based messaging (Organic users see premium features, Paid users see value)",
      "Device-optimized checkout (Mobile gets simpler 2-step EMI, Desktop shows full comparison)",
      "Engagement-based recommendations (High-intent users see scholarships, explorers see trials)"
    ],
    impact: "8-12% enrollment increase, 15% refund reduction",
    effort: "Medium - requires ML model training",
    targetMetrics: "Target: 8-12% enrollments; ≤15% refund/default rate in 60 days"
  },
  {
    name: "AI Personalized Plan Messenger", 
    description: "Smart messaging system that crafts personalized plan recommendations and explanations per user",
    features: [
      "Background-aware recommendations (Engineering vs Non-tech backgrounds)",
      "Career goal alignment (Job switch vs skill upgrade vs fresh start)",
      "Financial situation messaging (EMI-first vs scholarship-focus vs premium)",
      "Success story matching (show testimonials from similar user profiles)"
    ],
    impact: "12-18% conversion increase, 25% user satisfaction improvement", 
    effort: "High - requires NLP and user profiling system",
    targetMetrics: "Target: 12-18% enrollments; ≤10% refund/default rate in 60 days"
  }
];

// Segment performance data
const segmentData = [
  {
    segment: "Metro Organic (High-Intent)",
    users: 2847,
    avgPrice: 94999,
    conversionRate: 24.3,
    preferredPlan: "Premium + Mentorship",
    painPoints: ["Time commitment", "ROI assurance"],
    recommendation: "Show outcome-based pricing + alumni network"
  },
  {
    segment: "Tier-2 Paid Traffic",
    users: 1567,
    avgPrice: 74999,
    conversionRate: 16.8,
    preferredPlan: "Standard + EMI",
    painPoints: ["High cost", "Job guarantee"],
    recommendation: "Emphasize EMI options + placement statistics"
  },
  {
    segment: "Mobile-First Users",
    users: 3245,
    avgPrice: 67999,
    conversionRate: 12.4,
    preferredPlan: "Basic + Support",
    painPoints: ["Complex checkout", "Payment options"],
    recommendation: "Simplify mobile checkout + UPI/wallet options"
  },
  {
    segment: "Working Professionals",
    users: 1890,
    avgPrice: 109999,
    conversionRate: 28.7,
    preferredPlan: "Executive Track",
    painPoints: ["Flexible timing", "Industry relevance"],
    recommendation: "Weekend batches + corporate case studies"
  }
];

function PricingInsights() {
  const [selectedCourse, setSelectedCourse] = useState('all');
  const [timeframe, setTimeframe] = useState('6months');
  const [priceSlider, setPriceSlider] = useState(89999);
  const [showPredictions, setShowPredictions] = useState(true);
  const [tabValue, setTabValue] = useState(0);
  
  // New state for backend integration
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [problemAnalysis, setProblemAnalysis] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  // Optimization dialog state
  const [optimizationDialog, setOptimizationDialog] = useState({ open: false });
  const [optimizationResults, setOptimizationResults] = useState(null);
  const [optimizationLoading, setOptimizationLoading] = useState(false);

  // Message generation state
  const [messageDialog, setMessageDialog] = useState({ open: false, segment: null, message: '' });
  const [messageLoading, setMessageLoading] = useState(false);

  // Define loadInitialData function outside useEffect so it can be called by handleRefresh
  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Add delay to prevent rapid duplicate requests
      await new Promise(resolve => setTimeout(resolve, 100));

      // Load all required data in parallel
      const [dashboardRes, analyticsRes, problemRes, recommendationsRes] = await Promise.all([
        pricesenseService.getDashboardData(),
        pricesenseService.getAnalyticsSummary(500),
        pricesenseService.getProblemAnalysis(),
        pricesenseService.getRecommendations(10, 60.0)
      ]);

      setDashboardData(dashboardRes);
      setAnalytics(analyticsRes);
      setProblemAnalysis(problemRes);
      setRecommendations(recommendationsRes.recommendations || []);

    } catch (err) {
      setError(err.message || 'Failed to load pricing data');
      console.error('Error loading pricing data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const abortController = new AbortController();
    
    const loadWithAbortController = async () => {
      if (abortController.signal.aborted) return;
      await loadInitialData();
    };

    loadWithAbortController();
    
    // Cleanup function to prevent race conditions
    return () => {
      abortController.abort();
    };
  }, []);

  const handleRefresh = () => {
    loadInitialData();
  };

  const runOptimization = async () => {
    try {
      setOptimizationLoading(true);
      
      // Create test segments for optimization
      const testSegments = [
        pricesenseService.createTestSegment(),
        { ...pricesenseService.createTestSegment(), geography_score: 0.5, source: 'paid' },
        { ...pricesenseService.createTestSegment(), device_score: 0.7, device: 'mobile' }
      ];

      const results = await pricesenseService.optimizePlanSelection(testSegments);
      setOptimizationResults(results);
      setOptimizationDialog({ open: true });
      showSnackbar('Optimization completed successfully', 'success');
      
    } catch (err) {
      showSnackbar('Optimization failed: ' + err.message, 'error');
    } finally {
      setOptimizationLoading(false);
    }
  };

  const generatePricingMessage = async (segment) => {
    try {
      setMessageLoading(true);
      const messageData = await pricesenseService.personalizeMessage(segment);
      setMessageDialog({
        open: true,
        segment,
        message: messageData.message || 'Pricing message generated successfully'
      });
    } catch (err) {
      showSnackbar('Failed to generate message', 'error');
    } finally {
      setMessageLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    showSnackbar('Copied to clipboard', 'success');
  };

  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const closeSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const getPriceTrend = (current, suggested) => {
    if (suggested > current) return { icon: <TrendingUp />, color: 'success.main', text: 'Increase' };
    if (suggested < current) return { icon: <TrendingDown />, color: 'error.main', text: 'Decrease' };
    return { icon: <AttachMoney />, color: 'info.main', text: 'Maintain' };
  };

  const CourseCard = ({ course }) => {
    const trend = getPriceTrend(course.currentPrice, course.suggestedPrice);
    const priceDiff = course.suggestedPrice - course.currentPrice;
    const priceDiffPercent = ((priceDiff / course.currentPrice) * 100).toFixed(1);

    return (
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1rem' }}>
              {course.name}
            </Typography>
            <Chip
              icon={trend.icon}
              label={trend.text}
              color={priceDiff > 0 ? 'success' : priceDiff < 0 ? 'error' : 'default'}
              size="small"
              variant="filled"
            />
          </Box>

          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">Current Price</Typography>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                ₹{course.currentPrice.toLocaleString()}
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">AI Suggested</Typography>
              <Typography variant="h6" sx={{ fontWeight: 600, color: trend.color }}>
                ₹{course.suggestedPrice.toLocaleString()}
              </Typography>
            </Grid>
          </Grid>

          <Alert severity={priceDiff > 0 ? 'success' : priceDiff < 0 ? 'warning' : 'info'} sx={{ mb: 2 }}>
            <Typography variant="body2">
              {priceDiff > 0 ? '+' : ''}₹{Math.abs(priceDiff).toLocaleString()} ({priceDiffPercent}%) change recommended
            </Typography>
          </Alert>

          <Grid container spacing={1} sx={{ mb: 2 }}>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Demand Score</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main' }}>
                {course.demandScore}/100
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Completion Rate</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {course.completionRate}%
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Satisfaction</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {course.satisfaction}/5.0
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">Elasticity</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {course.priceElasticity}
              </Typography>
            </Grid>
          </Grid>

          <Button variant="outlined" size="small" fullWidth>
            View Detailed Analysis
          </Button>
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Alert severity="error" action={
          <Button color="inherit" size="small" onClick={handleRefresh}>
            Retry
          </Button>
        }>
          {error}
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
            PriceSense AI - Pricing Optimization
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Segment-Based Pricing • ML-Powered Plan Optimization • Dynamic Message Generation
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel>Timeframe</InputLabel>
            <Select
              value={timeframe}
              label="Timeframe"
              onChange={(e) => setTimeframe(e.target.value)}
            >
              <MenuItem value="3months">3 Months</MenuItem>
              <MenuItem value="6months">6 Months</MenuItem>
              <MenuItem value="1year">1 Year</MenuItem>
            </Select>
          </FormControl>
          <Button 
            variant="contained" 
            startIcon={optimizationLoading ? <CircularProgress size={20} /> : <Psychology />}
            onClick={runOptimization}
            disabled={optimizationLoading}
          >
            Run AI Optimization
          </Button>
          <IconButton onClick={handleRefresh} title="Refresh Data">
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card sx={{ 
            cursor: 'pointer',
            '&:hover': { transform: 'translateY(-2px)', boxShadow: 3 }
          }}
          onClick={() => setTabValue(2)} // Navigate to Problems tab
          >
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Problems Identified
              </Typography>
              <Typography variant="h4" color="primary">
                {problemAnalysis?.diagnosed_problems?.length || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Click to view details
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ 
            cursor: 'pointer',
            '&:hover': { transform: 'translateY(-2px)', boxShadow: 3 }
          }}
          onClick={() => setTabValue(1)} // Navigate to Segment Analysis tab
          >
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Segments Analyzed
              </Typography>
              <Typography variant="h4" color="primary">
                {problemAnalysis?.segment_challenges?.length || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Click to view analysis
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg Optimization Score
              </Typography>
              <Typography variant="h4" color="primary">
                {analytics?.optimization?.avg_score || 'N/A'}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                ML confidence
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Revenue Opportunity
              </Typography>
              <Typography variant="h4" color="success.main">
                {problemAnalysis?.overall_impact?.revenue_opportunity?.split(' ')[0] || '₹15L+'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Annual potential
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Pricing Analytics" icon={<AnalyticsIcon />} />
          <Tab label="Segment Optimization" icon={<SettingsIcon />} />
          <Tab label="Problem Analysis" icon={<Assessment />} />
          <Tab label="Recommendations" icon={<AutoFixHigh />} />
        </Tabs>
      </Box>

      {/* AI Insights Alert - Now with real data */}
      <Alert severity="info" icon={<Lightbulb />} sx={{ mb: 4 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
          AI Pricing Insights Summary
        </Typography>
        <Typography variant="body2">
          {problemAnalysis?.diagnosed_problems?.[0]?.impact || 
           'AI analysis shows significant revenue optimization opportunities across different user segments and pricing tiers.'}
        </Typography>
      </Alert>

      {/* Pricing Analytics Tab */}
      {tabValue === 0 && (
        <>
          {/* Real Analytics Cards */}
          <PricingAnalyticsView 
            analytics={analytics}
            courseData={courseData}
            onGenerateMessage={generatePricingMessage}
            messageLoading={messageLoading}
          />
        </>
      )}

      {/* Segment Analysis Tab */}
      {tabValue === 1 && (
        <SegmentAnalysisView problemAnalysis={problemAnalysis} analytics={analytics} />
      )}

      {/* Problems & Solutions Tab */}
      {tabValue === 2 && (
        <ProblemAnalysisView problemAnalysis={problemAnalysis} />
      )}

      {/* Charts Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Demand Trends */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                Course Demand Trends
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={demandTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <RechartsTooltip />
                  <Line type="monotone" dataKey="fullStack" stroke="#1976d2" strokeWidth={2} name="Full Stack" />
                  <Line type="monotone" dataKey="dataScience" stroke="#ff9800" strokeWidth={2} name="Data Science" />
                  <Line type="monotone" dataKey="aiMl" stroke="#4caf50" strokeWidth={2} name="AI & ML" />
                  <Line type="monotone" dataKey="productMgmt" stroke="#9c27b0" strokeWidth={2} name="Product Mgmt" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Price vs Demand Scatter */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                Price vs Demand Analysis
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <ScatterChart data={courseData}>
                  <CartesianGrid />
                  <XAxis type="number" dataKey="currentPrice" name="Price" />
                  <YAxis type="number" dataKey="demandScore" name="Demand" />
                  <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} />
                  <Scatter dataKey="demandScore" fill="#1976d2" />
                </ScatterChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Price Optimization Scenarios */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
            Price Optimization Scenarios
          </Typography>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow sx={{ backgroundColor: 'grey.50' }}>
                  <TableCell>Scenario</TableCell>
                  <TableCell align="center">Full Stack Development</TableCell>
                  <TableCell align="center">Data Science Mastery</TableCell>
                  <TableCell align="center">AI & Machine Learning</TableCell>
                  <TableCell align="center">Total Revenue Impact</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {priceOptimizationScenarios.map((scenario, index) => {
                  const totalRevenue = scenario.fullStack.revenue + scenario.dataScience.revenue + scenario.aiMl.revenue;
                  const currentTotal = courseData.reduce((sum, course) => sum + course.revenue, 0);
                  const revenueChange = ((totalRevenue - currentTotal) / currentTotal * 100).toFixed(1);
                  
                  return (
                    <TableRow key={index}>
                      <TableCell sx={{ fontWeight: 600 }}>{scenario.scenario}</TableCell>
                      <TableCell align="center">
                        <Typography variant="body2">₹{scenario.fullStack.price.toLocaleString()}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {scenario.fullStack.enrollments} enrollments
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Typography variant="body2">₹{scenario.dataScience.price.toLocaleString()}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {scenario.dataScience.enrollments} enrollments
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Typography variant="body2">₹{scenario.aiMl.price.toLocaleString()}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {scenario.aiMl.enrollments} enrollments
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            fontWeight: 600,
                            color: parseFloat(revenueChange) > 0 ? 'success.main' : 'error.main'
                          }}
                        >
                          {revenueChange > 0 ? '+' : ''}{revenueChange}%
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          ₹{(totalRevenue / 1000000).toFixed(1)}M
                        </Typography>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Interactive Price Simulator */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
            Interactive Price Simulator
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Full Stack Development Course Price
                </Typography>
                <Slider
                  value={priceSlider}
                  onChange={(e, newValue) => setPriceSlider(newValue)}
                  min={70000}
                  max={120000}
                  step={1000}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `₹${value.toLocaleString()}`}
                />
                <Typography variant="body2" color="text.secondary">
                  Current: ₹{priceSlider.toLocaleString()}
                </Typography>
              </Box>
              <FormControlLabel
                control={
                  <Switch
                    checked={showPredictions}
                    onChange={(e) => setShowPredictions(e.target.checked)}
                  />
                }
                label="Show AI Predictions"
              />
            </Grid>
            <Grid item xs={12} md={8}>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <School sx={{ fontSize: 32, color: 'primary.main', mb: 1 }} />
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {Math.round(342 * (1 - ((priceSlider - 89999) / 89999) * 0.65))}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Predicted Enrollments
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={4}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <AttachMoney sx={{ fontSize: 32, color: 'success.main', mb: 1 }} />
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      ₹{((priceSlider * Math.round(342 * (1 - ((priceSlider - 89999) / 89999) * 0.65))) / 1000000).toFixed(1)}M
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Predicted Revenue
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={4}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <People sx={{ fontSize: 32, color: 'warning.main', mb: 1 }} />
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {Math.round(95 - ((priceSlider - 89999) / 89999) * 10)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Demand Score
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Problems & Solutions Tab */}
      {tabValue === 2 && (
        <Grid container spacing={3}>
          {/* 12 Problem Diagnoses */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                  12 Key Problems - Plan Selection Not Optimized by Segment
                </Typography>
                <List>
                  {pricingProblems.map((problem, index) => (
                    <ListItem key={index} sx={{ pl: 0 }}>
                      <ListItemIcon>
                        <Assessment sx={{ color: 'error.main', fontSize: 20 }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={`${index + 1}. ${problem}`}
                        primaryTypographyProps={{ fontSize: '0.875rem' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* 2 AI Solutions */}
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {aiSolutions.map((solution, index) => (
                <Card key={index}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <AutoFixHigh sx={{ color: 'success.main', mr: 1 }} />
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        AI Solution {index + 1}: {solution.name}
                      </Typography>
                    </Box>
                    
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {solution.description}
                    </Typography>

                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                      Key Features:
                    </Typography>
                    <List dense>
                      {solution.features.map((feature, i) => (
                        <ListItem key={i} sx={{ pl: 2 }}>
                          <ListItemText
                            primary={`• ${feature}`}
                            primaryTypographyProps={{ fontSize: '0.8rem' }}
                          />
                        </ListItem>
                      ))}
                    </List>

                    <Divider sx={{ my: 1 }} />
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">
                        <strong>Impact:</strong> {solution.impact}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">
                        <strong>Effort:</strong> {solution.effort}
                      </Typography>
                    </Box>
                    
                    <Alert severity="success" sx={{ mt: 2 }}>
                      <Typography variant="body2">
                        <strong>Success Metrics:</strong> {solution.targetMetrics}
                      </Typography>
                    </Alert>
                  </CardContent>
                </Card>
              ))}
            </Box>
          </Grid>
        </Grid>
      )}

      {/* Optimization Results Dialog */}
      <Dialog 
        open={optimizationDialog.open} 
        onClose={() => setOptimizationDialog({ open: false })}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <Psychology />
            Pricing Optimization Results
          </Box>
        </DialogTitle>
        <DialogContent>
          {optimizationResults && (
            <OptimizationResultsView results={optimizationResults} />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOptimizationDialog({ open: false })}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Message Generation Dialog */}
      <Dialog 
        open={messageDialog.open} 
        onClose={() => setMessageDialog({ open: false, segment: null, message: '' })}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <SendIcon />
            Generated Pricing Message
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              AI-generated personalized pricing message:
            </Typography>
            <TextField
              multiline
              rows={6}
              value={messageDialog.message}
              onChange={(e) => setMessageDialog(prev => ({ ...prev, message: e.target.value }))}
              fullWidth
              variant="outlined"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMessageDialog({ open: false, segment: null, message: '' })}>
            Close
          </Button>
          <Button
            variant="contained"
            startIcon={<ContentCopyIcon />}
            onClick={() => copyToClipboard(messageDialog.message)}
          >
            Copy Message
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={closeSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={closeSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

// Pricing Analytics Component
const PricingAnalyticsView = ({ analytics, courseData, onGenerateMessage, messageLoading }) => {
  return (
    <>
      {/* Course Cards with real data integration */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {courseData.map((course) => (
          <Grid item xs={12} md={6} lg={3} key={course.id}>
            <CourseCardEnhanced 
              course={course} 
              analytics={analytics}
              onGenerateMessage={onGenerateMessage}
              messageLoading={messageLoading}
            />
          </Grid>
        ))}
      </Grid>
    </>
  );
};

// Enhanced Course Card Component
const CourseCardEnhanced = ({ course, analytics, onGenerateMessage, messageLoading }) => {
  const trend = getPriceTrend(course.currentPrice, course.suggestedPrice);
  const priceDiff = course.suggestedPrice - course.currentPrice;
  const priceDiffPercent = ((priceDiff / course.currentPrice) * 100).toFixed(1);

  const handleGenerateMessage = () => {
    const segment = pricesenseService.createTestSegment();
    segment.plan_total_amount = course.currentPrice;
    onGenerateMessage(segment);
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1rem' }}>
            {course.name}
          </Typography>
          <Chip
            icon={trend.icon}
            label={trend.text}
            color={priceDiff > 0 ? 'success' : priceDiff < 0 ? 'error' : 'default'}
            size="small"
            variant="filled"
          />
        </Box>

        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">Current Price</Typography>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              ₹{course.currentPrice.toLocaleString()}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">AI Suggested</Typography>
            <Typography variant="h6" sx={{ fontWeight: 600, color: trend.color }}>
              ₹{course.suggestedPrice.toLocaleString()}
            </Typography>
          </Grid>
        </Grid>

        <Alert severity={priceDiff > 0 ? 'success' : priceDiff < 0 ? 'warning' : 'info'} sx={{ mb: 2 }}>
          <Typography variant="body2">
            {priceDiff > 0 ? '+' : ''}₹{Math.abs(priceDiff).toLocaleString()} ({priceDiffPercent}%) change recommended
          </Typography>
        </Alert>

        <Grid container spacing={1} sx={{ mb: 2 }}>
          <Grid item xs={6}>
            <Typography variant="caption" color="text.secondary">Demand Score</Typography>
            <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main' }}>
              {course.demandScore}/100
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="caption" color="text.secondary">Completion Rate</Typography>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              {course.completionRate}%
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="caption" color="text.secondary">Satisfaction</Typography>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              {course.satisfaction}/5.0
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="caption" color="text.secondary">Elasticity</Typography>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              {course.priceElasticity}
            </Typography>
          </Grid>
        </Grid>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" size="small" fullWidth>
            View Analysis
          </Button>
          <Button 
            variant="contained" 
            size="small" 
            onClick={handleGenerateMessage}
            disabled={messageLoading}
            startIcon={messageLoading ? <CircularProgress size={16} /> : <SendIcon />}
          >
            Message
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

// Segment Optimization Component
const SegmentOptimizationView = ({ recommendations, analytics, onOptimize, optimizationLoading }) => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Segment Optimization Recommendations
              </Typography>
              <Button
                variant="contained"
                startIcon={optimizationLoading ? <CircularProgress size={20} /> : <Psychology />}
                onClick={onOptimize}
                disabled={optimizationLoading}
              >
                Run Optimization
              </Button>
            </Box>
            
            <Grid container spacing={2}>
              {recommendations.map((rec, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {rec.user_id || `Segment ${index + 1}`}
                      </Typography>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="textSecondary">
                          Optimization Score: <strong>{rec.optimization_score}%</strong>
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={rec.optimization_score}
                          sx={{ mt: 1 }}
                        />
                      </Box>
                      <Typography variant="body2" gutterBottom>
                        <strong>Suggested Plan:</strong> {rec.suggested_plan}
                      </Typography>
                      <Typography variant="body2" gutterBottom>
                        <strong>Segment:</strong> {rec.segment}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Risk Level:</strong> {rec.risk_level}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

// Segment Analysis Component
const SegmentAnalysisView = ({ problemAnalysis, analytics }) => {
  if (!problemAnalysis?.segment_challenges) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Loading segment analysis...
        </Typography>
      </Box>
    );
  }

  return (
    <Grid container spacing={3}>
      {/* Segment Challenges from Problem Analysis */}
      <Grid item xs={12}>
        <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
          Segment Analysis & Challenges
        </Typography>
      </Grid>
      
      {problemAnalysis.segment_challenges.map((challenge, index) => (
        <Grid item xs={12} md={6} key={index}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {pricesenseService.getSegmentIcon(challenge.segment_type)} {challenge.segment_name}
                </Typography>
              </Box>
              
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {challenge.description}
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Conversion Impact
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
                  {challenge.conversion_impact}
                </Typography>
              </Box>

              {challenge.characteristics && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Key Characteristics
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {challenge.characteristics.map((char, i) => (
                      <Chip 
                        key={i} 
                        label={char.replace(/_/g, ' ')} 
                        size="small" 
                        variant="outlined"
                        color="primary"
                      />
                    ))}
                  </Box>
                </Box>
              )}

              {challenge.supporting_metrics && (
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Volume %
                    </Typography>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {challenge.supporting_metrics.volume_percentage?.toFixed(1)}%
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Avg Revenue
                    </Typography>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {pricesenseService.formatCurrency(challenge.supporting_metrics.avg_revenue_per_user)}
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                      Lifetime Value
                    </Typography>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: 'success.main' }}>
                      {pricesenseService.formatCurrency(challenge.supporting_metrics.lifetime_value)}
                    </Typography>
                  </Grid>
                </Grid>
              )}
            </CardContent>
          </Card>
        </Grid>
      ))}

      {/* Analytics Summary if available */}
      {analytics && (
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Segment Performance Analytics
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="primary" sx={{ fontWeight: 600 }}>
                      {analytics.segment_performance?.length || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Active Segments
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="success.main" sx={{ fontWeight: 600 }}>
                      {(analytics.conversion_metrics?.overall_conversion_rate * 100)?.toFixed(1) || '18.4'}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Avg Conversion Rate
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="warning.main" sx={{ fontWeight: 600 }}>
                      {pricesenseService.formatCurrency(analytics.revenue_analysis?.customer_lifetime_value || 67500)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Avg Lifetime Value
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      )}
    </Grid>
  );
};

// Problem Analysis Component
const ProblemAnalysisView = ({ problemAnalysis }) => {
  if (!problemAnalysis) {
    return <Typography>No problem analysis data available</Typography>;
  }

  return (
    <Grid container spacing={3}>
      {/* Diagnosed Problems */}
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>
          Identified Problems
        </Typography>
        {problemAnalysis.diagnosed_problems?.map((problem, index) => (
          <Card key={problem.problem_id || index} sx={{ mb: 2 }}>
            <CardContent>
              <Box display="flex" justifyContent="between" alignItems="start" mb={2}>
                <Typography variant="h6" color="error">
                  {problem.title}
                </Typography>
                <Chip label="Action Required" color="error" size="small" />
              </Box>
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>Symptom:</strong> {problem.symptom}
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>Root Cause:</strong> {problem.root_cause}
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>Impact:</strong> {problem.impact}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                <strong>Evidence:</strong> {problem.evidence}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Grid>

      {/* Segment Challenges */}
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>
          Segment Challenges
        </Typography>
        <Grid container spacing={2}>
          {problemAnalysis.segment_challenges?.map((challenge, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {pricesenseService.getSegmentIcon(challenge.segment_type)} {challenge.segment_name}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    {challenge.description}
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                    {challenge.characteristics?.map((char, i) => (
                      <Chip key={i} label={char} size="small" variant="outlined" />
                    ))}
                  </Box>
                  <Typography variant="body2" color="primary">
                    <strong>Impact:</strong> {challenge.conversion_impact}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Grid>

      {/* Overall Impact */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Optimization Opportunity
            </Typography>
            <Grid container spacing={2}>
              {Object.entries(problemAnalysis.overall_impact || {}).map(([key, value]) => (
                <Grid item xs={12} md={6} key={key}>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </Typography>
                  <Typography variant="h6" color="primary">
                    {value}
                  </Typography>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

// Recommendations Component
const RecommendationsView = ({ recommendations, onGenerateMessage, messageLoading }) => {
  return (
    <Grid container spacing={3}>
      {recommendations.map((rec, index) => (
        <Grid item xs={12} md={6} key={index}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Recommendation #{index + 1}
                </Typography>
                <Chip 
                  label={pricesenseService.formatOptimizationScore(rec.optimization_score).level}
                  color={pricesenseService.formatOptimizationScore(rec.optimization_score).badge}
                  size="small"
                />
              </Box>
              
              <Typography variant="body2" sx={{ mb: 2 }}>
                <strong>Optimization Score:</strong> {rec.optimization_score}%
              </Typography>
              
              <LinearProgress
                variant="determinate"
                value={rec.optimization_score}
                sx={{ mb: 2 }}
              />
              
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>Suggested Plan:</strong> {rec.suggested_plan}
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>Segment:</strong> {rec.segment}
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                <strong>Messaging:</strong> {rec.messaging}
              </Typography>
              
              <Button
                variant="contained"
                size="small"
                startIcon={messageLoading ? <CircularProgress size={16} /> : <SendIcon />}
                onClick={() => {
                  const segment = pricesenseService.createTestSegment();
                  onGenerateMessage(segment);
                }}
                disabled={messageLoading}
                fullWidth
              >
                Generate Message
              </Button>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

// Optimization Results Component
const OptimizationResultsView = ({ results }) => {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Optimization Results: {results.total_processed} segments analyzed
      </Typography>
      <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
        Average Optimization Score: {results.avg_optimization_score}%
      </Typography>
      
      <Grid container spacing={2}>
        {results.results?.map((result, index) => (
          <Grid item xs={12} md={6} key={index}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Segment {index + 1}
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Optimization Score:</strong> {result.prediction?.optimization_score}%
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Segment Type:</strong> {result.insights?.segment}
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Primary Factors:</strong> {result.insights?.primary_factors?.join(', ')}
                </Typography>
                <Typography variant="body2">
                  <strong>Suggested Plan:</strong> {result.recommendations?.suggested_plan}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

// Helper function
const getPriceTrend = (current, suggested) => {
  if (suggested > current) return { icon: <TrendingUp />, color: 'success.main', text: 'Increase' };
  if (suggested < current) return { icon: <TrendingDown />, color: 'error.main', text: 'Decrease' };
  return { icon: <AttachMoney />, color: 'info.main', text: 'Maintain' };
};

export default PricingInsights;
