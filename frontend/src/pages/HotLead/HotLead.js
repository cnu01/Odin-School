import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Button,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Alert,
  Badge,
  Divider,
  Tabs,
  Tab,
  LinearProgress,
  CircularProgress,
  Snackbar,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Phone,
  Email,
  Assignment,
  Visibility,
  FilterList,
  Search,
  SmartToy,
  Psychology,
  TrendingUp,
  AutoFixHigh,
  Refresh,
  ModelTraining,
  Science,
  Bolt,
  Speed,
  Timeline,
  AccountTree,
  Assessment,
  CheckCircle,
  BuildCircle,
  Insights,
  RocketLaunch,
  MonetizationOn,
  Architecture,
} from '@mui/icons-material';
import hotleadService from '../../services/hotleadService';

function HotLead() {
  const [priorityLeads, setPriorityLeads] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const [selectedLead, setSelectedLead] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterScore, setFilterScore] = useState('all');
  const [leadExplanation, setLeadExplanation] = useState(null);
  const [outreachMessage, setOutreachMessage] = useState('');
  const [modelTraining, setModelTraining] = useState(false);
  const [problemAnalysis, setProblemAnalysis] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [aiSolutions, setAiSolutions] = useState(null);
  const [aiSolutionsLoading, setAiSolutionsLoading] = useState(false);
  
  // Create Lead state
  const [newLeadData, setNewLeadData] = useState({
    email: '',
    phone: '',
    source: 'organic',
    location: '',
    page_views: 5,
    time_on_site: 180,
    demo_requests: 0,
    first_name: '',
    last_name: '',
    course_pages_viewed: 2,
    downloads_count: 1,
    form_submissions: 1,
    device: 'desktop',
    is_return_visitor: false
  });
  const [createLeadLoading, setCreateLeadLoading] = useState(false);
  const [createdLeadResult, setCreatedLeadResult] = useState(null);

  // State to track which tabs have been loaded
  const [loadedTabs, setLoadedTabs] = useState({ 0: false, 1: false, 2: false, 3: false });

  // Load data on component mount
  useEffect(() => {
    loadInitialData();
  }, []);

  // Handle tab changes and lazy load data
  useEffect(() => {
    if (!loadedTabs[tabValue]) {
      loadTabData(tabValue);
    }
  }, [tabValue, loadedTabs]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      // Only load essential data on initial load
      const [priorityResponse, statusResponse] = await Promise.all([
        hotleadService.getPriorityQueue({ limit: 20, min_score: 0 }),
        hotleadService.getSystemStatus()
      ]);

      if (priorityResponse.success) {
        setPriorityLeads(priorityResponse.data.leads || []);
      }

      if (statusResponse.success) {
        setSystemStatus(statusResponse.data);
      }

      // Mark first tab as loaded
      setLoadedTabs(prev => ({ ...prev, 0: true }));

    } catch (err) {
      setError('Failed to load HotLead data');
      console.error('Error loading HotLead data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadTabData = async (tabIndex) => {
    if (loadedTabs[tabIndex]) return;

    try {
      switch (tabIndex) {
        case 0: // Priority Queue tab - already loaded in initial
          break;
        case 1: // Analytics tab
          await loadAnalytics();
          await loadProblemAnalysis();
          await loadAISolutions();
          break;
        case 2: // Priority Queue with Create Lead form
          // No additional data needed
          break;
        case 3: // AI Solutions tab
          if (!aiSolutions) {
            await loadAISolutions();
          }
          break;
        default:
          break;
      }

      setLoadedTabs(prev => ({ ...prev, [tabIndex]: true }));
    } catch (err) {
      console.error(`Error loading data for tab ${tabIndex}:`, err);
    }
  };

  const loadAnalytics = async () => {
    if (analytics) return; // Already loaded

    try {
      const analyticsResponse = await hotleadService.getAnalytics();
      if (analyticsResponse.success) {
        setAnalytics(analyticsResponse.data);
      }
    } catch (err) {
      console.error('Error loading analytics:', err);
    }
  };

  const loadData = async () => {
    // Refresh all data (used for manual refresh)
    try {
      setLoading(true);
      const [priorityResponse, analyticsResponse, statusResponse] = await Promise.all([
        hotleadService.getPriorityQueue({ limit: 20, min_score: 0 }),
        hotleadService.getAnalytics(),
        hotleadService.getSystemStatus()
      ]);

      if (priorityResponse.success) {
        setPriorityLeads(priorityResponse.data.leads || []);
      }

      if (analyticsResponse.success) {
        setAnalytics(analyticsResponse.data);
      }

      if (statusResponse.success) {
        setSystemStatus(statusResponse.data);
      }

    } catch (err) {
      setError('Failed to load HotLead data');
      console.error('Error loading HotLead data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadProblemAnalysis = async (forceRefresh = false) => {
    try {
      setAnalysisLoading(true);
      const response = await hotleadService.getProblemAnalysis(forceRefresh);
      
      if (response.success) {
        setProblemAnalysis(response.data);
      }
    } catch (err) {
      console.error('Error loading problem analysis:', err);
    } finally {
      setAnalysisLoading(false);
    }
  };

  const loadAISolutions = async () => {
    try {
      setAiSolutionsLoading(true);
      const response = await hotleadService.getAISolutions();
      
      if (response.success) {
        setAiSolutions(response.data);
      }
    } catch (err) {
      console.error('Error loading AI Solutions:', err);
    } finally {
      setAiSolutionsLoading(false);
    }
  };

  const handleLeadClick = async (lead) => {
    setSelectedLead(lead);
    setDialogOpen(true);
    
    // Get lead explanation
    try {
      const explanationResponse = await hotleadService.explainLeadPriority(lead.lead_id);
      if (explanationResponse.success) {
        setLeadExplanation(explanationResponse.data);
      }
    } catch (err) {
      console.error('Error getting lead explanation:', err);
    }
  };

  const handleGenerateOutreach = async (leadId) => {
    try {
      const response = await hotleadService.generateOutreachMessage({
        lead_id: leadId,
        rep_name: 'Sales Team',
        contact_method: 'email'
      });
      
      if (response.success) {
        setOutreachMessage(response.data.message);
        setSnackbarMessage('Outreach message generated successfully!');
        setSnackbarOpen(true);
      } else {
        setSnackbarMessage('Failed to generate outreach message');
        setSnackbarOpen(true);
      }
    } catch (err) {
      console.error('Error generating outreach:', err);
      setSnackbarMessage('Error generating outreach message');
      setSnackbarOpen(true);
    }
  };

  const handleContactUpdate = async (leadId, contactData) => {
    try {
      const response = await hotleadService.updateContactStatus({
        lead_id: leadId,
        contacted_by: 'current_user',
        contact_method: contactData.method,
        notes: contactData.notes,
        outcome: contactData.outcome
      });
      
      if (response.success) {
        setSnackbarMessage('Contact status updated successfully!');
        setSnackbarOpen(true);
        loadData(); // Refresh data
      } else {
        setSnackbarMessage('Failed to update contact status');
        setSnackbarOpen(true);
      }
    } catch (err) {
      console.error('Error updating contact:', err);
      setSnackbarMessage('Error updating contact status');
      setSnackbarOpen(true);
    }
  };

  // const handleTrainModel = async () => {
  //   try {
  //     setModelTraining(true);
  //     const response = await hotleadService.trainModel(2000);
      
  //     if (response.success) {
  //       setSnackbarMessage(`Model trained successfully! Accuracy: ${(response.data.metrics?.accuracy * 100).toFixed(1)}%`);
  //       setSnackbarOpen(true);
  //       // Refresh system status
  //       const statusResponse = await hotleadService.getSystemStatus();
  //       if (statusResponse.success) {
  //         setSystemStatus(statusResponse.data);
  //       }
  //     } else {
  //       setSnackbarMessage('Failed to train model');
  //       setSnackbarOpen(true);
  //     }
  //   } catch (err) {
  //     console.error('Error training model:', err);
  //     setSnackbarMessage('Error training model');
  //     setSnackbarOpen(true);
  //   } finally {
  //     setModelTraining(false);
  //   }
  // };

  // const handleSeedDatabase = async () => {
  //   try {
  //     setLoading(true);
  //     const response = await hotleadService.seedDatabase(1000);
      
  //     if (response.success) {
  //       setSnackbarMessage(`Database seeded with ${response.data.total_leads} leads. Conversion rate: ${response.data.conversion_rate}`);
  //       setSnackbarOpen(true);
  //       loadData(); // Refresh data
  //     } else {
  //       setSnackbarMessage('Failed to seed database');
  //       setSnackbarOpen(true);
  //     }
  //   } catch (err) {
  //     console.error('Error seeding database:', err);
  //     setSnackbarMessage('Error seeding database');
  //     setSnackbarOpen(true);
  //   } finally {
  //     setLoading(false);
  //   }
  // };

  const handleAnalyzeProblems = async () => {
    await loadProblemAnalysis(true); // Force refresh
    setSnackbarMessage('Problem analysis updated with fresh data!');
    setSnackbarOpen(true);
  };

  const handleLoadAISolutions = async () => {
    await loadAISolutions();
    setSnackbarMessage('AI Solutions updated!');
    setSnackbarOpen(true);
  };

  // Create Lead handlers
  const handleLeadInputChange = (event) => {
    const { name, value } = event.target;
    setNewLeadData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFillSampleData = () => {
    const sampleData = {
      email: 'rahul.student@gmail.com',
      phone: '+91-9876543210',
      source: 'organic',
      location: 'Mumbai, India',
      page_views: 8,
      time_on_site: 245,
      demo_requests: 1,
      first_name: 'Rahul',
      last_name: 'Sharma',
      course_pages_viewed: 3,
      downloads_count: 2,
      form_submissions: 1,
      device: 'desktop',
      is_return_visitor: false
    };
    setNewLeadData(sampleData);
  };

  const handleCreateLead = async (event) => {
    event.preventDefault();
    try {
      setCreateLeadLoading(true);
      setCreatedLeadResult(null);
      
      const response = await hotleadService.ingestLead(newLeadData);
      
      if (response.success) {
        setCreatedLeadResult(response.data);
        setSnackbarMessage('Lead created and scored successfully!');
        setSnackbarOpen(true);
        
        // Refresh priority queue to show the new lead
        loadData();
      } else {
        setSnackbarMessage(`Failed to create lead: ${response.error}`);
        setSnackbarOpen(true);
      }
    } catch (err) {
      console.error('Error creating lead:', err);
      setSnackbarMessage('Error creating lead');
      setSnackbarOpen(true);
    } finally {
      setCreateLeadLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'error'; // Hot
    if (score >= 70) return 'warning'; // Warm
    return 'default'; // Cold
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Hot';
    if (score >= 70) return 'Warm';
    return 'Cold';
  };

  const getStatusColor = (status) => {
    const colors = {
      new: 'primary',
      contacted: 'info',
      meeting_booked: 'success',
      enrolled: 'success',
      lost: 'error',
    };
    return colors[status] || 'default';
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const past = new Date(timestamp);
    const diffInMinutes = Math.floor((now - past) / (1000 * 60));
    
    if (diffInMinutes < 60) {
      return `${diffInMinutes} minutes ago`;
    } else if (diffInMinutes < 1440) {
      return `${Math.floor(diffInMinutes / 60)} hours ago`;
    } else {
      return `${Math.floor(diffInMinutes / 1440)} days ago`;
    }
  };

  const filteredLeads = priorityLeads.filter(lead => {
    const statusMatch = filterStatus === 'all' || lead.status === filterStatus;
    const scoreMatch = filterScore === 'all' || 
      (filterScore === 'hot' && lead.priority_score >= 80) ||
      (filterScore === 'warm' && lead.priority_score >= 70 && lead.priority_score < 80) ||
      (filterScore === 'cold' && lead.priority_score < 70);
    return statusMatch && scoreMatch;
  });

  const LeadDetailDialog = () => (
    <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar sx={{ bgcolor: 'primary.main' }}>
            {selectedLead?.email?.charAt(0).toUpperCase()}
          </Avatar>
          <Box>
            <Typography variant="h6">{selectedLead?.email}</Typography>
            <Typography variant="body2" color="text.secondary">
              Lead ID: {selectedLead?.lead_id}
            </Typography>
          </Box>
          <Box sx={{ ml: 'auto' }}>
            <Chip
              label={`${selectedLead?.priority_score}/100`}
              color={getScoreColor(selectedLead?.priority_score)}
              variant="filled"
            />
          </Box>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Grid container spacing={3}>
          {/* AI-Generated Summary */}
          <Grid item xs={12}>
            <Alert severity="info" icon={<Psychology />}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                AI Lead Analysis
              </Typography>
              <Typography variant="body2">
                <strong>{selectedLead?.lead_temperature}:</strong> Conversion probability {(selectedLead?.conversion_probability * 100).toFixed(1)}%.
                Source: {selectedLead?.source}, {selectedLead?.page_views} page views, {selectedLead?.time_on_site}s on site.
              </Typography>
            </Alert>
          </Grid>

          {/* Lead Explanation */}
          {leadExplanation && (
            <Grid item xs={12}>
              <Card sx={{ backgroundColor: 'success.50', border: '1px solid', borderColor: 'success.200' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <AutoFixHigh sx={{ color: 'success.main', mr: 1 }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'success.main' }}>
                      Why This Lead is Prioritized
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    {leadExplanation.explanation}
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    Recommended Action: {leadExplanation.recommended_action}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* AI-Generated Outreach */}
          {outreachMessage && (
            <Grid item xs={12}>
              <Card sx={{ backgroundColor: 'info.50', border: '1px solid', borderColor: 'info.200' }}>
                <CardContent>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2, color: 'info.main' }}>
                    AI-Generated Outreach Message
                  </Typography>
                  <Typography variant="body2" sx={{ 
                    backgroundColor: 'white', 
                    p: 2, 
                    borderRadius: 1,
                    fontStyle: 'italic'
                  }}>
                    {outreachMessage}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Lead Information */}
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
              Lead Details
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Email:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {selectedLead?.email}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Phone:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {selectedLead?.phone || 'Not provided'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Location:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {selectedLead?.location || 'Unknown'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Source:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {selectedLead?.source}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Status:</Typography>
                <Chip
                  label={selectedLead?.status}
                  color={getStatusColor(selectedLead?.status)}
                  size="small"
                />
              </Box>
            </Box>
          </Grid>

          {/* Behavioral Data */}
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
              Engagement Metrics
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Page Views:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {selectedLead?.page_views}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Time on Site:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {Math.floor(selectedLead?.time_on_site / 60)}m {selectedLead?.time_on_site % 60}s
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Course Pages:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {selectedLead?.course_pages_viewed || 0}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Downloads:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {selectedLead?.downloads_count || 0}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Demo Requests:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {selectedLead?.demo_requests || 0}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Device:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {selectedLead?.device || 'Unknown'}
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={() => setDialogOpen(false)}>Close</Button>
        <Button 
          variant="outlined" 
          startIcon={<AutoFixHigh />}
          onClick={() => handleGenerateOutreach(selectedLead?.lead_id)}
        >
          Generate Message
        </Button>
        <Button 
          variant="contained" 
          startIcon={<Phone />}
          onClick={() => handleContactUpdate(selectedLead?.lead_id, { method: 'phone', outcome: 'contacted' })}
        >
          Mark as Contacted
        </Button>
      </DialogActions>
    </Dialog>
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
            HotLead AI System
          </Typography>
          <Typography variant="body2" color="text.secondary">
            ML-Powered Lead Scoring • Priority Queue • Intelligent Routing
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button 
            variant="outlined" 
            startIcon={<Refresh />} 
            onClick={loadData}
          >
            Refresh
          </Button>
          {/* <Button 
            variant="outlined" 
            startIcon={<ModelTraining />}
            onClick={handleTrainModel}
            disabled={modelTraining}
          >
            {modelTraining ? 'Training...' : 'Train Model'}
          </Button> */}
          {/* <Button 
            variant="contained" 
            startIcon={<Science />}
            onClick={handleSeedDatabase}
          >
            Seed Database
          </Button> */}
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* System Status */}
      {/* {systemStatus && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="h6">System Status</Typography>
                <Typography variant="body2" color="text.secondary">
                  {systemStatus.system} - Version {systemStatus.version}
                </Typography>
              </Box>
              <Chip 
                label={systemStatus.status} 
                color="success" 
                variant="filled"
              />
            </Box>
          </CardContent>
        </Card>
      )} */}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Problem Diagnosis" />
          <Tab label="AI Solutions" />
          <Tab label="Priority Queue" />
          <Tab label="Analytics" />
          {/* <Tab label="Model Info" /> */}
        </Tabs>
      </Box>

      {/* Problem Diagnosis Tab */}
      {tabValue === 0 && (
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 3, display: 'flex', alignItems: 'center' }}>
            <SmartToy color="primary" sx={{ mr: 2 }} />
            AI-Powered Problem Diagnosis
          </Typography>
          
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>OdinSchool Business Context:</strong> EdTech platform with 600+ hiring partners. 
              Challenge: Converting website traffic to paid enrollments efficiently with healthy traffic but uneven conversion patterns.
            </Typography>
          </Alert>

          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  Real Lead Data Analysis
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Psychology />}
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

              {analysisLoading && (
                <Box sx={{ mb: 3 }}>
                  <LinearProgress />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    AI is analyzing 150 random leads from DB...
                  </Typography>
                </Box>
              )}

              {problemAnalysis && (
                <Box>
                  <Typography variant="h6" sx={{ mb: 3, color: 'success.main' }}>
                    ✅ Analysis Complete - Problems Identified:
                  </Typography>
                  
                  <Grid container spacing={3}>
                    {problemAnalysis.diagnosed_problems?.map((problem, index) => (
                      <Grid item xs={12} md={6} key={problem.problem_id}>
                        <Card sx={{ 
                          height: '100%',
                          borderLeft: '4px solid',
                          borderColor: index === 0 ? 'error.main' : 'warning.main',
                          bgcolor: index === 0 ? 'error.50' : 'warning.50'
                        }}>
                          <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                              <Chip 
                                label={`Problem ${index + 1}`}
                                color={index === 0 ? 'error' : 'warning'}
                                size="small"
                                sx={{ mr: 2 }}
                              />
                              <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1rem' }}>
                                {problem.title}
                              </Typography>
                            </Box>
                            
                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'primary.main' }}>
                                🔍 Symptom (What we observe):
                              </Typography>
                              <Typography variant="body2" sx={{ mb: 2 }}>
                                {problem.symptom}
                              </Typography>
                            </Box>

                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'error.main' }}>
                                🎯 Root Cause (Why it's happening):
                              </Typography>
                              <Typography variant="body2" sx={{ mb: 2 }}>
                                {problem.root_cause}
                              </Typography>
                            </Box>

                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'warning.main' }}>
                                💰 Business Impact:
                              </Typography>
                              <Typography variant="body2" sx={{ mb: 2 }}>
                                {problem.impact}
                              </Typography>
                            </Box>

                            <Box>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'success.main' }}>
                                📊 Evidence from Real Data:
                              </Typography>
                              <Typography variant="body2" sx={{ 
                                bgcolor: 'white', 
                                p: 2, 
                                borderRadius: 1,
                                border: '1px solid',
                                borderColor: 'grey.300'
                              }}>
                                {problem.evidence}
                              </Typography>
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>

                  {/* Implementation Status */}
                  {/* {problemAnalysis.implementation_status && (
                    <Card sx={{ mt: 3, bgcolor: 'primary.50' }}>
                      <CardContent>
                        <Typography variant="h6" sx={{ mb: 2 }}>
                          🛠️ Implementation Status
                        </Typography>
                        <Grid container spacing={2}>
                          {Object.entries(problemAnalysis.implementation_status).map(([key, status]) => (
                            <Grid item xs={12} md={6} key={key}>
                              <Typography variant="body2">
                                <strong>{key.replace(/_/g, ' ').toUpperCase()}:</strong> {status}
                              </Typography>
                            </Grid>
                          ))}
                        </Grid>
                      </CardContent>
                    </Card>
                  )} */}
                </Box>
              )}

              {!problemAnalysis && !analysisLoading && (
                <Alert severity="info">
                  <Typography variant="body2">
                    Click "Analyze Problems" to get AI-powered insights from your real lead data in MongoDB.
                    LLM will analyze patterns, identify issues, and provide evidence-based recommendations.
                  </Typography>
                </Alert>
              )}
            </CardContent>
          </Card>
        </Box>
      )}

      {/* AI Solutions Tab */}
      {tabValue === 1 && (
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 3, display: 'flex', alignItems: 'center' }}>
            <RocketLaunch color="primary" sx={{ mr: 2 }} />
            AI Solutions: Lead Scoring & Prioritization
          </Typography>
          
          <Alert severity="success" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>Live AI Systems:</strong> ML-powered lead scoring (72.5% accuracy), Dynamic priority routing, 
              Claude-powered problem analysis. Plus 2 proposed enhancements for faster lead prioritization.
            </Typography>
          </Alert>

          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  Current AI Implementation & Proposed Solutions
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Bolt />}
                  onClick={handleLoadAISolutions}
                  disabled={aiSolutionsLoading}
                  sx={{ minWidth: 180 }}
                >
                  {aiSolutionsLoading ? (
                    <>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      Loading...
                    </>
                  ) : (
                    'Load AI Solutions'
                  )}
                </Button>
              </Box>

              {aiSolutionsLoading && (
                <Box sx={{ mb: 3 }}>
                  <LinearProgress />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Loading implemented AI solutions and lead scoring recommendations...
                  </Typography>
                </Box>
              )}

              {aiSolutions && (
                <Box>
                  {/* Current AI Solutions */}
                  <Typography variant="h6" sx={{ mb: 3, color: 'success.main', display: 'flex', alignItems: 'center' }}>
                    <CheckCircle sx={{ mr: 1 }} />
                    Currently Implemented AI Solutions
                  </Typography>
                  
                  <Grid container spacing={3} sx={{ mb: 4 }}>
                    {aiSolutions.solutions?.filter(sol => sol.current_status.includes('✅')).map((solution, index) => (
                      <Grid item xs={12} md={6} lg={4} key={solution.solution_id}>
                        <Card sx={{ 
                          height: '100%',
                          borderTop: '4px solid',
                          borderTopColor: 'success.main',
                          bgcolor: 'success.50'
                        }}>
                          <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                              <Chip 
                                label={solution.current_status}
                                color="success"
                                size="small"
                                sx={{ mr: 1 }}
                              />
                              <Chip 
                                label={`${solution.confidence_score * 100}% accuracy`}
                                variant="outlined"
                                size="small"
                              />
                            </Box>
                            
                            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, fontSize: '1rem' }}>
                              {solution.title}
                            </Typography>
                            
                            <Typography variant="body2" sx={{ mb: 2, lineHeight: 1.5 }}>
                              {solution.description}
                            </Typography>

                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'primary.main' }}>
                                🎯 Problem Solved:
                              </Typography>
                              <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
                                {solution.problem_addressed}
                              </Typography>
                            </Box>

                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'success.main' }}>
                                📊 Current Impact:
                              </Typography>
                              <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                                {solution.expected_impact}
                              </Typography>
                            </Box>

                            {solution.success_metrics && solution.success_metrics.length > 0 && (
                              <Box>
                                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'info.main' }}>
                                  ✅ Success Metrics:
                                </Typography>
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                  {solution.success_metrics.slice(0, 3).map((metric, i) => (
                                    <Chip 
                                      key={i}
                                      label={metric}
                                      size="small"
                                      variant="outlined"
                                      color="success"
                                    />
                                  ))}
                                </Box>
                              </Box>
                            )}
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>

                  {/* Proposed AI Enhancements */}
                  <Typography variant="h6" sx={{ mb: 3, color: 'primary.main', display: 'flex', alignItems: 'center' }}>
                    <RocketLaunch sx={{ mr: 1 }} />
                    Proposed AI-Driven Lead Scoring Enhancements
                  </Typography>
                  
                  <Grid container spacing={3} sx={{ mb: 4 }}>
                    {aiSolutions.solutions?.filter(sol => sol.current_status === 'Ready to Implement').map((solution, index) => (
                      <Grid item xs={12} md={6} key={solution.solution_id}>
                        <Card sx={{ 
                          height: '100%',
                          borderTop: '4px solid',
                          borderTopColor: 'primary.main',
                          bgcolor: 'primary.50'
                        }}>
                          <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                              <Chip 
                                label={solution.current_status}
                                color="primary"
                                size="small"
                                sx={{ mr: 1 }}
                              />
                              <Chip 
                                label={`${solution.timeline_weeks} weeks`}
                                variant="outlined"
                                size="small"
                              />
                            </Box>
                            
                            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2, fontSize: '1.1rem' }}>
                              {solution.title}
                            </Typography>
                            
                            <Typography variant="body2" sx={{ mb: 2, lineHeight: 1.5 }}>
                              {solution.description}
                            </Typography>

                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'error.main' }}>
                                ⚠️ Problem to Solve:
                              </Typography>
                              <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
                                {solution.problem_addressed}
                              </Typography>
                            </Box>

                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'success.main' }}>
                                📈 Expected Impact:
                              </Typography>
                              <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                                {solution.expected_impact}
                              </Typography>
                            </Box>

                            <Box>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'info.main' }}>
                                🔧 Technical Requirements:
                              </Typography>
                              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                {solution.technical_requirements?.slice(0, 3).map((req, i) => (
                                  <Chip 
                                    key={i}
                                    label={req}
                                    size="small"
                                    variant="outlined"
                                    color="info"
                                  />
                                ))}
                              </Box>
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>

                  {/* Fast Routing Implementation */}
                  {aiSolutions.implementation_roadmap && (
                    <Card sx={{ bgcolor: 'info.50', borderLeft: '4px solid', borderLeftColor: 'info.main' }}>
                      <CardContent>
                        <Typography variant="h6" sx={{ mb: 3, color: 'info.main', display: 'flex', alignItems: 'center' }}>
                          <Speed sx={{ mr: 1 }} />
                          Fast Routing for Top Leads
                        </Typography>

                        {aiSolutions.implementation_roadmap.current_fast_routing && (
                          <Box sx={{ mb: 3 }}>
                            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, color: 'success.main' }}>
                              ✅ Currently Implemented:
                            </Typography>
                            <Typography variant="body2" sx={{ mb: 2 }}>
                              {aiSolutions.implementation_roadmap.current_fast_routing.description}
                            </Typography>
                            
                            <Grid container spacing={2}>
                              <Grid item xs={12} md={6}>
                                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                                  Features:
                                </Typography>
                                {aiSolutions.implementation_roadmap.current_fast_routing.features?.map((feature, i) => (
                                  <Typography key={i} variant="body2" sx={{ ml: 2, mb: 0.5 }}>
                                    {feature}
                                  </Typography>
                                ))}
                              </Grid>
                              <Grid item xs={12} md={6}>
                                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                                  Performance:
                                </Typography>
                                {Object.entries(aiSolutions.implementation_roadmap.current_fast_routing.performance || {}).map(([key, value]) => (
                                  <Typography key={key} variant="body2" sx={{ ml: 2, mb: 0.5 }}>
                                    <strong>{key.replace(/_/g, ' ')}:</strong> {value}
                                  </Typography>
                                ))}
                              </Grid>
                            </Grid>
                          </Box>
                        )}

                        {aiSolutions.implementation_roadmap.proposed_enhancements && (
                          <Box>
                            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, color: 'primary.main' }}>
                              🚀 Proposed Enhancements:
                            </Typography>
                            <Grid container spacing={2}>
                              {Object.entries(aiSolutions.implementation_roadmap.proposed_enhancements).map(([key, enhancement]) => (
                                <Grid item xs={12} md={6} key={key}>
                                  <Card variant="outlined">
                                    <CardContent sx={{ p: 2 }}>
                                      <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                                        {enhancement.description}
                                      </Typography>
                                      <Typography variant="body2" sx={{ mb: 1, color: 'text.secondary' }}>
                                        <strong>Implementation:</strong> {enhancement.implementation}
                                      </Typography>
                                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <Chip label={enhancement.timeline} size="small" color="warning" />
                                        <Typography variant="body2" sx={{ color: 'success.main', fontWeight: 600 }}>
                                          {enhancement.impact}
                                        </Typography>
                                      </Box>
                                    </CardContent>
                                  </Card>
                                </Grid>
                              ))}
                            </Grid>
                          </Box>
                        )}
                      </CardContent>
                    </Card>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>
      )}
      {/* Priority Queue Tab */}
      {tabValue === 2 && (
        <>
          {/* Summary Cards */}
          {analytics && (
            <Grid container spacing={3} sx={{ mb: 3 }}>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ color: 'primary.main', fontWeight: 'bold' }}>
                      {analytics.current_metrics?.total_leads_today || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Leads Today
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ color: 'error.main', fontWeight: 'bold' }}>
                      {analytics.current_metrics?.priority_leads || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Priority Leads
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ color: 'warning.main', fontWeight: 'bold' }}>
                      {analytics.current_metrics?.avg_score || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Average Score
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ color: 'success.main', fontWeight: 'bold' }}>
                      {analytics.current_metrics?.conversion_rate || 0}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Conversion Rate
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}

          {/* Filters */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Status Filter</InputLabel>
                <Select
                  value={filterStatus}
                  label="Status Filter"
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <MenuItem value="all">All Status</MenuItem>
                  <MenuItem value="new">New</MenuItem>
                  <MenuItem value="contacted">Contacted</MenuItem>
                  <MenuItem value="meeting_booked">Meeting Booked</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Score Filter</InputLabel>
                <Select
                  value={filterScore}
                  label="Score Filter"
                  onChange={(e) => setFilterScore(e.target.value)}
                >
                  <MenuItem value="all">All Scores</MenuItem>
                  <MenuItem value="hot">Hot Leads (80+)</MenuItem>
                  <MenuItem value="warm">Warm Leads (70-79)</MenuItem>
                  <MenuItem value="cold">Cold Leads (&lt;70)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          {/* Leads Table */}
          <Card>
            <CardContent sx={{ p: 0 }}>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow sx={{ backgroundColor: 'grey.50' }}>
                      <TableCell>Lead</TableCell>
                      <TableCell align="center">AI Score</TableCell>
                      <TableCell>Source</TableCell>
                      <TableCell>Status</TableCell>
                      {/* <TableCell>Temperature</TableCell> */}
                      <TableCell>Created</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredLeads.map((lead) => (
                      <TableRow key={lead.lead_id} hover>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Avatar sx={{ width: 40, height: 40, bgcolor: 'primary.main' }}>
                              {lead.email?.charAt(0).toUpperCase()}
                            </Avatar>
                            <Box>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                                {lead.email}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {lead.location || 'Unknown location'}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {lead.page_views} views • {lead.device}
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={`${lead.priority_score}/100`}
                            color={getScoreColor(lead.priority_score)}
                            variant="filled"
                            size="small"
                          />
                          <Typography variant="caption" display="block" color="text.secondary">
                            {getScoreLabel(lead.priority_score)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">{lead.source}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {(lead.conversion_probability * 100).toFixed(1)}% probability
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={lead.status}
                            color={getStatusColor(lead.status)}
                            variant="outlined"
                            size="small"
                          />
                        </TableCell>
                        {/* <TableCell>
                          <Typography variant="body2">
                            {lead.lead_temperature}
                          </Typography>
                        </TableCell> */}
                        <TableCell>
                          <Typography variant="body2">
                            {formatTimeAgo(lead.created_at)}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Box sx={{ display: 'flex', gap: 0.5 }}>
                            <IconButton size="small" color="primary">
                              <Phone />
                            </IconButton>
                            <IconButton size="small" color="primary">
                              <Email />
                            </IconButton>
                            <IconButton size="small" onClick={() => handleLeadClick(lead)}>
                              <Visibility />
                            </IconButton>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>

          {/* Test Create Lead Section */}
          <Card sx={{ mt: 4, bgcolor: 'primary.50', borderLeft: '4px solid', borderLeftColor: 'primary.main' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, color: 'primary.main', display: 'flex', alignItems: 'center' }}>
                <AutoFixHigh sx={{ mr: 1 }} />
                Test AI Lead Scoring - Create Lead
              </Typography>
              
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body2">
                  <strong>Try the AI System:</strong> Create a sample lead and see our ML model score it in real-time. 
                  The system will automatically apply our 3 implemented AI solutions and show priority scoring.
                </Typography>
              </Alert>

              <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                  <Box component="form" onSubmit={handleCreateLead} sx={{ '& .MuiTextField-root': { mb: 2 } }}>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Email"
                          name="email"
                          type="email"
                          value={newLeadData.email}
                          onChange={handleLeadInputChange}
                          required
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Phone"
                          name="phone"
                          value={newLeadData.phone}
                          onChange={handleLeadInputChange}
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <FormControl fullWidth size="small">
                          <InputLabel>Source</InputLabel>
                          <Select
                            name="source"
                            value={newLeadData.source}
                            onChange={handleLeadInputChange}
                            label="Source"
                          >
                            <MenuItem value="organic">🔍 Organic Search</MenuItem>
                            <MenuItem value="paid_search">📢 Paid Search</MenuItem>
                            <MenuItem value="social_media">📱 Social Media</MenuItem>
                            <MenuItem value="referral">👥 Referral</MenuItem>
                            <MenuItem value="email">📧 Email</MenuItem>
                            <MenuItem value="website_form">🌐 Website Form</MenuItem>
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Location"
                          name="location"
                          value={newLeadData.location}
                          onChange={handleLeadInputChange}
                          size="small"
                          placeholder="e.g., Mumbai, India"
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          label="Page Views"
                          name="page_views"
                          type="number"
                          value={newLeadData.page_views}
                          onChange={handleLeadInputChange}
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          label="Time on Site (seconds)"
                          name="time_on_site"
                          type="number"
                          value={newLeadData.time_on_site}
                          onChange={handleLeadInputChange}
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          label="Demo Requests"
                          name="demo_requests"
                          type="number"
                          value={newLeadData.demo_requests}
                          onChange={handleLeadInputChange}
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="First Name"
                          name="first_name"
                          value={newLeadData.first_name}
                          onChange={handleLeadInputChange}
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Last Name"
                          name="last_name"
                          value={newLeadData.last_name}
                          onChange={handleLeadInputChange}
                          size="small"
                        />
                      </Grid>
                    </Grid>
                    
                    <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
                      <Button
                        type="submit"
                        variant="contained"
                        startIcon={<AutoFixHigh />}
                        disabled={createLeadLoading}
                        sx={{ minWidth: 180 }}
                      >
                        {createLeadLoading ? (
                          <>
                            <CircularProgress size={20} sx={{ mr: 1 }} />
                            Scoring...
                          </>
                        ) : (
                          'Create & Score Lead'
                        )}
                      </Button>
                      
                      <Button
                        variant="outlined"
                        onClick={handleFillSampleData}
                        startIcon={<Science />}
                      >
                        Fill Sample Data
                      </Button>
                    </Box>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  {createdLeadResult && (
                    <Card sx={{ bgcolor: 'success.50', border: '2px solid', borderColor: 'success.main' }}>
                      <CardContent>
                        <Typography variant="h6" sx={{ mb: 2, color: 'success.main', display: 'flex', alignItems: 'center' }}>
                          <TrendingUp sx={{ mr: 1 }} />
                          AI Scoring Result
                        </Typography>
                        
                        <Box sx={{ textAlign: 'center', mb: 2 }}>
                          <Typography variant="h3" sx={{ color: createdLeadResult.priority_score >= 80 ? 'error.main' : createdLeadResult.priority_score >= 60 ? 'warning.main' : 'info.main', fontWeight: 'bold' }}>
                            {createdLeadResult.priority_score}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Priority Score
                          </Typography>
                        </Box>

                        <Box sx={{ mb: 2 }}>
                          <Chip 
                            label={createdLeadResult.lead_temperature}
                            color={createdLeadResult.is_priority ? 'error' : 'warning'}
                            sx={{ mb: 1, display: 'block' }}
                          />
                          <Chip 
                            label={`${Math.round(createdLeadResult.conversion_probability * 100)}% Conversion Probability`}
                            variant="outlined"
                            color="success"
                            sx={{ display: 'block' }}
                          />
                        </Box>

                        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                          AI Analysis:
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          <strong>Assigned Rep:</strong> {createdLeadResult.assigned_rep}
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          <strong>Status:</strong> {createdLeadResult.status}
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          <strong>Lead ID:</strong> {createdLeadResult.lead_id}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Created:</strong> {new Date(createdLeadResult.created_at).toLocaleString()}
                        </Typography>
                      </CardContent>
                    </Card>
                  )}
                  
                  {!createdLeadResult && (
                    <Card sx={{ bgcolor: 'grey.50' }}>
                      <CardContent sx={{ textAlign: 'center', py: 4 }}>
                        <AutoFixHigh sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
                        <Typography variant="body2" color="text.secondary">
                          Fill out the form and click "Create & Score Lead" to see our AI system in action!
                        </Typography>
                      </CardContent>
                    </Card>
                  )}
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </>
      )}

      {/* Analytics Tab */}
      {tabValue === 3 && (
        <Box>
          {/* Prioritization & Justification Analysis Section */}
          {aiSolutions?.prioritization_analysis && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h5" sx={{ mb: 3, color: 'warning.main', display: 'flex', alignItems: 'center', fontWeight: 'bold' }}>
                <Assessment sx={{ mr: 2, fontSize: 32 }} />
                Prioritize & Justify: Impact vs. Effort Analysis
              </Typography>
              
              {/* Summary Metrics */}
              <Card sx={{ mb: 3, bgcolor: 'warning.50', borderLeft: '4px solid orange' }}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, color: 'warning.dark' }}>
                    🎯 Overall Target: {aiSolutions.prioritization_analysis.summary.combined_impact}
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="text.secondary">Total Solutions</Typography>
                      <Typography variant="h4" color="primary.main">
                        {aiSolutions.prioritization_analysis.summary.total_solutions}
                      </Typography>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="text.secondary">Live Solutions</Typography>
                      <Typography variant="h4" color="success.main">
                        {aiSolutions.prioritization_analysis.summary.live_solutions}
                      </Typography>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="text.secondary">Avg Confidence</Typography>
                      <Typography variant="h4" color="info.main">
                        {(aiSolutions.prioritization_analysis.summary.avg_confidence * 100).toFixed(0)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="text.secondary">Pending Implementation</Typography>
                      <Typography variant="h4" color="warning.main">
                        {aiSolutions.prioritization_analysis.summary.pending_solutions}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>

              {/* Prioritized Solutions Table */}
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    📊 Solution Priority Ranking (Impact × Effort Analysis)
                  </Typography>
                  
                  <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
                    <Table stickyHeader>
                      <TableHead>
                        <TableRow>
                          <TableCell><strong>Rank</strong></TableCell>
                          <TableCell><strong>Solution</strong></TableCell>
                          <TableCell align="center"><strong>Priority Score</strong></TableCell>
                          <TableCell align="center"><strong>Impact</strong></TableCell>
                          <TableCell align="center"><strong>Effort</strong></TableCell>
                          <TableCell align="center"><strong>Timeline</strong></TableCell>
                          <TableCell><strong>Key Success Metric</strong></TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {aiSolutions.prioritization_analysis.prioritized_solutions.map((solution, index) => (
                          <TableRow key={solution.solution_id} sx={{ 
                            bgcolor: index < 3 ? 'success.50' : 'background.default',
                            '&:hover': { bgcolor: 'action.hover' }
                          }}>
                            <TableCell>
                              <Chip 
                                label={`#${index + 1}`}
                                color={index < 3 ? 'success' : 'default'}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>
                              <Box>
                                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                  {solution.title}
                                </Typography>
                                <Chip 
                                  label={solution.current_status}
                                  color={solution.current_status.includes('✅') ? 'success' : 'warning'}
                                  size="small"
                                  sx={{ mt: 0.5 }}
                                />
                              </Box>
                            </TableCell>
                            <TableCell align="center">
                              <Typography variant="h6" color="primary.main">
                                {solution.priority_index}
                              </Typography>
                            </TableCell>
                            <TableCell align="center">
                              <Chip 
                                label={`${solution.impact_score}%`}
                                color={solution.impact_score > 85 ? 'success' : solution.impact_score > 70 ? 'warning' : 'default'}
                                variant="outlined"
                              />
                            </TableCell>
                            <TableCell align="center">
                              <Chip 
                                label={`${solution.effort_score}%`}
                                color={solution.effort_score > 85 ? 'success' : solution.effort_score > 70 ? 'warning' : 'error'}
                                variant="outlined"
                              />
                            </TableCell>
                            <TableCell align="center">
                              <Typography variant="body2">
                                {solution.timeline_weeks === 0 ? '✅ Live' : `${solution.timeline_weeks}w`}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" sx={{ fontSize: '0.85rem' }}>
                                <strong>{solution.success_metrics?.primary_kpi || 'Implementation success'}</strong>
                                <br />
                                <span style={{ color: '#666' }}>
                                  {solution.success_metrics?.target_value || 'Successful deployment'}
                                </span>
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>

              {/* Implementation Strategy */}
              <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} md={6}>
                  <Card sx={{ height: '100%' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 2, color: 'info.main', display: 'flex', alignItems: 'center' }}>
                        <RocketLaunch sx={{ mr: 1 }} />
                        🚀 Recommended Implementation Sequence
                      </Typography>
                      {aiSolutions.prioritization_analysis.implementation_strategy.recommended_sequence.map((step, index) => (
                        <Box key={index} sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                          <Chip 
                            label={index + 1}
                            size="small"
                            color="primary"
                            sx={{ mr: 2, mt: 0.2, minWidth: '32px', height: '24px' }}
                          />
                          <Typography variant="body2" sx={{ lineHeight: 1.5, flex: 1 }}>
                            {step.replace(/^\d+\.\s*/, '')}
                          </Typography>
                        </Box>
                      ))}
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Card sx={{ height: '100%' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 2, color: 'success.main', display: 'flex', alignItems: 'center' }}>
                        <TrendingUp sx={{ mr: 1 }} />
                        📈 Success Tracking KPIs
                      </Typography>
                      {aiSolutions.prioritization_analysis.success_tracking.kpi_dashboard.map((kpi, index) => (
                        <Box key={index} sx={{ mb: 1.5 }}>
                          <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main' }}>
                            • {kpi.split('(')[0]}
                          </Typography>
                          {kpi.includes('(') && (
                            <Typography variant="body2" sx={{ color: 'text.secondary', fontSize: '0.85rem', ml: 1 }}>
                              {kpi.split('(')[1]?.replace(')', '')}
                            </Typography>
                          )}
                        </Box>
                      ))}
                      
                      <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #e0e0e0' }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                          Measurement Intervals:
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {aiSolutions.prioritization_analysis.success_tracking.measurement_intervals.map((interval, i) => (
                            <Chip 
                              key={i}
                              label={interval}
                              size="small"
                              variant="outlined"
                              color="info"
                            />
                          ))}
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}
        </Box>
      )}

          {/* Original Analytics Content */}
          {/* {analytics && (
            <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Source Performance</Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Source</TableCell>
                        <TableCell align="right">Leads</TableCell>
                        <TableCell align="right">Conv. Rate</TableCell>
                        <TableCell align="right">Avg Score</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {analytics.source_performance.map((source) => (
                        <TableRow key={source.source}>
                          <TableCell>{source.source}</TableCell>
                          <TableCell align="right">{source.leads}</TableCell>
                          <TableCell align="right">{source.conversion_rate}%</TableCell>
                          <TableCell align="right">{source.avg_score}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Success Metrics</Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box>
                    <Typography variant="body2">Meeting Booking Rate</Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={analytics.success_metrics_tracking.meeting_booking_rate} 
                      color="success"
                    />
                    <Typography variant="caption" color="text.secondary">
                      {analytics.success_metrics_tracking.meeting_booking_rate}%
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2">No-Show Reduction</Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={analytics.success_metrics_tracking.no_show_reduction} 
                      color="warning"
                    />
                    <Typography variant="caption" color="text.secondary">
                      {analytics.success_metrics_tracking.no_show_reduction}%
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2">Win Rate Improvement</Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={analytics.success_metrics_tracking.win_rate_improvement} 
                      color="info"
                    />
                    <Typography variant="caption" color="text.secondary">
                      {analytics.success_metrics_tracking.win_rate_improvement}%
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )} */}

      {/* Model Info Tab */}
      {tabValue === 4 && systemStatus && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Model Information</Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {systemStatus.ml_model && (
                    <>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2">Model Name:</Typography>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {systemStatus.ml_model.model_name}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2">Is Trained:</Typography>
                        <Chip 
                          label={systemStatus.ml_model.is_trained ? 'Yes' : 'No'}
                          color={systemStatus.ml_model.is_trained ? 'success' : 'error'}
                          size="small"
                        />
                      </Box>
                      {systemStatus.ml_model.metadata?.metrics && (
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2">Accuracy:</Typography>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {(systemStatus.ml_model.metadata.metrics.accuracy * 100).toFixed(1)}%
                          </Typography>
                        </Box>
                      )}
                    </>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>System Capabilities</Typography>
                <List>
                  {systemStatus.capabilities?.map((capability, index) => (
                    <ListItem key={index} sx={{ pl: 0 }}>
                      <ListItemText primary={capability} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <LeadDetailDialog />

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Box>
  );
}

export default HotLead;
