import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Alert,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Button,
  IconButton,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  LinearProgress,
  Badge,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Info,
  Warning,
  CheckCircle,
  FilterList,
  Refresh,
  Assessment,
  AutoFixHigh,
  Timeline,
  DataUsage,
  Storage,
  CloudSync,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  FunnelChart,
  Funnel,
  Cell,
} from 'recharts';

// Enhanced unified analytics data from multiple sources
// 12 core reasons why decisions are slow/inconsistent (from PDF)
const decisionProblems = [
  "Data scattered across 7+ systems (CRM, GA4, ads, support, telephony, LMS)",
  "Lead-to-Enrollment conversion varies 2-4 percentage points between reports",
  "Weekly executive reviews take 3-5 hours of manual data gathering",
  "Budget allocation decisions lag 7-10 days after performance changes",
  "Different teams use different attribution models causing confusion",
  "Real-time data only available in some systems, others have 24h delays",
  "No unified KPI definitions - teams measure 'qualified lead' differently",
  "Manual Excel reports prone to human error and version conflicts",
  "Historical trend analysis requires pulling from multiple dashboards",
  "Cross-channel performance comparison impossible without manual work",
  "Missing context for anomalies - spikes/drops lack actionable insights",
  "No automated alerts for significant performance changes"
];

// Multi-source system integration status
const systemIntegration = {
  crm: { status: 'connected', lastSync: '2 min ago', health: 95 },
  ga4: { status: 'connected', lastSync: '15 min ago', health: 98 },
  adPlatforms: { status: 'connected', lastSync: '5 min ago', health: 92 },
  telephony: { status: 'connected', lastSync: '1 min ago', health: 97 },
  lms: { status: 'connected', lastSync: '30 min ago', health: 89 },
  support: { status: 'connected', lastSync: '10 min ago', health: 94 }
};

// AI-generated executive brief with anomalies and recommendations
const weeklyExecutiveBrief = {
  period: "Week of Jan 8-14, 2024",
  overallHealth: "Strong",
  keyAnomalies: [
    {
      type: "Alert",
      severity: "high",
      metric: "Instagram Ad CPL",
      change: "+127% (₹485 → ₹1,100)",
      cause: "iOS 14.5 attribution issues",
      recommendation: "Pause iOS-targeted campaigns, shift budget to Android segments",
      impact: "₹45K budget at risk"
    },
    {
      type: "Opportunity", 
      severity: "medium",
      metric: "Organic Search Conversion",
      change: "+34% vs last week",
      cause: "SEO content on 'Data Science careers' ranking higher",
      recommendation: "Double content production budget, create similar content for AI/ML",
      impact: "Potential 15% lead increase"
    },
    {
      type: "Risk",
      severity: "medium", 
      metric: "Call Connect Rate",
      change: "-18% in Tier-2 cities",
      cause: "Regional holiday period affecting availability",
      recommendation: "Adjust calling hours, increase WhatsApp outreach",
      impact: "89 leads pending follow-up"
    }
  ],
  doNextActions: [
    "Immediate: Pause underperforming Instagram iOS campaigns (saves ₹8K/day)",
    "This Week: Increase SEO content budget by 25% focusing on AI/ML keywords", 
    "Monitor: Tier-2 city calling patterns, implement regional holiday calendar"
  ]
};

// Mock data - in real app would come from unified API
const kpiData = [
  {
    title: 'Lead-to-Enrollment Rate',
    value: '18.5%',
    change: '+2.3%',
    trend: 'up',
    color: 'success',
    source: 'CRM + LMS Integration',
    confidence: 96,
  },
  {
    title: 'Total Leads (This Month)',
    value: '2,847',
    change: '+12.7%',
    trend: 'up',
    color: 'primary',
    source: 'GA4 + Ad Platforms',
    confidence: 98,
  },
  {
    title: 'Cost Per Qualified Lead',
    value: '₹485',
    change: '-8.1%',
    trend: 'down',
    color: 'success',
    source: 'Ad Spend + CRM Qualified',
    confidence: 94,
  },
  {
    title: 'Overall ROI',
    value: '3.2x',
    change: '+0.4x',
    trend: 'up',
    color: 'warning',
    source: 'Revenue - All Costs',
    confidence: 91,
  },
];

