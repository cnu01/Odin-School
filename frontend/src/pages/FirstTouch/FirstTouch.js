import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  LinearProgress,
  Tooltip,
  Badge,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Snackbar
} from '@mui/material';
import {
  Phone as PhoneIcon,
  Psychology as PsychologyIcon,
  TrendingUp as TrendingUpIcon,
  Analytics as AnalyticsIcon,
  Speed as SpeedIcon,
  Assignment as AssignmentIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon,
  LocationOn as LocationIcon,
  Devices as DevicesIcon,
  Star as StarIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Timer as TimerIcon
} from '@mui/icons-material';
import firsttouchService from '../../services/firsttouchService';

// Tab panel component
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`firsttouch-tabpanel-${index}`}
      aria-labelledby={`firsttouch-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function FirstTouch() {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [leads, setLeads] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [problemAnalysis, setProblemAnalysis] = useState(null);
  const [optimizationDialog, setOptimizationDialog] = useState({ open: false, lead: null });
  const [optimizationResult, setOptimizationResult] = useState(null);
  const [optimizationLoading, setOptimizationLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  // Define loadInitialData function that can be used throughout the component
  const loadInitialData = async () => {
    try {
      setLoading(true);
      
      // Load problem analysis and analytics
      const [problemRes, analyticsRes] = await Promise.all([
        firsttouchService.getProblemAnalysis(),
        firsttouchService.getCallAnalytics({
          date_range: [getDateDaysAgo(7), getCurrentDate()],
          filters: {},
          metrics: ['connect_rate', 'qualification_rate', 'conversion_rate']
        })
      ]);

      setProblemAnalysis(problemRes);
      setAnalytics(analyticsRes);
      
      // Generate sample leads for demo
      generateSampleLeads();
      
    } catch (error) {
      console.error('Error loading FirstTouch data:', error);
      showSnackbar('Error loading data. Using demo data.', 'warning');
      generateSampleLeads();
    } finally {
      setLoading(false);
    }
  };

  // Load data on component mount with race condition protection
  useEffect(() => {
    const abortController = new AbortController();
    
    const loadWithDelay = async () => {
      // Add delay to prevent rapid duplicate requests
      await new Promise(resolve => setTimeout(resolve, 100));
      
      if (!abortController.signal.aborted) {
        await loadInitialData();
      }
    };

    loadWithDelay();
    
    // Cleanup function to prevent race conditions
    return () => {
      abortController.abort();
    };
  }, []);

  const generateSampleLeads = () => {
    const sampleLeads = [
      {
        ...firsttouchService.createTestLead(),
        name: 'Priya Sharma',
        email: 'priya.sharma@email.com',
        phone: '+91-9876543210',
        source: 'website',
        intent_type: 'demo_request',
        urgency_level: 'high',
        time_since_inquiry_minutes: 5,
        lead_engagement_score: 0.92
      },
      {
        ...firsttouchService.createTestLead(),
        name: 'Rajesh Kumar',
        email: 'rajesh.k@email.com', 
        phone: '+91-9876543211',
        source: 'social',
        intent_type: 'course_inquiry',
        urgency_level: 'medium',
        time_since_inquiry_minutes: 15,
        lead_engagement_score: 0.78
      },
      {
        ...firsttouchService.createTestLead(),
        name: 'Anita Desai',
        email: 'anita.desai@email.com',
        phone: '+91-9876543212',
        source: 'referral',
        intent_type: 'pricing',
        urgency_level: 'medium',
        time_since_inquiry_minutes: 45,
        lead_engagement_score: 0.85
      }
    ];
    setLeads(sampleLeads);
  };

  const optimizeLead = async (lead) => {
    try {
      setOptimizationLoading(true);
      setOptimizationDialog({ open: true, lead });
      
      const result = await firsttouchService.optimizeCallTiming(lead);
      setOptimizationResult(result);
      
    } catch (error) {
      console.error('Error optimizing lead:', error);
      showSnackbar('Error optimizing call timing', 'error');
    } finally {
      setOptimizationLoading(false);
    }
  };

  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const getCurrentDate = () => {
    return new Date().toISOString().split('T')[0];
  };

  const getDateDaysAgo = (days) => {
    const date = new Date();
    date.setDate(date.getDate() - days);
    return date.toISOString().split('T')[0];
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
            FirstTouch AI - Call Optimization
          </Typography>
          <Typography variant="body2" color="text.secondary">
            AI-powered call timing optimization and script recommendations
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadInitialData}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => generateSampleLeads()}
          >
            Add Test Lead
          </Button>
        </Box>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Problems Identified
              </Typography>
              <Typography variant="h4" color="primary">
                {problemAnalysis?.problems?.length || 3}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Speed-to-lead issues
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Connect Rate
              </Typography>
              <Typography variant="h4" color="success.main">
                {analytics ? `${(analytics.connect_rate * 100).toFixed(1)}%` : '68.2%'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Current performance
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg Response Time
              </Typography>
              <Typography variant="h4" color="warning.main">
                {analytics ? `${analytics.avg_time_to_contact?.toFixed(1)}min` : '127.5min'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Target: &lt;15 min
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
                ₹219L+
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Annual optimization
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* AI Insights Alert */}
      <Alert severity="info" icon={<PsychologyIcon />} sx={{ mb: 4 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
          AI Insights Summary
        </Typography>
        <Typography variant="body2">
          {problemAnalysis?.problems?.[0]?.impact || 
           'Speed-to-lead optimization can improve conversion rates by 1.2x. Leads contacted within 15 minutes show significantly higher connect rates.'}
        </Typography>
      </Alert>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Lead Priority Queue" />
          <Tab label="Performance Analytics" />
          <Tab label="Problem Analysis" />
          <Tab label="Agent Interface" />
        </Tabs>
      </Box>

      {/* Lead Priority Queue Tab */}
      <TabPanel value={tabValue} index={0}>
        <LeadPriorityQueue 
          leads={leads}
          onOptimizeLead={optimizeLead}
        />
      </TabPanel>

      {/* Performance Analytics Tab */}
      <TabPanel value={tabValue} index={1}>
        <PerformanceAnalytics analytics={analytics} />
      </TabPanel>

      {/* Problem Analysis Tab */}
      <TabPanel value={tabValue} index={2}>
        <ProblemAnalysisView problemAnalysis={problemAnalysis} />
      </TabPanel>

      {/* Agent Interface Tab */}
      <TabPanel value={tabValue} index={3}>
        <AgentInterface leads={leads} onOptimizeLead={optimizeLead} />
      </TabPanel>

      {/* Optimization Dialog */}
      <Dialog 
        open={optimizationDialog.open} 
        onClose={() => setOptimizationDialog({ open: false })}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <PsychologyIcon />
            Call Optimization Results
          </Box>
        </DialogTitle>
        <DialogContent>
          {optimizationLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : optimizationResult ? (
            <OptimizationResults result={optimizationResult} lead={optimizationDialog.lead} />
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOptimizationDialog({ open: false })}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
}

// Lead Priority Queue Component
const LeadPriorityQueue = ({ leads, onOptimizeLead }) => {
  return (
    <Grid container spacing={3}>
      {leads.map((lead, index) => (
        <Grid item xs={12} md={6} lg={4} key={lead.lead_id}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1rem' }}>
                    {lead.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {lead.email}
                  </Typography>
                </Box>
                <Chip 
                  label={firsttouchService.getLeadTemperature(lead).temp}
                  size="small"
                  sx={{ 
                    backgroundColor: firsttouchService.getLeadTemperature(lead).color,
                    color: 'white'
                  }}
                />
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Source: {firsttouchService.getSourceIcon(lead.source)} {lead.source}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Intent: {lead.intent_type.replace('_', ' ')}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Time since inquiry: {lead.time_since_inquiry_minutes} minutes
                </Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Engagement Score: {(lead.lead_engagement_score * 100).toFixed(0)}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={lead.lead_engagement_score * 100} 
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>

              <Button
                variant="contained"
                fullWidth
                startIcon={<PsychologyIcon />}
                onClick={() => onOptimizeLead(lead)}
              >
                Optimize Call
              </Button>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

// Performance Analytics Component
const PerformanceAnalytics = ({ analytics }) => {
  if (!analytics) {
    return <Typography>Loading analytics...</Typography>;
  }

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Overall Performance
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Total Calls: {analytics.total_calls}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Connect Rate: {(analytics.connect_rate * 100).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Qualification Rate: {(analytics.qualification_rate * 100).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Booking Rate: {(analytics.booking_rate * 100).toFixed(1)}%
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Segment Performance
            </Typography>
            {Object.entries(analytics.performance_by_segment || {}).map(([segment, data]) => (
              <Box key={segment} sx={{ mb: 1 }}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {segment}: {(data.connect_rate * 100).toFixed(1)}% connect rate
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {data.calls} calls, {(data.qualification_rate * 100).toFixed(1)}% qualified
                </Typography>
              </Box>
            ))}
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              AI Recommendations
            </Typography>
            <List>
              {analytics.recommendations?.map((rec, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <CheckCircleIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText primary={rec} />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

// Problem Analysis Component
const ProblemAnalysisView = ({ problemAnalysis }) => {
  if (!problemAnalysis) {
    return <Typography>Loading problem analysis...</Typography>;
  }

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>
          Identified Problems
        </Typography>
        {problemAnalysis.problems?.map((problem, index) => (
          <Card key={problem.problem_id || index} sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" color="error" gutterBottom>
                {problem.title}
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>Symptom:</strong> {problem.symptom}
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
    </Grid>
  );
};

// Agent Interface Component
const AgentInterface = ({ leads, onOptimizeLead }) => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>
          Agent Dashboard - Next Actions
        </Typography>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Lead</TableCell>
                <TableCell>Source</TableCell>
                <TableCell>Urgency</TableCell>
                <TableCell>Time</TableCell>
                <TableCell>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {leads.map((lead) => (
                <TableRow key={lead.lead_id}>
                  <TableCell>
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {lead.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {lead.intent_type.replace('_', ' ')}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={lead.source}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={lead.urgency_level}
                      size="small"
                      color={lead.urgency_level === 'high' ? 'error' : 'default'}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {lead.time_since_inquiry_minutes}m ago
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      variant="contained"
                      startIcon={<PhoneIcon />}
                      onClick={() => onOptimizeLead(lead)}
                    >
                      Call Now
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Grid>
    </Grid>
  );
};

// Optimization Results Component
const OptimizationResults = ({ result, lead }) => {
  const probability = firsttouchService.formatProbability(result.success_probability);
  const timing = firsttouchService.formatTiming(result.optimal_timing);

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Success Probability
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="h4" sx={{ color: probability.color }}>
                {probability.percentage}%
              </Typography>
              <Chip 
                label={probability.level} 
                size="small"
                sx={{ backgroundColor: probability.color, color: 'white' }}
              />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Optimal Timing
            </Typography>
            <Typography variant="h6" sx={{ color: timing.urgencyColor }}>
              {timing.urgencyText}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Priority: {timing.priorityLevel}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Script Recommendations
            </Typography>
            <Typography variant="body2">
              <strong>Approach:</strong> {result.script_recommendations?.script_type || 'Personalized approach'}
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              <strong>Key Points:</strong> {JSON.stringify(result.script_recommendations?.talking_points || ['Build rapport', 'Understand needs', 'Present solution'])}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default FirstTouch;
