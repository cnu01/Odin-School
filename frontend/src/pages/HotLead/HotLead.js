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
  TrendingDown,
  Schedule,
  Person,
  LocationOn,
  Language,
  Speed,
  Timer,
  AttachMoney,
  CallMade,
  CallReceived,
  RecordVoiceOver,
  Settings,
  PlayArrow,
  Pause,
  AutoFixHigh,
  Refresh,
  ModelTraining,
  Analytics,
  Science,
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

  // Load data on component mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
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

  const handleTrainModel = async () => {
    try {
      setModelTraining(true);
      const response = await hotleadService.trainModel(2000);
      
      if (response.success) {
        setSnackbarMessage(`Model trained successfully! Accuracy: ${(response.data.metrics?.accuracy * 100).toFixed(1)}%`);
        setSnackbarOpen(true);
        // Refresh system status
        const statusResponse = await hotleadService.getSystemStatus();
        if (statusResponse.success) {
          setSystemStatus(statusResponse.data);
        }
      } else {
        setSnackbarMessage('Failed to train model');
        setSnackbarOpen(true);
      }
    } catch (err) {
      console.error('Error training model:', err);
      setSnackbarMessage('Error training model');
      setSnackbarOpen(true);
    } finally {
      setModelTraining(false);
    }
  };

  const handleSeedDatabase = async () => {
    try {
      setLoading(true);
      const response = await hotleadService.seedDatabase(1000);
      
      if (response.success) {
        setSnackbarMessage(`Database seeded with ${response.data.total_leads} leads. Conversion rate: ${response.data.conversion_rate}`);
        setSnackbarOpen(true);
        loadData(); // Refresh all data
      } else {
        setSnackbarMessage('Failed to seed database');
        setSnackbarOpen(true);
      }
    } catch (err) {
      console.error('Error seeding database:', err);
      setSnackbarMessage('Error seeding database');
      setSnackbarOpen(true);
    } finally {
      setLoading(false);
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
          <Button 
            variant="outlined" 
            startIcon={<ModelTraining />}
            onClick={handleTrainModel}
            disabled={modelTraining}
          >
            {modelTraining ? 'Training...' : 'Train Model'}
          </Button>
          <Button 
            variant="contained" 
            startIcon={<Science />}
            onClick={handleSeedDatabase}
          >
            Seed Database
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* System Status */}
      {systemStatus && (
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
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Priority Queue" />
          <Tab label="Analytics" />
          <Tab label="Model Info" />
        </Tabs>
      </Box>

      {/* Priority Queue Tab */}
      {tabValue === 0 && (
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
                      <TableCell>Temperature</TableCell>
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
                        <TableCell>
                          <Typography variant="body2">
                            {lead.lead_temperature}
                          </Typography>
                        </TableCell>
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
        </>
      )}

      {/* Analytics Tab */}
      {tabValue === 1 && analytics && (
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
      )}

      {/* Model Info Tab */}
      {tabValue === 2 && systemStatus && (
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