const funnelData = [
  { name: 'Website Visitors', value: 15420, fill: '#8884d8' },
  { name: 'Leads Generated', value: 2847, fill: '#82ca9d' },
  { name: 'Qualified Leads', value: 1893, fill: '#ffc658' },
  { name: 'Meeting Booked', value: 891, fill: '#ff7300' },
  { name: 'Enrolled', value: 527, fill: '#0088fe' },
];

const performanceData = [
  { month: 'Jan', leads: 2100, enrollments: 378, cpl: 520 },
  { month: 'Feb', leads: 2400, enrollments: 432, cpl: 480 },
  { month: 'Mar', leads: 2200, enrollments: 396, cpl: 510 },
  { month: 'Apr', leads: 2680, enrollments: 483, cpl: 450 },
  { month: 'May', leads: 2847, enrollments: 527, cpl: 485 },
];

const sourceData = [
  { source: 'Organic Search', leads: 890, percentage: 31.3 },
  { source: 'Social Media', leads: 654, percentage: 23.0 },
  { source: 'Influencers', leads: 568, percentage: 19.9 },
  { source: 'Paid Ads', leads: 487, percentage: 17.1 },
  { source: 'Referrals', leads: 248, percentage: 8.7 },
];

function Dashboard() {
  const [timeRange, setTimeRange] = useState('month');
  const [leadSource, setLeadSource] = useState('all');
  const [tabValue, setTabValue] = useState(0);

  const KPICard = ({ data }) => (
    <Card sx={{ height: '100%', position: 'relative', overflow: 'visible' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
            {data.title}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {data.trend === 'up' ? (
              <TrendingUp sx={{ color: 'success.main', fontSize: 20 }} />
            ) : (
              <TrendingDown sx={{ color: 'error.main', fontSize: 20 }} />
            )}
          </Box>
        </Box>
        <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
          {data.value}
        </Typography>
        <Chip
          label={data.change}
          size="small"
          color={data.trend === 'up' ? 'success' : 'error'}
          variant="outlined"
        />
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Source: {data.source}
          </Typography>
          <Chip
            label={`${data.confidence}% confidence`}
            size="small"
            color={data.confidence > 95 ? 'success' : data.confidence > 90 ? 'warning' : 'error'}
            variant="outlined"
          />
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      {/* Header with Controls */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
            OneTruth - Unified Analytics
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Single source of truth from CRM, GA4, Ads, Telephony, LMS & Support
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <MenuItem value="week">This Week</MenuItem>
              <MenuItem value="month">This Month</MenuItem>
              <MenuItem value="quarter">This Quarter</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel>Lead Source</InputLabel>
            <Select
              value={leadSource}
              label="Lead Source"
              onChange={(e) => setLeadSource(e.target.value)}
            >
              <MenuItem value="all">All Sources</MenuItem>
              <MenuItem value="organic">Organic</MenuItem>
              <MenuItem value="paid">Paid Ads</MenuItem>
              <MenuItem value="social">Social Media</MenuItem>
              <MenuItem value="influencer">Influencers</MenuItem>
            </Select>
          </FormControl>
          <IconButton>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {/* System Integration Status */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <DataUsage sx={{ color: 'primary.main', mr: 1 }} />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Multi-Source Data Integration Status
            </Typography>
          </Box>
          <Grid container spacing={2}>
            {Object.entries(systemIntegration).map(([system, data]) => (
              <Grid item xs={6} md={2} key={system}>
                <Box sx={{ textAlign: 'center', p: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                    <CloudSync sx={{ 
                      color: data.status === 'connected' ? 'success.main' : 'error.main',
                      fontSize: 20, mr: 0.5 
                    }} />
                    <Typography variant="body2" sx={{ fontWeight: 600, textTransform: 'uppercase' }}>
                      {system}
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={data.health} 
                    color={data.health > 95 ? 'success' : data.health > 90 ? 'warning' : 'error'}
                    sx={{ height: 6, borderRadius: 3, mb: 0.5 }}
                  />
                  <Typography variant="caption" color="text.secondary">
                    {data.lastSync} • {data.health}%
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Analytics Dashboard" />
          <Tab label="Executive Brief" />
          <Tab label="Decision Problems" />
        </Tabs>
      </Box>

      {/* Analytics Dashboard Tab */}
      {tabValue === 0 && (
        <>
          {/* KPI Scorecards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {kpiData.map((kpi, index) => (
          <Grid item xs={12} sm={6} lg={3} key={index}>
            <KPICard data={kpi} />
          </Grid>
        ))}
      </Grid>

      {/* Executive Brief */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Info sx={{ color: 'primary.main', mr: 1 }} />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              AI Executive Brief
            </Typography>
          </Box>
          
          <Alert severity="warning" sx={{ mb: 2 }}>
            <strong>Anomaly Detected:</strong> CPL from Creator 'TechGuruRaj' is 150% above average (₹1,215 vs ₹485). 
            Recommendation: Pause campaign and re-evaluate audience targeting.
          </Alert>
          
          <Alert severity="success" sx={{ mb: 2 }}>
            <strong>Opportunity Identified:</strong> Organic search conversions are 23% higher this month. 
            Recommendation: Increase SEO content budget by 15%.
          </Alert>
          
          <Alert severity="info">
            <strong>Next Best Action:</strong> 127 leads from 'Data Science Webinar' haven't been contacted. 
            Priority: Assign to top performers immediately.
          </Alert>
        </CardContent>
      </Card>

      {/* Main Charts Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Lead to Enrollment Funnel */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                Lead → Enrollment Funnel
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={funnelData} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="name" type="category" width={100} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#1976d2" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Trends */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                Performance Trends
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="leads"
                    stroke="#1976d2"
                    strokeWidth={3}
                    name="Leads"
                  />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="enrollments"
                    stroke="#ff9800"
                    strokeWidth={3}
                    name="Enrollments"
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="cpl"
                    stroke="#4caf50"
                    strokeWidth={3}
                    name="CPL (₹)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Lead Sources Breakdown */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
            Lead Sources Performance
          </Typography>
          <Grid container spacing={2}>
            {sourceData.map((source, index) => (
              <Grid item xs={12} sm={6} md={4} lg={2.4} key={index}>
                <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: 'grey.50' }}>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                    {source.leads}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {source.source}
                  </Typography>
                  <Chip
                    label={`${source.percentage}%`}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                </Paper>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
        </>
      )}

      {/* Executive Brief Tab */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Timeline sx={{ color: 'primary.main', mr: 1 }} />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    AI-Generated Executive Brief - {weeklyExecutiveBrief.period}
                  </Typography>
                  <Chip
                    label={`Overall Health: ${weeklyExecutiveBrief.overallHealth}`}
                    color="success"
                    variant="filled"
                    sx={{ ml: 2 }}
                  />
                </Box>

                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
                  Key Anomalies & Opportunities:
                </Typography>

                {weeklyExecutiveBrief.keyAnomalies.map((anomaly, index) => (
                  <Alert 
                    key={index}
                    severity={anomaly.severity === 'high' ? 'error' : anomaly.severity === 'medium' ? 'warning' : 'info'}
                    sx={{ mb: 2 }}
                  >
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      {anomaly.type}: {anomaly.metric}
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>Change:</strong> {anomaly.change}
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>Cause:</strong> {anomaly.cause}
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>Recommendation:</strong> {anomaly.recommendation}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Impact:</strong> {anomaly.impact}
                    </Typography>
                  </Alert>
                ))}

                <Divider sx={{ my: 3 }} />

                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
                  Do-Next Actions (Prioritized):
                </Typography>
                <List>
                  {weeklyExecutiveBrief.doNextActions.map((action, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <AutoFixHigh sx={{ color: 'success.main' }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={action}
                        primaryTypographyProps={{ fontWeight: 500 }}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Decision Problems Tab */}
      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                  12 Core Reasons Why Decisions Are Slow/Inconsistent
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Problems identified that lead to delayed and inconsistent business decisions:
                </Typography>
                <List>
                  {decisionProblems.map((problem, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <Assessment sx={{ color: 'error.main' }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={`${index + 1}. ${problem}`}
                        primaryTypographyProps={{ fontSize: '0.9rem' }}
                      />
                    </ListItem>
                  ))}
                </List>

                <Divider sx={{ my: 3 }} />

                <Alert severity="success">
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                    OneTruth Solution Impact:
                  </Typography>
                  <Typography variant="body2">
                    <strong>Target Metrics:</strong> Cut report prep by 80%; decisions within 48 hours; 10-15% ROI improvement on reallocated spend
                  </Typography>
                </Alert>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}

export default Dashboard;
