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
  Switch,
  FormControlLabel,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Badge,
  Tooltip,
} from "@mui/material";
import {
  AttachMoney as AttachMoneyIcon,
  Psychology as PsychologyIcon,
  Assessment as AssessmentIcon,
  Dashboard as DashboardIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  Speed as SpeedIcon,
  School as SchoolIcon,
  Groups as GroupsIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  MonetizationOn as MonetizationOnIcon,
  Savings as SavingsIcon,
} from "@mui/icons-material";
import pricesenseService from "../../services/pricesenseService";

// Tab panel component
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`pricesense-tabpanel-${index}`}
      aria-labelledby={`pricesense-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function a11yProps(index) {
  return {
    id: `pricesense-tab-${index}`,
    'aria-controls': `pricesense-tabpanel-${index}`,
  };
}

const PriceSense = () => {
  // Tab management
  const [currentTab, setCurrentTab] = useState(0);
  
  // Data states
  const [problemAnalysis, setProblemAnalysis] = useState(null);
  const [solutions, setSolutions] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  
  // UI states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "info"
  });

  // Demo settings
  const [timeRange, setTimeRange] = useState("7d");
  const [includeAnomalies, setIncludeAnomalies] = useState(true);

  // Load data based on current tab
  const loadTabData = async (tabIndex) => {
    if (loading) return;
    
    setLoading(true);
    setError(null);

    try {
      switch (tabIndex) {
        case 0: // Diagnose Problems
          const problemRes = await pricesenseService.getProblemAnalysis();
          setProblemAnalysis(problemRes);
          break;

        case 1: // Propose Solutions
          const solutionsRes = await pricesenseService.getProposedSolutions();
          setSolutions(solutionsRes);
          break;

        case 2: // Prioritize & Justify
          // Load both solutions and problem analysis for comparison
          const [solutionsRes2, problemRes2] = await Promise.all([
            pricesenseService.getProposedSolutions(),
            pricesenseService.getProblemAnalysis(),
          ]);
          setSolutions(solutionsRes2);
          setProblemAnalysis(problemRes2);
          break;

        case 3: // Live Demo
          const dashboardRes = await pricesenseService.getDashboardData(timeRange, includeAnomalies);
          setDashboardData(dashboardRes);
          break;

        default:
          console.warn("Unknown tab index:", tabIndex);
      }
    } catch (error) {
      console.error("Failed to load tab data:", error);
      setError(error.message);
      setSnackbar({
        open: true,
        message: `Failed to load data: ${error.message}`,
        severity: "error"
      });
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    loadTabData(0); // Start with first tab
  }, []);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
    loadTabData(newValue);
  };

  // Refresh current tab data
  const refreshCurrentTab = async () => {
    if (currentTab === 0) {
      // Force refresh problem analysis
      try {
        setLoading(true);
        const problemRes = await pricesenseService.getProblemAnalysis(true);
        setProblemAnalysis(problemRes);
        setSnackbar({
          open: true,
          message: "Problem analysis refreshed successfully",
          severity: "success"
        });
      } catch (error) {
        setSnackbar({
          open: true,
          message: `Refresh failed: ${error.message}`,
          severity: "error"
        });
      } finally {
        setLoading(false);
      }
    } else {
      loadTabData(currentTab);
    }
  };

  // Handle demo settings change
  const handleDemoSettingsChange = () => {
    if (currentTab === 3) {
      loadTabData(3); // Reload dashboard data
    }
  };

  // Render functions for each tab
  const renderProblemsTab = () => (
    <Box>
      <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 3, display: 'flex', alignItems: 'center' }}>
        <PsychologyIcon color="primary" sx={{ mr: 2 }} />
        🔍 Diagnose Problems - Plan Selection Optimization Issues
      </Typography>
      
      <Alert severity="warning" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Core Challenge:</strong> Conversion lifts on certain plans aren't consistent across audiences. 
          High-intent segments choosing longer payment plans with higher churn rates.
          {problemAnalysis && (
            <Box component="span" sx={{ ml: 1 }}>
              <Chip 
                size="small" 
                color="primary" 
                label="Analysis from Real Data" 
                variant="outlined"
              />
            </Box>
          )}
        </Typography>
      </Alert>

      {loading && (
        <Box display="flex" justifyContent="center" alignItems="center" py={4}>
          <CircularProgress size={40} />
          <Typography variant="body1" sx={{ ml: 2 }}>
            Loading real data from MongoDB...
          </Typography>
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>Data Loading Error:</strong> {error}
            <br />
            <Button size="small" onClick={refreshCurrentTab} sx={{ mt: 1 }}>
              Retry Loading
            </Button>
          </Typography>
        </Alert>
      )}

      {!loading && !error && !problemAnalysis && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            No data loaded yet. Click refresh to load problem analysis from your database.
          </Typography>
        </Alert>
      )}

      {problemAnalysis && (
        <Grid container spacing={3}>
          {/* Diagnosed Problems */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                  <ErrorIcon color="error" sx={{ mr: 1 }} />
                  Identified Problems
                </Typography>
                {problemAnalysis.diagnosed_problems?.map((problem, index) => (
                  <Paper key={index} sx={{ p: 2, mb: 2, border: '1px solid #e0e0e0' }}>
                    <Typography variant="h6" color="error" gutterBottom>
                      {problem.title}
                    </Typography>
                    <Typography variant="body2" paragraph>
                      <strong>Symptom:</strong> {problem.symptom}
                    </Typography>
                    <Typography variant="body2" paragraph>
                      <strong>Root Cause:</strong> {problem.root_cause}
                    </Typography>
                    <Typography variant="body2" paragraph>
                      <strong>Impact:</strong> {problem.impact}
                    </Typography>
                    <Typography variant="body2" paragraph>
                      <strong>Evidence:</strong> {problem.evidence}
                    </Typography>
                    
                    {/* Supporting Data Visualization */}
                    {problem.supporting_data && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>Supporting Metrics:</Typography>
                        <Grid container spacing={2}>
                          {Object.entries(problem.supporting_data).map(([key, value]) => (
                            key !== 'segment_performance' && key !== 'revenue_impact' && key !== 'scholarship_segments' && key !== 'potential_recovery' && (
                              <Grid item xs={6} md={3} key={key}>
                                <Paper sx={{ p: 1, textAlign: 'center', bgcolor: '#f5f5f5' }}>
                                  <Typography variant="caption" color="text.secondary">
                                    {key.replace(/_/g, ' ').toUpperCase()}
                                  </Typography>
                                  <Typography variant="h6" color="primary">
                                    {typeof value === 'number' ? 
                                      (value < 1 ? `${(value * 100).toFixed(1)}%` : value.toLocaleString()) 
                                      : value
                                    }
                                  </Typography>
                                </Paper>
                              </Grid>
                            )
                          ))}
                        </Grid>
                      </Box>
                    )}
                  </Paper>
                ))}
              </CardContent>
            </Card>
          </Grid>

          {/* Segment Challenges */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                  <GroupsIcon color="warning" sx={{ mr: 1 }} />
                  Segment-Specific Challenges
                </Typography>
                <Grid container spacing={2}>
                  {problemAnalysis.segment_challenges?.map((segment, index) => (
                    <Grid item xs={12} md={4} key={index}>
                      <Paper sx={{ p: 2, height: '100%', border: '1px solid #e0e0e0' }}>
                        <Chip 
                          label={segment.segment_type.toUpperCase()} 
                          color="primary" 
                          size="small" 
                          sx={{ mb: 1 }}
                        />
                        <Typography variant="h6" gutterBottom>
                          {segment.segment_name}
                        </Typography>
                        <Typography variant="body2" paragraph>
                          {segment.description}
                        </Typography>
                        <Typography variant="body2" color="primary" gutterBottom>
                          <strong>Impact:</strong> {segment.conversion_impact}
                        </Typography>
                        
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>Characteristics:</Typography>
                          <List dense>
                            {segment.characteristics?.map((char, idx) => (
                              <ListItem key={idx} sx={{ py: 0, px: 0 }}>
                                <ListItemIcon sx={{ minWidth: 20 }}>
                                  <CheckCircleIcon color="success" fontSize="small" />
                                </ListItemIcon>
                                <ListItemText 
                                  primary={char} 
                                  primaryTypographyProps={{ variant: 'body2' }}
                                />
                              </ListItem>
                            ))}
                          </List>
                        </Box>

                        {/* Supporting Metrics */}
                        {segment.supporting_metrics && (
                          <Box sx={{ mt: 2 }}>
                            <Typography variant="subtitle2" gutterBottom>Key Metrics:</Typography>
                            {Object.entries(segment.supporting_metrics).map(([key, value]) => (
                              <Box key={key} display="flex" justifyContent="space-between" mb={0.5}>
                                <Typography variant="caption">
                                  {key.replace(/_/g, ' ')}:
                                </Typography>
                                <Typography variant="caption" fontWeight="bold">
                                  {typeof value === 'number' ? 
                                    (value < 1 ? `${(value * 100).toFixed(1)}%` : value.toFixed(1))
                                    : value
                                  }
                                </Typography>
                              </Box>
                            ))}
                          </Box>
                        )}
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Overall Impact Summary */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                  <TrendingUpIcon color="success" sx={{ mr: 1 }} />
                  Overall Business Impact
                </Typography>
                <Grid container spacing={2}>
                  {problemAnalysis.overall_impact && Object.entries(problemAnalysis.overall_impact).map(([key, value]) => (
                    <Grid item xs={12} sm={6} key={key}>
                      <Paper sx={{ p: 2, bgcolor: '#f8f9fa', textAlign: 'center' }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {key.replace(/_/g, ' ').toUpperCase()}
                        </Typography>
                        <Typography variant="h6" color="primary" fontWeight="bold">
                          {value}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );

  const renderSolutionsTab = () => (
    <Box>
      <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 3, display: 'flex', alignItems: 'center' }}>
        <AttachMoneyIcon color="primary" sx={{ mr: 2 }} />
        💡 Propose Solutions - AI-Based Plan Recommendation & Messaging
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Two AI-First Approaches:</strong> (a) Smart plan recommendation engine using ML to match optimal plans to segments 
          (b) Intelligent scholarship & discount messaging based on eligibility and behavior patterns.
        </Typography>
      </Alert>

      {solutions && (
        <Grid container spacing={3}>
          {/* AI Plan Recommendation Engine */}
          {solutions.ai_plan_recommendation && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <PsychologyIcon color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6">
                      {solutions.ai_plan_recommendation.title}
                    </Typography>
                    <Chip label="Core Solution" color="primary" size="small" sx={{ ml: 2 }} />
                  </Box>
                  
                  <Typography variant="body1" paragraph>
                    {solutions.ai_plan_recommendation.description}
                  </Typography>
                  
                  <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                    <strong>Technical Approach:</strong>
                  </Typography>
                  <Typography variant="body2" paragraph>
                    {solutions.ai_plan_recommendation.technical_approach}
                  </Typography>

                  <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                    <strong>Key Benefits:</strong>
                  </Typography>
                  <List>
                    {solutions.ai_plan_recommendation.benefits?.map((benefit, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <CheckCircleIcon color="success" />
                        </ListItemIcon>
                        <ListItemText primary={benefit} />
                      </ListItem>
                    ))}
                  </List>

                  <Box display="flex" gap={2} mt={2} flexWrap="wrap">
                    <Chip 
                      label={`Effort: ${solutions.ai_plan_recommendation.implementation_effort}`} 
                      color="warning" 
                    />
                    <Chip 
                      label={`ROI: ${solutions.ai_plan_recommendation.expected_roi}`} 
                      color="success" 
                    />
                  </Box>

                  {/* Success Metrics */}
                  <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                    <strong>Success Metrics:</strong>
                  </Typography>
                  <Grid container spacing={1}>
                    {solutions.ai_plan_recommendation.success_metrics?.map((metric, index) => (
                      <Grid item xs={12} sm={6} key={index}>
                        <Paper sx={{ p: 1, bgcolor: '#e8f5e8' }}>
                          <Typography variant="body2">{metric}</Typography>
                        </Paper>
                      </Grid>
                    ))}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Smart Scholarship Messaging */}
          {solutions.smart_scholarship_messaging && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <SavingsIcon color="secondary" sx={{ mr: 1 }} />
                    <Typography variant="h6">
                      {solutions.smart_scholarship_messaging.title}
                    </Typography>
                    <Chip label="Quick Win" color="secondary" size="small" sx={{ ml: 2 }} />
                  </Box>
                  
                  <Typography variant="body1" paragraph>
                    {solutions.smart_scholarship_messaging.description}
                  </Typography>

                  <Grid container spacing={2} sx={{ mt: 2 }}>
                    <Grid item xs={12} md={4}>
                      <Typography variant="subtitle1" gutterBottom>
                        <strong>AI Capabilities:</strong>
                      </Typography>
                      <List dense>
                        {solutions.smart_scholarship_messaging.ai_capabilities?.map((capability, index) => (
                          <ListItem key={index} sx={{ py: 0.5 }}>
                            <ListItemIcon sx={{ minWidth: 30 }}>
                              <CheckCircleIcon color="primary" fontSize="small" />
                            </ListItemIcon>
                            <ListItemText 
                              primary={capability} 
                              primaryTypographyProps={{ variant: 'body2' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Grid>

                    <Grid item xs={12} md={4}>
                      <Typography variant="subtitle1" gutterBottom>
                        <strong>Automation Features:</strong>
                      </Typography>
                      <List dense>
                        {solutions.smart_scholarship_messaging.automation_features?.map((feature, index) => (
                          <ListItem key={index} sx={{ py: 0.5 }}>
                            <ListItemIcon sx={{ minWidth: 30 }}>
                              <CheckCircleIcon color="success" fontSize="small" />
                            </ListItemIcon>
                            <ListItemText 
                              primary={feature} 
                              primaryTypographyProps={{ variant: 'body2' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Grid>

                    <Grid item xs={12} md={4}>
                      <Typography variant="subtitle1" gutterBottom>
                        <strong>Behavioral Optimization:</strong>
                      </Typography>
                      <List dense>
                        {solutions.smart_scholarship_messaging.behavioral_optimization?.map((optimization, index) => (
                          <ListItem key={index} sx={{ py: 0.5 }}>
                            <ListItemIcon sx={{ minWidth: 30 }}>
                              <CheckCircleIcon color="info" fontSize="small" />
                            </ListItemIcon>
                            <ListItemText 
                              primary={optimization} 
                              primaryTypographyProps={{ variant: 'body2' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Grid>
                  </Grid>

                  <Box display="flex" gap={2} mt={2} flexWrap="wrap">
                    <Chip 
                      label={`Effort: ${solutions.smart_scholarship_messaging.implementation_effort}`} 
                      color="success" 
                    />
                    <Chip 
                      label={`ROI: ${solutions.smart_scholarship_messaging.expected_roi}`} 
                      color="success" 
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      )}
    </Box>
  );

  const renderPrioritizationTab = () => (
    <Box>
      <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 3, display: 'flex', alignItems: 'center' }}>
        <AssessmentIcon color="primary" sx={{ mr: 2 }} />
        📊 Prioritize & Justify by Impact vs Effort
      </Typography>
      
      <Alert severity="success" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Success Metrics:</strong> {
            solutions?.combined_impact ? (
              `${solutions.combined_impact.conversion_optimization} improvement; 
              ${solutions.combined_impact.churn_reduction} defaults reduction; 
              ${solutions.combined_impact.revenue_protection} revenue impact.`
            ) : (
              '+8-12% enrollments through optimized plan presentation; -15% refund/default rate via segment-aware recommendations; +18% scholarship conversion efficiency.'
            )
          }
        </Typography>
      </Alert>

      {solutions?.prioritization && (
        <Grid container spacing={3}>
          {/* Prioritization Matrix */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                  <AssessmentIcon color="primary" sx={{ mr: 1 }} />
                  Solution Prioritization Matrix
                </Typography>
                
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                        <TableCell><strong>Solution</strong></TableCell>
                        <TableCell align="center"><strong>Impact Score</strong></TableCell>
                        <TableCell align="center"><strong>Effort Score</strong></TableCell>
                        <TableCell><strong>ROI Potential</strong></TableCell>
                        <TableCell><strong>Timeline</strong></TableCell>
                        <TableCell><strong>Risk Level</strong></TableCell>
                        <TableCell><strong>Priority</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {solutions.prioritization.map((solution, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Typography variant="body2" fontWeight="bold">
                              {solution.solution_id.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Box display="flex" alignItems="center" justifyContent="center">
                              <Typography variant="h6" color="primary">
                                {solution.impact_score}
                              </Typography>
                              <Typography variant="body2" color="text.secondary" sx={{ ml: 0.5 }}>
                                /10
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell align="center">
                            <Box display="flex" alignItems="center" justifyContent="center">
                              <Typography variant="h6" color="warning.main">
                                {solution.effort_score}
                              </Typography>
                              <Typography variant="body2" color="text.secondary" sx={{ ml: 0.5 }}>
                                /10
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="success.main" fontWeight="bold">
                              {solution.roi_potential}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {solution.timeline}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={solution.risk_level.split(' ')[0]} 
                              color={
                                solution.risk_level.includes('Very Low') ? 'success' :
                                solution.risk_level.includes('Low') ? 'info' :
                                solution.risk_level.includes('Medium') ? 'warning' : 'error'
                              }
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={solution.business_priority.split(' ')[0]} 
                              color={
                                solution.business_priority.includes('Critical') ? 'error' :
                                solution.business_priority.includes('High') ? 'warning' : 'info'
                              }
                              size="small"
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

          {/* Combined Impact Visualization */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                  <TrendingUpIcon color="success" sx={{ mr: 1 }} />
                  Combined Business Impact
                </Typography>
                
                <Grid container spacing={2}>
                  {solutions.combined_impact && Object.entries(solutions.combined_impact).map(([key, value]) => (
                    <Grid item xs={12} sm={6} md={4} key={key}>
                      <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#e8f5e8' }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {key.replace(/_/g, ' ').toUpperCase()}
                        </Typography>
                        <Typography variant="h6" color="success.main" fontWeight="bold">
                          {value}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>

                {/* ROI Calculation Summary */}
                <Box sx={{ mt: 3, p: 2, bgcolor: '#f0f8ff', borderRadius: 1 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    <strong>60-Day Success Targets:</strong>
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={4}>
                      <Typography variant="body2">
                        <strong>Enrollment Increase:</strong> +8-12%
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Typography variant="body2">
                        <strong>Refund/Default Reduction:</strong> {
                          solutions?.combined_impact?.churn_reduction || '-15%'
                        }
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Typography variant="body2">
                        <strong>Revenue Protection:</strong> {
                          solutions?.combined_impact?.revenue_protection || '₹52L+ annually'
                        }
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );

  const renderLiveDemoTab = () => (
    <Box>
      <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 3, display: 'flex', alignItems: 'center' }}>
        <DashboardIcon color="primary" sx={{ mr: 2 }} />
        🚀 Live Demo - Pricing Optimization Dashboard
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Real-Time Demo:</strong> ML-powered pricing optimization using{' '}
          <Chip 
            size="small" 
            color="success" 
            label={dashboardData?.dashboard?.data_points ? `${dashboardData.dashboard.data_points} Real Records` : 'Live Data'} 
            sx={{ mx: 0.5 }} 
          />
          from your MongoDB database with segment-aware plan recommendations, 
          scholarship automation, and churn risk assessment for maximized revenue quality.
        </Typography>
      </Alert>

      {/* Demo Controls */}
      <Box display="flex" gap={2} mb={3} alignItems="center" flexWrap="wrap">
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Time Range</InputLabel>
          <Select
            value={timeRange}
            label="Time Range"
            onChange={(e) => {
              setTimeRange(e.target.value);
              setTimeout(handleDemoSettingsChange, 100);
            }}
          >
            <MenuItem value="7d">7 Days</MenuItem>
            <MenuItem value="30d">30 Days</MenuItem>
            <MenuItem value="90d">90 Days</MenuItem>
          </Select>
        </FormControl>
        
        <FormControlLabel
          control={
            <Switch
              checked={includeAnomalies}
              onChange={(e) => {
                setIncludeAnomalies(e.target.checked);
                setTimeout(handleDemoSettingsChange, 100);
              }}
            />
          }
          label="Include Anomalies"
        />
        
        <Button variant="outlined" onClick={refreshCurrentTab} disabled={loading}>
          <RefreshIcon sx={{ mr: 1 }} />
          Refresh Real Data
        </Button>
        
        {dashboardData?.last_updated && (
          <Chip 
            label={`Updated: ${new Date(dashboardData.last_updated).toLocaleTimeString()}`}
            variant="outlined"
            size="small"
            color="info"
          />
        )}
      </Box>

      {dashboardData?.dashboard && (
        <Grid container spacing={3}>
          {/* Business Health Score */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <SpeedIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">Pricing Optimization Health</Typography>
                </Box>
                
                <Box display="flex" alignItems="center" mb={2}>
                  <Typography variant="h2" color="primary.main" sx={{ mr: 2 }}>
                    {dashboardData.dashboard.business_health.overall_health_score}%
                  </Typography>
                  <Chip 
                    label={dashboardData.dashboard.business_health.health_grade}
                    color={dashboardData.dashboard.business_health.overall_health_score >= 70 ? 'success' : 'warning'}
                  />
                </Box>
                
                <LinearProgress 
                  variant="determinate" 
                  value={dashboardData.dashboard.business_health.overall_health_score} 
                  sx={{ mb: 2, height: 8, borderRadius: 1 }}
                />

                <Typography variant="subtitle2" gutterBottom>Component Scores:</Typography>
                {Object.entries(dashboardData.dashboard.business_health.component_scores || {}).map(([key, value]) => (
                  <Box key={key} display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2">
                      {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                    </Typography>
                    <Typography variant="body2" fontWeight="bold" color="primary.main">
                      {value}%
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>

          {/* Key Pricing Metrics */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <MonetizationOnIcon sx={{ mr: 1, color: 'success.main' }} />
                  <Typography variant="h6">Key Pricing Metrics</Typography>
                </Box>
                
                <Grid container spacing={2}>
                  {Object.entries(dashboardData.dashboard.key_metrics || {}).map(([key, value]) => (
                    <Grid item xs={12} sm={6} key={key}>
                      <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#f8f9fa' }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </Typography>
                        <Typography variant="h6" color="primary.main" fontWeight="bold">
                          {value}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Performance Trends */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <TrendingUpIcon sx={{ mr: 1, color: 'info.main' }} />
                  <Typography variant="h6">Performance Trends</Typography>
                </Box>
                
                <List>
                  {Object.entries(dashboardData.dashboard.trends || {}).map(([key, value]) => (
                    <ListItem key={key} sx={{ px: 0 }}>
                      <ListItemIcon>
                        {value > 0 ? (
                          <TrendingUpIcon color="success" />
                        ) : (
                          <TrendingUpIcon color="error" sx={{ transform: 'scaleY(-1)' }} />
                        )}
                      </ListItemIcon>
                      <ListItemText
                        primary={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        secondary={`${value > 0 ? '+' : ''}${(value * 100).toFixed(1)}%`}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Anomaly Detection */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <WarningIcon sx={{ mr: 1, color: 'warning.main' }} />
                  <Typography variant="h6">Pricing Anomalies</Typography>
                </Box>
                
                <Box display="flex" alignItems="center" mb={2}>
                  <Badge badgeContent={dashboardData.dashboard.anomalies.total_anomalies} color="error">
                    <WarningIcon color="warning" />
                  </Badge>
                  <Typography variant="h4" sx={{ ml: 2 }}>
                    {dashboardData.dashboard.anomalies.total_anomalies}
                  </Typography>
                  <Typography variant="body1" sx={{ ml: 1 }}>
                    anomalies detected
                  </Typography>
                </Box>
                
                {dashboardData.dashboard.anomalies.total_anomalies > 0 && (
                  <Typography variant="body2" color="text.secondary">
                    Anomaly severity levels: {dashboardData.dashboard.anomalies.severity_levels.join(', ')}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Plan Performance Analysis */}
          {dashboardData.plan_performance && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                    <SchoolIcon sx={{ mr: 1, color: 'secondary.main' }} />
                    Plan Performance Analysis
                  </Typography>
                  
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                          <TableCell><strong>Plan Type</strong></TableCell>
                          <TableCell align="center"><strong>Conversion Rate</strong></TableCell>
                          <TableCell align="center"><strong>Churn Rate</strong></TableCell>
                          <TableCell align="center"><strong>Avg Revenue</strong></TableCell>
                          <TableCell align="center"><strong>Total Users</strong></TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {Object.entries(dashboardData.plan_performance).map(([planType, performance]) => (
                          <TableRow key={planType}>
                            <TableCell>
                              <Typography variant="body2" fontWeight="bold">
                                {planType.replace(/_/g, ' ').toUpperCase()}
                              </Typography>
                            </TableCell>
                            <TableCell align="center">
                              <Typography variant="body2" color="success.main">
                                {(performance.conversion_rate * 100).toFixed(1)}%
                              </Typography>
                            </TableCell>
                            <TableCell align="center">
                              <Typography variant="body2" color="error.main">
                                {(performance.churn_rate * 100).toFixed(1)}%
                              </Typography>
                            </TableCell>
                            <TableCell align="center">
                              <Typography variant="body2">
                                ₹{performance.avg_revenue.toLocaleString()}
                              </Typography>
                            </TableCell>
                            <TableCell align="center">
                              <Typography variant="body2">
                                {performance.total}
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Data Quality Metrics */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                  <CheckCircleIcon sx={{ mr: 1, color: 'success.main' }} />
                  Data Quality & System Status
                </Typography>
                
                <Grid container spacing={2}>
                  {Object.entries(dashboardData.dashboard.data_quality || {}).map(([key, value]) => (
                    <Grid item xs={6} md={3} key={key}>
                      <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#e8f5e8' }}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {key.replace(/([A-Z])/g, ' $1').trim().toUpperCase()}
                        </Typography>
                        <Typography variant="h6" color="success.main" fontWeight="bold">
                          {value}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Box display="flex" alignItems="center" mb={3}>
        <AttachMoneyIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
        <Box flexGrow={1}>
          <Typography variant="h4" component="h1" fontWeight="bold">
            PriceSense Analytics
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            AI-Powered Pricing Optimization with Segment-Aware Plan Recommendations
          </Typography>
        </Box>
        
        {/* Real Data Indicator */}
        {(dashboardData?.dashboard?.data_points || problemAnalysis || solutions) && (
          <Box>
            <Chip 
              icon={<CheckCircleIcon />}
              label={dashboardData?.dashboard?.data_points ? 
                `Live Data: ${dashboardData.dashboard.data_points} Records` : 
                'Real MongoDB Data'
              }
              color="success"
              variant="outlined"
              sx={{ mb: 1 }}
            />
            {dashboardData?.last_updated && (
              <Typography variant="caption" display="block" color="text.secondary">
                Last updated: {new Date(dashboardData.last_updated).toLocaleString()}
              </Typography>
            )}
          </Box>
        )}
      </Box>

      {/* Tab Navigation */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs 
          value={currentTab} 
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{
            '& .MuiTab-root': {
              minHeight: 72,
              textTransform: 'none',
              fontSize: '1rem',
              fontWeight: 600,
            },
          }}
        >
          <Tab 
            label={
              <Box textAlign="center">
                <PsychologyIcon sx={{ display: 'block', mx: 'auto', mb: 0.5 }} />
                Diagnose Problems
              </Box>
            } 
            {...a11yProps(0)} 
          />
          <Tab 
            label={
              <Box textAlign="center">
                <AttachMoneyIcon sx={{ display: 'block', mx: 'auto', mb: 0.5 }} />
                Propose Solutions
              </Box>
            } 
            {...a11yProps(1)} 
          />
          <Tab 
            label={
              <Box textAlign="center">
                <AssessmentIcon sx={{ display: 'block', mx: 'auto', mb: 0.5 }} />
                Prioritize & Justify
              </Box>
            } 
            {...a11yProps(2)} 
          />
          <Tab 
            label={
              <Box textAlign="center">
                <DashboardIcon sx={{ display: 'block', mx: 'auto', mb: 0.5 }} />
                Live Demo
              </Box>
            } 
            {...a11yProps(3)} 
          />
        </Tabs>
      </Box>

      {/* Loading indicator */}
      {loading && (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      )}

      {/* Error display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Tab Panels */}
      <TabPanel value={currentTab} index={0}>
        {renderProblemsTab()}
      </TabPanel>

      <TabPanel value={currentTab} index={1}>
        {renderSolutionsTab()}
      </TabPanel>

      <TabPanel value={currentTab} index={2}>
        {renderPrioritizationTab()}
      </TabPanel>

      <TabPanel value={currentTab} index={3}>
        {renderLiveDemoTab()}
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

export default PriceSense;
