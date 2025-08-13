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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControlLabel,
  Switch,
  Tabs,
  Tab,
  LinearProgress,
  Tooltip,
  IconButton,
  Snackbar
} from '@mui/material';
import {
  PersonAdd as PersonAddIcon,
  TrendingUp as TrendingUpIcon,
  Message as MessageIcon,
  Analytics as AnalyticsIcon,
  Refresh as RefreshIcon,
  Send as SendIcon,
  ContentCopy as ContentCopyIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import refermoreService from '../../services/refermoreService';

// Tab panel component
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`refermore-tabpanel-${index}`}
      aria-labelledby={`refermore-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ReferralManagement = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [problemAnalysis, setProblemAnalysis] = useState(null);
  const [error, setError] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  // Message generation dialog state
  const [messageDialog, setMessageDialog] = useState({ open: false, profile: null, message: '' });
  const [messageLoading, setMessageLoading] = useState(false);

  // Candidate scoring dialog state
  const [scoringDialog, setScoringDialog] = useState({ open: false });
  const [scoringForm, setScoringForm] = useState({
    completion_rate: 0.7,
    engagement_score: 60,
    satisfaction_rating: 8,
    forum_posts: 5,
    social_shares: 2,
    net_promoter_score: 20,
    certificate_earned: false
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load all required data in parallel
      const [dashboardRes, candidatesRes, analyticsRes, problemRes] = await Promise.all([
        refermoreService.getDashboardData(),
        refermoreService.getCandidates(20, 0.6),
        refermoreService.getAnalytics(500),
        refermoreService.getProblemAnalysis()
      ]);

      setDashboardData(dashboardRes);
      setCandidates(candidatesRes.items || []);
      setAnalytics(analyticsRes);
      setProblemAnalysis(problemRes);

    } catch (err) {
      setError(err.message || 'Failed to load referral data');
      console.error('Error loading referral data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadInitialData();
  };

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  const handleGenerateMessage = async (profile) => {
    try {
      setMessageLoading(true);
      const messageData = await refermoreService.personalizeMessage(profile);
      setMessageDialog({
        open: true,
        profile,
        message: messageData.message || 'Message generated successfully'
      });
    } catch (err) {
      showSnackbar('Failed to generate message', 'error');
    } finally {
      setMessageLoading(false);
    }
  };

  const handleScoreCandidate = async () => {
    try {
      setMessageLoading(true);
      const scoreData = await refermoreService.scoreReferralPropensity(scoringForm);
      
      // Add to candidates list
      const newCandidate = {
        student_id: `NEW_${Date.now()}`,
        score: scoreData.propensity_score,
        likelihood: scoreData.insights?.likelihood_bucket || 'medium',
        profile: scoringForm
      };
      
      setCandidates(prev => [newCandidate, ...prev]);
      setScoringDialog({ open: false });
      showSnackbar(`Candidate scored: ${scoreData.propensity_score}% propensity`, 'success');
      
    } catch (err) {
      showSnackbar('Failed to score candidate', 'error');
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

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error" action={
          <Button color="inherit" size="small" onClick={handleRefresh}>
            Retry
          </Button>
        }>
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          ReferMore AI - Referral Management
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<PersonAddIcon />}
            onClick={() => setScoringDialog({ open: true })}
            sx={{ mr: 2 }}
          >
            Score New Candidate
          </Button>
          <IconButton onClick={handleRefresh} title="Refresh Data">
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                High-Propensity Candidates
              </Typography>
              <Typography variant="h4" color="primary">
                {candidates.filter(c => c.likelihood === 'high').length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Ready for outreach
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Candidates
              </Typography>
              <Typography variant="h4" color="primary">
                {candidates.length}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                In pipeline
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg Propensity Score
              </Typography>
              <Typography variant="h4" color="primary">
                {analytics?.distribution?.avg_propensity || 'N/A'}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Model confidence
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
                {problemAnalysis?.overall_impact?.referral_optimization?.split(' ')[0] || '₹10L+'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Annual potential
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs Navigation */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentTab} onChange={handleTabChange}>
          <Tab label="Candidate Dashboard" icon={<PersonAddIcon />} />
          <Tab label="Analytics" icon={<AnalyticsIcon />} />
          <Tab label="Problem Analysis" icon={<TrendingUpIcon />} />
        </Tabs>
      </Box>

      {/* Tab Content */}
      <TabPanel value={currentTab} index={0}>
        <CandidateDashboard 
          candidates={candidates}
          onGenerateMessage={handleGenerateMessage}
          messageLoading={messageLoading}
        />
      </TabPanel>

      <TabPanel value={currentTab} index={1}>
        <AnalyticsDashboard analytics={analytics} />
      </TabPanel>

      <TabPanel value={currentTab} index={2}>
        <ProblemAnalysisView problemAnalysis={problemAnalysis} />
      </TabPanel>

      {/* Message Generation Dialog */}
      <Dialog 
        open={messageDialog.open} 
        onClose={() => setMessageDialog({ open: false, profile: null, message: '' })}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <MessageIcon />
            Personalized Referral Message
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Generated message for candidate:
            </Typography>
            <TextField
              multiline
              rows={8}
              value={messageDialog.message}
              onChange={(e) => setMessageDialog(prev => ({ ...prev, message: e.target.value }))}
              fullWidth
              variant="outlined"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMessageDialog({ open: false, profile: null, message: '' })}>
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

      {/* Scoring Dialog */}
      <Dialog
        open={scoringDialog.open}
        onClose={() => setScoringDialog({ open: false })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Score New Referral Candidate</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              label="Completion Rate"
              type="number"
              value={scoringForm.completion_rate}
              onChange={(e) => setScoringForm(prev => ({ ...prev, completion_rate: parseFloat(e.target.value) }))}
              inputProps={{ min: 0, max: 1, step: 0.1 }}
              fullWidth
              sx={{ mb: 2 }}
            />
            <TextField
              label="Engagement Score (0-100)"
              type="number"
              value={scoringForm.engagement_score}
              onChange={(e) => setScoringForm(prev => ({ ...prev, engagement_score: parseInt(e.target.value) }))}
              inputProps={{ min: 0, max: 100 }}
              fullWidth
              sx={{ mb: 2 }}
            />
            <TextField
              label="Satisfaction Rating (1-10)"
              type="number"
              value={scoringForm.satisfaction_rating}
              onChange={(e) => setScoringForm(prev => ({ ...prev, satisfaction_rating: parseInt(e.target.value) }))}
              inputProps={{ min: 1, max: 10 }}
              fullWidth
              sx={{ mb: 2 }}
            />
            <TextField
              label="Forum Posts"
              type="number"
              value={scoringForm.forum_posts}
              onChange={(e) => setScoringForm(prev => ({ ...prev, forum_posts: parseInt(e.target.value) }))}
              inputProps={{ min: 0 }}
              fullWidth
              sx={{ mb: 2 }}
            />
            <TextField
              label="Social Shares"
              type="number"
              value={scoringForm.social_shares}
              onChange={(e) => setScoringForm(prev => ({ ...prev, social_shares: parseInt(e.target.value) }))}
              inputProps={{ min: 0 }}
              fullWidth
              sx={{ mb: 2 }}
            />
            <TextField
              label="Net Promoter Score (-100 to 100)"
              type="number"
              value={scoringForm.net_promoter_score}
              onChange={(e) => setScoringForm(prev => ({ ...prev, net_promoter_score: parseInt(e.target.value) }))}
              inputProps={{ min: -100, max: 100 }}
              fullWidth
              sx={{ mb: 2 }}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={scoringForm.certificate_earned}
                  onChange={(e) => setScoringForm(prev => ({ ...prev, certificate_earned: e.target.checked }))}
                />
              }
              label="Certificate Earned"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setScoringDialog({ open: false })}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleScoreCandidate}
            disabled={messageLoading}
          >
            {messageLoading ? <CircularProgress size={20} /> : 'Score Candidate'}
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
    </Container>
  );
};

// Candidate Dashboard Component
const CandidateDashboard = ({ candidates, onGenerateMessage, messageLoading }) => {
  const getPropensityColor = (likelihood) => {
    switch (likelihood) {
      case 'high': return 'success';
      case 'medium': return 'warning';
      case 'low': return 'error';
      default: return 'default';
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Referral Candidates
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Candidate ID</TableCell>
                <TableCell>Propensity Score</TableCell>
                <TableCell>Likelihood</TableCell>
                <TableCell>Timing</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {candidates.map((candidate, index) => (
                <TableRow key={candidate.student_id || index}>
                  <TableCell>{candidate.student_id || `CAND-${index}`}</TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="body2" fontWeight="bold">
                        {candidate.score || 'N/A'}%
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={candidate.score || 0}
                        sx={{ width: 60, height: 6 }}
                      />
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={candidate.likelihood || 'Unknown'} 
                      color={getPropensityColor(candidate.likelihood)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {candidate.optimal_timing || 'Within 24h'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      startIcon={<SendIcon />}
                      onClick={() => onGenerateMessage(candidate.profile || candidate)}
                      disabled={messageLoading}
                    >
                      Generate Message
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {candidates.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <Typography color="textSecondary">
                      No candidates found. Add some candidates to get started.
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
};

// Analytics Dashboard Component
const AnalyticsDashboard = ({ analytics }) => {
  if (!analytics) {
    return <Typography>No analytics data available</Typography>;
  }

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Propensity Distribution
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="textSecondary">
                High Propensity: {analytics.distribution?.high_share || 0}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={analytics.distribution?.high_share || 0}
                color="success"
                sx={{ mb: 1 }}
              />
              <Typography variant="body2" color="textSecondary">
                Medium Propensity: {analytics.distribution?.medium_share || 0}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={analytics.distribution?.medium_share || 0}
                color="warning"
                sx={{ mb: 1 }}
              />
              <Typography variant="body2" color="textSecondary">
                Low Propensity: {analytics.distribution?.low_share || 0}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={analytics.distribution?.low_share || 0}
                color="error"
              />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              ROI Metrics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Total Invites</Typography>
                <Typography variant="h6">{analytics.roi?.totals?.invites || 0}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Signups</Typography>
                <Typography variant="h6">{analytics.roi?.totals?.signups || 0}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Conversions</Typography>
                <Typography variant="h6">{analytics.roi?.totals?.conversions || 0}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">ROI Multiple</Typography>
                <Typography variant="h6" color="success.main">
                  {analytics.roi?.roi_multiple ? `${analytics.roi.roi_multiple}x` : 'N/A'}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
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

export default ReferralManagement;
