import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import {
  SmartToy as SmartToyIcon,
  RocketLaunch as RocketLaunchIcon,
  Assessment as AssessmentIcon,
  Dashboard as DashboardIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  Speed as SpeedIcon,
  Psychology as PsychologyIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from "@mui/icons-material";
import onetruthService from "../../services/onetruthService";

// Tab panel component
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`onetruth-tabpanel-${index}`}
      aria-labelledby={`onetruth-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const OneTruth = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [loadedTabs, setLoadedTabs] = useState(new Set([0]));
  const [problemAnalysis, setProblemAnalysis] = useState(null);
  const [solutions, setSolutions] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [error, setError] = useState(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "info",
  });
  const [analysisLoading, setAnalysisLoading] = useState(false);

  useEffect(() => {
    loadTabData(0); // Load first tab on mount
  }, []);

  const showSnackbar = (message, severity = "info") => {
    setSnackbar({ open: true, message, severity });
  };

  const loadTabData = async (tabIndex, forceRefresh = false) => {
    // Skip if already loaded and not forcing refresh
    if (loadedTabs.has(tabIndex) && !forceRefresh) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      switch (tabIndex) {
        case 0: // Diagnose Problems
          const problemRes = await onetruthService.getProblemAnalysis();
          setProblemAnalysis(problemRes);
          break;

        case 1: // Propose Solutions
          const solutionsRes = await onetruthService.getProposedSolutions();
          setSolutions(solutionsRes);
          break;

        case 2: // Prioritize & Justify
          // Load both solutions and problem analysis for comparison
          const [solutionsRes2, problemRes2] = await Promise.all([
            onetruthService.getProposedSolutions(),
            onetruthService.getProblemAnalysis(),
          ]);
          setSolutions(solutionsRes2);
          setProblemAnalysis(problemRes2);
          break;

        case 3: // Live Demo
          const dashboardRes = await onetruthService.getDashboardData("7d", true);
          setDashboardData(dashboardRes);
          break;

        default:
          console.warn("Unknown tab index:", tabIndex);
      }

      // Mark tab as loaded
      setLoadedTabs((prev) => new Set([...prev, tabIndex]));
    } catch (err) {
      setError(err.message || `Failed to load data for tab ${tabIndex}`);
      console.error(`Error loading tab ${tabIndex} data:`, err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = (forceRefresh = false) => {
    if (forceRefresh) {
      setLoadedTabs(new Set());
    }
    loadTabData(currentTab, forceRefresh);
  };

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
    loadTabData(newValue);
  };

  const handleAnalyzeProblems = async () => {
    try {
      setAnalysisLoading(true);
      setError(null);

      const problemRes = await onetruthService.getProblemAnalysis(true);
      setProblemAnalysis(problemRes);

      showSnackbar(
        "Problem analysis updated with latest marketing analytics data!",
        "success"
      );
    } catch (err) {
      setError(err.message || "Failed to analyze problems");
    } finally {
      setAnalysisLoading(false);
    }
  };

  // Render Problem Analysis Section
  const renderProblemAnalysis = () => {
    if (!problemAnalysis) {
      return (
        <Alert severity="info">
          <Typography variant="body2">
            Loading problem analysis...
          </Typography>
        </Alert>
      );
    }

    return (
      <Grid container spacing={3}>
        {problemAnalysis.diagnosed_problems.map((problem, index) => (
          <Grid item xs={12} key={problem.problem_id}>
            <Card>
              <CardContent>
                <Box sx={{ display: "flex", alignItems: "flex-start", mb: 2 }}>
                  <ErrorIcon color="error" sx={{ mr: 2, mt: 0.5 }} />
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6" gutterBottom>
                      {problem.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      <strong>Symptom:</strong> {problem.symptom}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      <strong>Root Cause:</strong> {problem.root_cause}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      <strong>Business Impact:</strong> {problem.impact}
                    </Typography>
                    <Alert severity="warning" sx={{ mt: 2 }}>
                      <Typography variant="body2">
                        <strong>Evidence:</strong> {problem.evidence}
                      </Typography>
                    </Alert>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}

        {/* Segment Challenges */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
            Data Source Analysis
          </Typography>
          <Grid container spacing={2}>
            {problemAnalysis.segment_challenges.map((segment, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      {segment.segment_name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {segment.description}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Impact:</strong> {segment.conversion_impact}
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      {segment.characteristics.map((char, idx) => (
                        <Chip
                          key={idx}
                          label={char}
                          size="small"
                          sx={{ mr: 1, mb: 1 }}
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>
    );
  };

  // Render Solutions Section
  const renderSolutions = () => {
    if (!solutions) {
      return (
        <Alert severity="info">
          <Typography variant="body2">
            Loading proposed solutions...
          </Typography>
        </Alert>
      );
    }

    return (
      <Grid container spacing={3}>
        {/* Solution 1: Data Unification */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "flex-start", mb: 2 }}>
                <RocketLaunchIcon color="primary" sx={{ mr: 2, mt: 0.5 }} />
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h6" gutterBottom>
                    {solutions.data_unification.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {solutions.data_unification.description}
                  </Typography>
                  <Typography variant="body2" paragraph>
                    <strong>Technical Approach:</strong> {solutions.data_unification.technical_approach}
                  </Typography>
                  
                  <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                    Key Benefits:
                  </Typography>
                  <List dense>
                    {solutions.data_unification.benefits.map((benefit, idx) => (
                      <ListItem key={idx}>
                        <ListItemIcon>
                          <CheckCircleIcon color="success" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={benefit} />
                      </ListItem>
                    ))}
                  </List>

                  <Grid container spacing={2} sx={{ mt: 2 }}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2">
                        <strong>Implementation:</strong> {solutions.data_unification.implementation_effort}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2">
                        <strong>Expected ROI:</strong> {solutions.data_unification.expected_roi}
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Solution 2: Executive Briefing */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "flex-start", mb: 2 }}>
                <PsychologyIcon color="secondary" sx={{ mr: 2, mt: 0.5 }} />
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h6" gutterBottom>
                    {solutions.executive_briefing.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {solutions.executive_briefing.description}
                  </Typography>
                  
                  <Grid container spacing={2} sx={{ mt: 2 }}>
                    <Grid item xs={12} md={4}>
                      <Typography variant="subtitle2" gutterBottom>
                        AI Capabilities:
                      </Typography>
                      {solutions.executive_briefing.ai_capabilities.map((cap, idx) => (
                        <Chip key={idx} label={cap} size="small" sx={{ mr: 1, mb: 1 }} color="primary" />
                      ))}
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Typography variant="subtitle2" gutterBottom>
                        Automation Features:
                      </Typography>
                      {solutions.executive_briefing.automation_features.map((feature, idx) => (
                        <Chip key={idx} label={feature} size="small" sx={{ mr: 1, mb: 1 }} color="secondary" />
                      ))}
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Typography variant="subtitle2" gutterBottom>
                        Decision Support:
                      </Typography>
                      {solutions.executive_briefing.decision_support.map((support, idx) => (
                        <Chip key={idx} label={support} size="small" sx={{ mr: 1, mb: 1 }} color="success" />
                      ))}
                    </Grid>
                  </Grid>

                  <Grid container spacing={2} sx={{ mt: 2 }}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2">
                        <strong>Implementation:</strong> {solutions.executive_briefing.implementation_effort}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2">
                        <strong>Expected ROI:</strong> {solutions.executive_briefing.expected_roi}
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  // Render Prioritization Section
  const renderPrioritization = () => {
    if (!solutions) {
      return (
        <Alert severity="info">
          <Typography variant="body2">
            Loading prioritization analysis...
          </Typography>
        </Alert>
      );
    }

    return (
      <Grid container spacing={3}>
        {/* Impact vs Effort Matrix */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Solution Prioritization Matrix
              </Typography>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Solution</TableCell>
                      <TableCell align="center">Impact Score</TableCell>
                      <TableCell align="center">Effort Score</TableCell>
                      <TableCell>ROI Potential</TableCell>
                      <TableCell>Timeline</TableCell>
                      <TableCell>Priority</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {solutions.prioritization.map((item) => (
                      <TableRow key={item.solution_id}>
                        <TableCell>
                          {item.solution_id === "data_unification_platform"
                            ? "Data Unification Platform"
                            : "AI Executive Briefing"}
                        </TableCell>
                        <TableCell align="center">
                          <Box sx={{ display: "flex", alignItems: "center" }}>
                            <LinearProgress
                              variant="determinate"
                              value={item.impact_score * 10}
                              sx={{ width: 60, mr: 1 }}
                              color="success"
                            />
                            <Typography variant="body2">{item.impact_score}/10</Typography>
                          </Box>
                        </TableCell>
                        <TableCell align="center">
                          <Box sx={{ display: "flex", alignItems: "center" }}>
                            <LinearProgress
                              variant="determinate"
                              value={item.effort_score * 10}
                              sx={{ width: 60, mr: 1 }}
                              color="warning"
                            />
                            <Typography variant="body2">{item.effort_score}/10</Typography>
                          </Box>
                        </TableCell>
                        <TableCell>{item.roi_potential}</TableCell>
                        <TableCell>{item.timeline}</TableCell>
                        <TableCell>
                          <Chip
                            label={item.business_priority}
                            color={
                              item.business_priority === "Critical"
                                ? "error"
                                : item.business_priority === "High"
                                ? "warning"
                                : "primary"
                            }
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Combined Impact */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Combined Business Impact
              </Typography>
              <Grid container spacing={2}>
                {Object.entries(solutions.combined_impact).map(([key, value]) => (
                  <Grid item xs={12} md={6} lg={4} key={key}>
                    <Box sx={{ textAlign: "center", p: 2 }}>
                      <Typography variant="h6" color="primary">
                        {value}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {key.replace(/_/g, " ").toUpperCase()}
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Success Metrics */}
        <Grid item xs={12}>
          <Alert severity="success">
            <Typography variant="body1" gutterBottom>
              <strong>Success Metrics Targets:</strong>
            </Typography>
            <List dense>
              {solutions.data_unification.success_metrics.map((metric, idx) => (
                <ListItem key={idx}>
                  <ListItemIcon>
                    <TrendingUpIcon color="success" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText primary={metric} />
                </ListItem>
              ))}
            </List>
          </Alert>
        </Grid>
      </Grid>
    );
  };

  // Render Live Demo Section
  const renderLiveDemo = () => {
    if (!dashboardData) {
      return (
        <Alert severity="info">
          <Typography variant="body2">
            Loading live demo data...
          </Typography>
        </Alert>
      );
    }

    return (
      <Grid container spacing={3}>
        {/* System Status */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                OneTruth Marketing Analytics - Live System
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={3}>
                  <Box sx={{ textAlign: "center" }}>
                    <CheckCircleIcon color="success" sx={{ fontSize: 40 }} />
                    <Typography variant="h6">Active</Typography>
                    <Typography variant="caption">System Status</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box sx={{ textAlign: "center" }}>
                    <Typography variant="h4" color="primary">
                      {dashboardData.analytics?.total_records || 0}
                    </Typography>
                    <Typography variant="caption">Analytics Records</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box sx={{ textAlign: "center" }}>
                    <Typography variant="h4" color="success.main">
                      {dashboardData.analytics?.avg_health_score?.toFixed(1) || "0.0"}%
                    </Typography>
                    <Typography variant="caption">Business Health</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box sx={{ textAlign: "center" }}>
                    <Typography variant="h4" color="warning.main">
                      {dashboardData.analytics?.anomaly_rate || 0}%
                    </Typography>
                    <Typography variant="caption">Anomaly Rate</Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Data Sources Status */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Integrated Data Sources
              </Typography>
              <Grid container spacing={2}>
                {Object.entries(dashboardData.system_status?.data_sources || {}).map(([source, status]) => (
                  <Grid item xs={12} sm={6} md={4} lg={2} key={source}>
                    <Box sx={{ textAlign: "center", p: 1 }}>
                      <Chip
                        label={source.toUpperCase()}
                        color={status === "connected" ? "success" : "error"}
                        icon={status === "connected" ? <CheckCircleIcon /> : <ErrorIcon />}
                      />
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Business Metrics Dashboard */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Real-Time Business Intelligence
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: "center" }}>
                      <Typography variant="h4" color="primary">
                        {dashboardData.dashboard?.key_metrics?.lead_conversion_rate || "0%"}
                      </Typography>
                      <Typography variant="caption">Lead Conversion Rate</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: "center" }}>
                      <Typography variant="h4" color="success.main">
                        {dashboardData.dashboard?.key_metrics?.ad_efficiency || "₹0"}
                      </Typography>
                      <Typography variant="caption">Cost Per Lead</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: "center" }}>
                      <Typography variant="h4" color="info.main">
                        {dashboardData.dashboard?.key_metrics?.support_satisfaction || "0/10"}
                      </Typography>
                      <Typography variant="caption">Support CSAT</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Predictions */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent AI Predictions & Anomalies
              </Typography>
              {dashboardData.analytics?.recent_predictions?.length > 0 ? (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell>Health Score</TableCell>
                        <TableCell>Anomaly Status</TableCell>
                        <TableCell>Action</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {dashboardData.analytics.recent_predictions.map((pred, idx) => (
                        <TableRow key={idx}>
                          <TableCell>{pred.date}</TableCell>
                          <TableCell>
                            <LinearProgress
                              variant="determinate"
                              value={pred.health_score || 0}
                              sx={{ width: 100 }}
                              color={pred.health_score > 70 ? "success" : "warning"}
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={pred.anomaly ? "Anomaly Detected" : "Normal"}
                              color={pred.anomaly ? "error" : "success"}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Button size="small" variant="outlined">
                              View Details
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No recent predictions available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ textAlign: "center", mb: 4 }}>
        <Typography variant="h3" sx={{ fontWeight: "bold", mb: 2 }}>
          OneTruth - Marketing Analytics
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 3 }}>
          AI-Powered Unified Business Intelligence for Executive Decision Making
        </Typography>
        <Box sx={{ display: "flex", justifyContent: "center", gap: 2, mb: 3 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => handleRefresh(false)}
            disabled={loading}
          >
            Refresh Data
          </Button>
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={() => handleRefresh(true)}
            disabled={loading}
          >
            Force Refresh
          </Button>
        </Box>
      </Box>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Loading Indicator */}
      {loading && (
        <Box sx={{ display: "flex", justifyContent: "center", my: 3 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Tabs Navigation */}
      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}>
        <Tabs value={currentTab} onChange={handleTabChange}>
          <Tab label="Diagnose Problems" icon={<SmartToyIcon />} />
          <Tab label="Propose Solutions" icon={<RocketLaunchIcon />} />
          <Tab label="Prioritize & Justify" icon={<AssessmentIcon />} />
          <Tab label="Live Demo" icon={<DashboardIcon />} />
        </Tabs>
      </Box>

      {/* Tab 0: Diagnose Problems */}
      <TabPanel value={currentTab} index={0}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 3, display: 'flex', alignItems: 'center' }}>
            <SmartToyIcon color="primary" sx={{ mr: 2 }} />
            🔍 Diagnose the Problem
          </Typography>
          
          <Alert severity="warning" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>OneTruth Challenge:</strong> Leadership can't make fast decisions because data lives in many places 
              (CRM, analytics, ads, support, telephony, LMS). Weekly executive reviews take 3–5 hours of manual prep 
              with 2-4 percentage point conversion variances across reports.
            </Typography>
          </Alert>

          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  AI Analysis of Marketing Analytics Data
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<PsychologyIcon />}
                  onClick={handleAnalyzeProblems}
                  disabled={analysisLoading}
                  sx={{ minWidth: 160 }}
                >
                  {analysisLoading ? (
                    <>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      Analyzing...
                    </>
                  ) : (
                    'Analyze Problems'
                  )}
                </Button>
              </Box>
              {renderProblemAnalysis()}
            </CardContent>
          </Card>
        </Box>
      </TabPanel>

      {/* Tab 1: Propose Solutions */}
      <TabPanel value={currentTab} index={1}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 3, display: 'flex', alignItems: 'center' }}>
            <RocketLaunchIcon color="primary" sx={{ mr: 2 }} />
            💡 Propose AI-First Solutions
          </Typography>
          
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>Two AI-First Approaches:</strong> (a) Unify key metrics into single source of truth 
              (b) Auto-generate weekly executive brief with anomalies and "do-next" recommendations.
            </Typography>
          </Alert>

          {renderSolutions()}
        </Box>
      </TabPanel>

      {/* Tab 2: Prioritize & Justify */}
      <TabPanel value={currentTab} index={2}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 3, display: 'flex', alignItems: 'center' }}>
            <AssessmentIcon color="primary" sx={{ mr: 2 }} />
            📊 Prioritize & Justify by Impact vs Effort
          </Typography>
          
          <Alert severity="success" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>Success Metrics:</strong> Cut report prep by 80% (5h → 1h); decisions within 48 hours; 
              +15-20% ROI on reallocated spend; real-time anomaly detection vs 7-10 day lag.
            </Typography>
          </Alert>

          {renderPrioritization()}
        </Box>
      </TabPanel>

      {/* Tab 3: Live Demo */}
      <TabPanel value={currentTab} index={3}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 3, display: 'flex', alignItems: 'center' }}>
            <DashboardIcon color="primary" sx={{ mr: 2 }} />
            🚀 Live Demo - Unified Marketing Intelligence
          </Typography>
          
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>Real-Time Demo:</strong> Unified analytics from CRM, GA4, ad platforms, support, telephony, 
              and LMS with AI-powered anomaly detection and executive insights.
            </Typography>
          </Alert>

          {renderLiveDemo()}
        </Box>
      </TabPanel>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default OneTruth;
