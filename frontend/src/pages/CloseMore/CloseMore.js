import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Button,
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
} from '@mui/material';
import {
  Psychology,
  Schedule,
  TrendingUp,
  TrendingDown,
  Phone,
  WhatsApp,
  Email,
  Assignment,
  Visibility,
  Person,
  Warning,
  CheckCircle,
  AccessTime,
  AutoFixHigh,
  NotificationsActive,
  ChatBubble,
  PlayArrow,
} from '@mui/icons-material';
import closemoreService from '../../services/closemoreService';

function CloseMore() {
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [filterStage, setFilterStage] = useState('all');
  const [filterPriority, setFilterPriority] = useState('all');
  const [conversations, setConversations] = useState([]);
  const [dailyActions, setDailyActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  // Calculate conversation summary from actual data
  const conversationSummary = {
    totalConversations: conversations.length,
    awaitingAction: conversations.filter(c => c.requiresAction).length,
    scheduledMeetings: conversations.filter(c => c.stage === 'meeting').length,
    noShows: conversations.filter(c => c.stage === 'noshow').length,
    avgResponseTime: conversations.length > 0 ? 
      Math.round(conversations.reduce((acc, c) => acc + (c.responseTime || 0), 0) / conversations.length * 10) / 10 + ' hours' 
      : '0 hours',
    winRateThisWeek: conversations.length > 0 ? 
      Math.round(conversations.filter(c => c.stage === 'closed').length / conversations.length * 100) 
      : 0,
  };

  // Load data from API on component mount - simplified approach
  useEffect(() => {
    let isMounted = true;
    
    const loadData = async () => {
      if (!isMounted) return;
      
      try {
        setLoading(true);
        setError(null);
        
        // Simple delay to prevent rapid duplicate requests
        await new Promise(resolve => setTimeout(resolve, 200));
        
        if (!isMounted) return;
        
        const [conversationsData, actionsData] = await Promise.all([
          closemoreService.getConversations(),
          closemoreService.getDailyActions()
        ]);
        
        if (isMounted) {
          setConversations(conversationsData);
          setDailyActions(actionsData);
        }
      } catch (err) {
        if (isMounted) {
          setError('Failed to load data');
          console.error('Error loading CloseMore data:', err);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    // Debounce the load to prevent React 18 Strict Mode double calls
    const timeoutId = setTimeout(loadData, 50);
    
    return () => {
      isMounted = false;
      clearTimeout(timeoutId);
    };
  }, []);

  const getPriorityColor = (priority) => {
    const colors = {
      high: 'error',
      medium: 'warning',
      low: 'info',
    };
    return colors[priority] || 'default';
  };

  const getStageColor = (stage) => {
    const colors = {
      discovery: 'info',
      proposal: 'warning',
      negotiation: 'primary',
      nurture: 'secondary',
      closed: 'success',
    };
    return colors[stage] || 'default';
  };

  const getSentimentColor = (sentiment) => {
    const colors = {
      positive: 'success',
      neutral: 'warning',
      negative: 'error',
      cautious: 'info',
      uncertain: 'secondary',
    };
    return colors[sentiment] || 'default';
  };

  const handleConversationClick = async (conversation) => {
    setSelectedConversation(conversation);
    setDialogOpen(true);
    
    // Load detailed conversation analysis
    try {
      const analysis = await closemoreService.analyzeConversation(conversation.id);
      setAnalysisResult(analysis);
    } catch (err) {
      console.error('Error analyzing conversation:', err);
      setSnackbarMessage('Failed to analyze conversation');
      setSnackbarOpen(true);
    }
  };

  const handleGenerateNextAction = async (conversationId) => {
    try {
      const action = await closemoreService.generateNextAction(conversationId);
      setSnackbarMessage('Next action generated successfully');
      setSnackbarOpen(true);
      // Refresh conversations to show updated data
      const updatedConversations = await closemoreService.getConversations();
      setConversations(updatedConversations);
    } catch (err) {
      console.error('Error generating next action:', err);
      setSnackbarMessage('Failed to generate next action');
      setSnackbarOpen(true);
    }
  };

  const filteredConversations = conversations.filter(conv => {
    const stageMatch = filterStage === 'all' || conv.stage === filterStage;
    const priorityMatch = filterPriority === 'all' || conv.priority === filterPriority;
    return stageMatch && priorityMatch;
  });

  const ConversationDetailDialog = () => (
    <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar>{selectedConversation?.customerAvatar}</Avatar>
          <Box>
            <Typography variant="h6">{selectedConversation?.customerName}</Typography>
            <Typography variant="body2" color="text.secondary">
              {selectedConversation?.channel} • {selectedConversation?.lastContact}
            </Typography>
          </Box>
          <Box sx={{ ml: 'auto' }}>
            <Chip
              label={`${selectedConversation?.winProbability}% Win Probability`}
              color={selectedConversation?.winProbability > 70 ? 'success' : selectedConversation?.winProbability > 50 ? 'warning' : 'error'}
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
                AI Conversation Summary
              </Typography>
              <Typography variant="body2">
                {analysisResult?.summary || selectedConversation?.aiSummary}
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Button 
                  variant="outlined" 
                  size="small" 
                  onClick={() => handleGenerateNextAction(selectedConversation?.id)}
                  startIcon={<AutoFixHigh />}
                >
                  Analyze with AI
                </Button>
              </Box>
            </Alert>
          </Grid>

          {/* Analysis Results */}
          {analysisResult && (
            <Grid item xs={12}>
              <Card sx={{ backgroundColor: 'primary.50', border: '1px solid', borderColor: 'primary.200' }}>
                <CardContent>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2, color: 'primary.main' }}>
                    AI Analysis Results
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>Sentiment:</strong> {analysisResult.sentiment}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>Intent:</strong> {analysisResult.intent}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Confidence:</strong> {analysisResult.confidence}%
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>Key Topics:</strong> {analysisResult.keyTopics?.join(', ')}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Recommended Action:</strong> {analysisResult.recommendedAction}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Next Best Action */}
          <Grid item xs={12}>
            <Card sx={{ backgroundColor: 'success.50', border: '1px solid', borderColor: 'success.200' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <AutoFixHigh sx={{ color: 'success.main', mr: 1 }} />
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'success.main' }}>
                    Next Best Action
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Action:</strong> {selectedConversation?.nextAction}
                </Typography>
                <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
                  <strong>Reason:</strong> {selectedConversation?.actionReason}
                </Typography>
                <Button variant="contained" color="success" size="small">
                  Mark as Completed
                </Button>
              </CardContent>
            </Card>
          </Grid>

          {/* Conversation Details */}
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
              Conversation Details
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <ChatBubble sx={{ fontSize: 16, color: 'text.secondary' }} />
                <Typography variant="body2">Channel: {selectedConversation?.channel}</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Assignment sx={{ fontSize: 16, color: 'text.secondary' }} />
                <Typography variant="body2">Stage: {selectedConversation?.stage}</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Psychology sx={{ fontSize: 16, color: 'text.secondary' }} />
                <Typography variant="body2">Sentiment: {selectedConversation?.sentiment}</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Schedule sx={{ fontSize: 16, color: 'text.secondary' }} />
                <Typography variant="body2">
                  Meeting: {selectedConversation?.meetingScheduled ? 'Scheduled' : 'Not scheduled'}
                </Typography>
              </Box>
            </Box>
          </Grid>

          {/* Objections & Progress */}
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
              Identified Objections
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
              {selectedConversation?.objections.map((objection, index) => (
                <Chip
                  key={index}
                  label={objection.replace('_', ' ')}
                  size="small"
                  color="warning"
                  variant="outlined"
                />
              ))}
            </Box>
            <Typography variant="body2" color="text.secondary">
              Conversations: {selectedConversation?.conversationCount}
            </Typography>
          </Grid>
        </Grid>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={() => setDialogOpen(false)}>Close</Button>
        <Button variant="contained" startIcon={<Phone />}>
          Call Now
        </Button>
        <Button variant="contained" startIcon={<WhatsApp />}>
          WhatsApp
        </Button>
        <Button variant="contained" startIcon={<Email />}>
          Send Email
        </Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Box>
      {/* Loading State */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
          <CircularProgress size={60} />
        </Box>
      )}

      {/* Error State */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Main Content - only show when not loading */}
      {!loading && (
        <>
          {/* Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Box>
              <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                Conversation Management
              </Typography>
              <Typography variant="body2" color="text.secondary">
                CloseMore AI Conversations • Next-Best-Action • Smart Nudges
              </Typography>
            </Box>
            <Button variant="contained" startIcon={<NotificationsActive />}>
              Send Nudges
            </Button>
          </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={2}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ color: 'primary.main', fontWeight: 'bold' }}>
                {conversationSummary.totalConversations}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Conversations
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={2}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ color: 'warning.main', fontWeight: 'bold' }}>
                {conversationSummary.awaitingAction}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Awaiting Action
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={2}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ color: 'success.main', fontWeight: 'bold' }}>
                {conversationSummary.scheduledMeetings}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Scheduled Meetings
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={2}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ color: 'error.main', fontWeight: 'bold' }}>
                {conversationSummary.noShows}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                No-Shows
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={2}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ color: 'info.main', fontWeight: 'bold' }}>
                {conversationSummary.avgResponseTime}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Avg Response Time
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={2}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ color: 'success.main', fontWeight: 'bold' }}>
                {conversationSummary.winRateThisWeek}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Win Rate This Week
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Active Conversations" />
          <Tab label="Daily Actions by Rep" />
        </Tabs>
      </Box>

      {/* Active Conversations Tab */}
      {tabValue === 0 && (
        <>
          {/* Filters */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Stage Filter</InputLabel>
                <Select
                  value={filterStage}
                  label="Stage Filter"
                  onChange={(e) => setFilterStage(e.target.value)}
                >
                  <MenuItem value="all">All Stages</MenuItem>
                  <MenuItem value="discovery">Discovery</MenuItem>
                  <MenuItem value="proposal">Proposal</MenuItem>
                  <MenuItem value="negotiation">Negotiation</MenuItem>
                  <MenuItem value="nurture">Nurture</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Priority Filter</InputLabel>
                <Select
                  value={filterPriority}
                  label="Priority Filter"
                  onChange={(e) => setFilterPriority(e.target.value)}
                >
                  <MenuItem value="all">All Priorities</MenuItem>
                  <MenuItem value="high">High Priority</MenuItem>
                  <MenuItem value="medium">Medium Priority</MenuItem>
                  <MenuItem value="low">Low Priority</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          {/* Conversations Table */}
          <Card>
            <CardContent sx={{ p: 0 }}>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow sx={{ backgroundColor: 'grey.50' }}>
                      <TableCell>Customer</TableCell>
                      <TableCell>Channel</TableCell>
                      <TableCell>Stage</TableCell>
                      <TableCell>Priority</TableCell>
                      <TableCell>Win Probability</TableCell>
                      <TableCell>Next Action</TableCell>
                      <TableCell>Last Contact</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredConversations.map((conversation) => (
                      <TableRow key={conversation.id} hover>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Avatar sx={{ width: 40, height: 40 }}>{conversation.customerAvatar}</Avatar>
                            <Box>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                                {conversation.customerName}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {conversation.conversationCount} conversations
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={conversation.channel}
                            size="small"
                            variant="outlined"
                            icon={
                              conversation.channel === 'WhatsApp' ? <WhatsApp /> :
                              conversation.channel === 'Phone' ? <Phone /> : <Email />
                            }
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={conversation.stage}
                            color={getStageColor(conversation.stage)}
                            variant="outlined"
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Badge badgeContent={conversation.priority === 'high' ? '!' : null} color="error">
                            <Chip
                              label={conversation.priority}
                              color={getPriorityColor(conversation.priority)}
                              variant="filled"
                              size="small"
                            />
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={conversation.winProbability}
                              sx={{ width: 60, height: 6 }}
                              color={
                                conversation.winProbability > 70 ? 'success' :
                                conversation.winProbability > 50 ? 'warning' : 'error'
                              }
                            />
                            <Typography variant="caption">{conversation.winProbability}%</Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ maxWidth: 200 }}>
                            {conversation.nextAction}
                          </Typography>
                          <Chip
                            label={conversation.sentiment}
                            color={getSentimentColor(conversation.sentiment)}
                            variant="outlined"
                            size="small"
                            sx={{ mt: 0.5 }}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">{conversation.lastContact}</Typography>
                          {conversation.meetingScheduled && (
                            <Chip
                              label="Meeting Scheduled"
                              color="success"
                              size="small"
                              variant="outlined"
                              icon={<Schedule />}
                              sx={{ mt: 0.5 }}
                            />
                          )}
                        </TableCell>
                        <TableCell align="center">
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => handleConversationClick(conversation)}
                          >
                            View Details
                          </Button>
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

      {/* Daily Actions by Rep Tab */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          {dailyActions.map((rep) => (
            <Grid item xs={12} md={4} key={rep.rep}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                    <Avatar sx={{ bgcolor: 'primary.main' }}>{rep.avatar}</Avatar>
                    <Box>
                      <Typography variant="h6">{rep.rep}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Sales Representative
                      </Typography>
                    </Box>
                  </Box>

                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" sx={{ color: 'warning.main', fontWeight: 'bold' }}>
                          {rep.pendingActions}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Pending Actions
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" sx={{ color: 'error.main', fontWeight: 'bold' }}>
                          {rep.highPriority}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          High Priority
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" sx={{ color: 'success.main', fontWeight: 'bold' }}>
                          {rep.completedToday}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Completed Today
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" sx={{ color: 'info.main', fontWeight: 'bold' }}>
                          {rep.winRate}%
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Win Rate
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>

                  <Divider sx={{ my: 2 }} />

                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    Avg Response Time: <strong>{rep.avgResponseTime}</strong>
                  </Typography>

                  <Button
                    variant="contained"
                    fullWidth
                    startIcon={<PlayArrow />}
                    sx={{ mt: 1 }}
                  >
                    View Action List
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <ConversationDetailDialog />
      </>
      )}

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

export default CloseMore;
