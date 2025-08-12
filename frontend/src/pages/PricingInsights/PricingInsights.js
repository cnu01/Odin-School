import React, { useState } from 'react';
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
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
} from 'recharts';

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

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
            Pricing Insights & Segment Optimization
          </Typography>
          <Typography variant="body2" color="text.secondary">
            PriceSense AI • Segment-Based Pricing • Plan Optimization by User Type
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
          <Button variant="contained" startIcon={<Psychology />}>
            Run AI Analysis
          </Button>
        </Box>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Course Pricing" />
          <Tab label="Segment Analysis" />
          <Tab label="Problems & Solutions" />
        </Tabs>
      </Box>

      {/* AI Insights Alert */}
      <Alert severity="info" icon={<Lightbulb />} sx={{ mb: 4 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
          AI Pricing Insights Summary
        </Typography>
        <Typography variant="body2">
          Market analysis suggests increasing Full Stack and Data Science course prices by 5-6% to optimize revenue. 
          AI & ML course is overpriced relative to demand - consider reducing by 10% to increase enrollment. 
          Product Management shows strong demand with room for 7% price increase.
        </Typography>
      </Alert>

      {/* Course Pricing Tab */}
      {tabValue === 0 && (
        <>
          {/* Course Cards */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {courseData.map((course) => (
              <Grid item xs={12} md={6} lg={3} key={course.id}>
                <CourseCard course={course} />
              </Grid>
            ))}
          </Grid>

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
                  <Tooltip />
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
                  <Tooltip cursor={{ strokeDasharray: '3 3' }} />
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
        </>
      )}

      {/* Segment Analysis Tab */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          {segmentData.map((segment, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    {segment.segment.includes('Metro') && <LocationOn sx={{ mr: 1, color: 'primary.main' }} />}
                    {segment.segment.includes('Mobile') && <PhoneAndroid sx={{ mr: 1, color: 'primary.main' }} />}
                    {segment.segment.includes('Working') && <WorkOutline sx={{ mr: 1, color: 'primary.main' }} />}
                    {!segment.segment.includes('Metro') && !segment.segment.includes('Mobile') && !segment.segment.includes('Working') && <Computer sx={{ mr: 1, color: 'primary.main' }} />}
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {segment.segment}
                    </Typography>
                  </Box>
                  
                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Users</Typography>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {segment.users.toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Avg Price</Typography>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        ₹{segment.avgPrice.toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Conversion Rate</Typography>
                      <Typography variant="h6" sx={{ fontWeight: 600, color: 'success.main' }}>
                        {segment.conversionRate}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">Preferred Plan</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {segment.preferredPlan}
                      </Typography>
                    </Grid>
                  </Grid>

                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                    Key Pain Points:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                    {segment.painPoints.map((pain, i) => (
                      <Chip key={i} label={pain} size="small" color="warning" variant="outlined" />
                    ))}
                  </Box>

                  <Alert severity="info">
                    <Typography variant="body2">
                      <strong>AI Recommendation:</strong> {segment.recommendation}
                    </Typography>
                  </Alert>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

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
    </Box>
  );
}

export default PricingInsights;
