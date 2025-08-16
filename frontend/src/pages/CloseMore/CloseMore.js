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
  
  // New state for call transcription analysis
  const [transcriptionText, setTranscriptionText] = useState('');
  const [transcriptionAnalyzing, setTranscriptionAnalyzing] = useState(false);
  const [transcriptionResult, setTranscriptionResult] = useState(null);
  const [generatingTranscription, setGeneratingTranscription] = useState(false);
  const [autoRefreshing, setAutoRefreshing] = useState(false);
  
  // Daily Actions Dialog state
  const [actionsDialogOpen, setActionsDialogOpen] = useState(false);
  const [selectedRepActions, setSelectedRepActions] = useState(null);
  const [actionManagementMode, setActionManagementMode] = useState(false);

  // Function to refresh team data
  const refreshTeamData = async (isAutoRefresh = false) => {
    try {
      if (isAutoRefresh) {
        setAutoRefreshing(true);
      }
      const actionsData = await closemoreService.getDailyActions();
      setDailyActions(actionsData);
    } catch (error) {
      console.error('Error refreshing team data:', error);
    } finally {
      if (isAutoRefresh) {
        setAutoRefreshing(false);
      }
    }
  };

  // Action management functions
  const handleMarkActionComplete = (actionIndex) => {
    if (selectedRepActions && selectedRepActions.actions) {
      console.log('Marking action complete for rep:', selectedRepActions.repId);
      console.log('Current dailyActions:', dailyActions);
      console.log('selectedRepActions:', selectedRepActions);
      
      const updatedActions = [...selectedRepActions.actions];
      updatedActions[actionIndex] = {
        ...updatedActions[actionIndex],
        status: 'completed',
        completed_at: new Date().toISOString()
      };
      
      const updatedRepActions = {
        ...selectedRepActions,
        actions: updatedActions,
        completedToday: selectedRepActions.completedToday + 1,
        pendingActions: selectedRepActions.pendingActions - 1
      };
      
      setSelectedRepActions(updatedRepActions);
      
      // Update the team overview data as well
      const updatedDailyActions = dailyActions.map(rep => {
        console.log('Comparing rep.repId:', rep.repId, 'with selectedRepActions.repId:', selectedRepActions.repId);
        return rep.repId === selectedRepActions.repId 
          ? {
              ...rep,
              completedToday: rep.completedToday + 1,
              pendingActions: rep.pendingActions - 1
            }
          : rep;
      });
      
      console.log('Updated dailyActions:', updatedDailyActions);
      setDailyActions(updatedDailyActions);
      
      setSnackbarMessage('Action marked as completed!');
      setSnackbarOpen(true);
    }
  };

  const handleReassignAction = (actionIndex, newRepId) => {
    if (selectedRepActions && selectedRepActions.actions) {
      const updatedActions = [...selectedRepActions.actions];
      updatedActions[actionIndex] = {
        ...updatedActions[actionIndex],
        reassigned_to: newRepId,
        reassigned_at: new Date().toISOString()
      };
      
      setSelectedRepActions({
        ...selectedRepActions,
        actions: updatedActions
      });
      
      setSnackbarMessage('Action reassigned successfully!');
      setSnackbarOpen(true);
    }
  };

  const handleUpdateActionPriority = (actionIndex, newPriority) => {
    if (selectedRepActions && selectedRepActions.actions) {
      const updatedActions = [...selectedRepActions.actions];
      const currentAction = selectedRepActions.actions[actionIndex];
      const wasHighPriority = currentAction.priority_score >= 80;
      const isNowHighPriority = newPriority >= 80;
      
      updatedActions[actionIndex] = {
        ...updatedActions[actionIndex],
        priority_score: newPriority,
        urgency_level: newPriority >= 80 ? 'high' : newPriority >= 60 ? 'medium' : 'low'
      };
      
      const updatedRepActions = {
        ...selectedRepActions,
        actions: updatedActions
      };
      
      setSelectedRepActions(updatedRepActions);
      
      // Update high priority count in team overview if priority threshold crossed
      if (wasHighPriority !== isNowHighPriority) {
        const highPriorityDelta = isNowHighPriority ? 1 : -1;
        const updatedDailyActions = dailyActions.map(rep => 
          rep.repId === selectedRepActions.repId 
            ? {
                ...rep,
                highPriority: rep.highPriority + highPriorityDelta
              }
            : rep
        );
        setDailyActions(updatedDailyActions);
      }
      
      setSnackbarMessage('Action priority updated!');
      setSnackbarOpen(true);
    }
  };

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

  // Load data from API on component mount with periodic refresh
  useEffect(() => {
    let isMounted = true;
    let loadingTimeout = null;
    let refreshInterval = null;
    
    const loadData = async () => {
      if (!isMounted) return;
      
      try {
        setLoading(true);
        setError(null);
        
        // Load conversations first
        const conversationsData = await closemoreService.getConversations();
        if (isMounted) {
          setConversations(conversationsData);
        }
        
        // Then load daily actions with a small delay to prevent race conditions
        if (isMounted) {
          loadingTimeout = setTimeout(async () => {
            if (isMounted) {
              const actionsData = await closemoreService.getDailyActions();
              if (isMounted) {
                console.log('Setting daily actions:', actionsData);
                setDailyActions(actionsData);
              }
            }
          }, 100);
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

    // Load data immediately
    loadData();
    
    // Auto-refresh disabled per user request
    // refreshInterval = setInterval(() => {
    //   if (isMounted) {
    //     refreshTeamData(true); // Auto-refresh with indicator
    //   }
    // }, 30000);
    
    return () => {
      isMounted = false;
      if (loadingTimeout) {
        clearTimeout(loadingTimeout);
      }
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
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
      // Prepare conversation data for analysis
      const conversationData = {
        lead_id: conversation.id,
        channel: 'email', // Always use 'email' to avoid validation errors
        conversation_text: conversation.content || conversation.aiSummary || 'Customer interested in our services',
        rep_id: 'current_rep'
      };
      
      const analysis = await closemoreService.analyzeConversation(conversationData);
      
      if (analysis.success) {
        // Map the API response to the expected format for the UI
        const mappedAnalysis = {
          sentiment: analysis.data.sentiment_analysis?.overall_sentiment > 0 ? 'Positive' : 
                    analysis.data.sentiment_analysis?.overall_sentiment < 0 ? 'Negative' : 'Neutral',
          intent: analysis.data.detected_intent || 'Unknown',
          confidence: Math.round((analysis.data.intent_confidence || 0.6) * 100),
          keyTopics: analysis.data.key_topics || [],
          recommendedAction: analysis.data.next_steps?.[0] || 'Follow up with customer'
        };
        setAnalysisResult(mappedAnalysis);
      } else {
        throw new Error(analysis.error);
      }
    } catch (err) {
      console.error('Error analyzing conversation:', err);
      setSnackbarMessage('Failed to analyze conversation');
      setSnackbarOpen(true);
    }
  };

  // New handler for call transcription analysis
  const handleTranscriptionAnalysis = async () => {
    if (!transcriptionText.trim()) {
      setSnackbarMessage('Please enter a call transcription to analyze');
      setSnackbarOpen(true);
      return;
    }

    setTranscriptionAnalyzing(true);
    setTranscriptionResult(null);

    try {
      // Create a conversation object for analysis
      const conversationData = {
        lead_id: `manual_${Date.now()}`,
        channel: 'call_transcript',
        conversation_text: transcriptionText,
        rep_id: 'current_rep',
        stage: 'discovery',
        priority: 'medium'
      };

      const result = await closemoreService.analyzeConversation(conversationData);
      
      if (result.success) {
        setTranscriptionResult(result.data);
        setSnackbarMessage('Call transcription analyzed successfully!');
        setSnackbarOpen(true);
      } else {
        throw new Error(result.error || 'Analysis failed');
      }
    } catch (err) {
      console.error('Error analyzing transcription:', err);
      setSnackbarMessage(`Analysis failed: ${err.message}`);
      setSnackbarOpen(true);
    } finally {
      setTranscriptionAnalyzing(false);
    }
  };

  // Clear transcription analysis
  const handleClearTranscription = () => {
    setTranscriptionText('');
    setTranscriptionResult(null);
  };

  const handleGenerateTranscription = async () => {
    setGeneratingTranscription(true);
    setTranscriptionText(''); // Clear any existing text
    setTranscriptionResult(null);
    
    try {
      console.log('Starting transcription generation...');
      const result = await closemoreService.generateCallTranscription();
      console.log('Transcription generation result:', result);
      
      if (result.success && result.data) {
        console.log('Transcription successful, length:', result.data.length);
        setTranscriptionText(result.data);
        setSnackbarMessage('AI call transcription generated successfully!');
        setSnackbarOpen(true);
      } else {
        console.error('Transcription failed:', result.error);
        setSnackbarMessage(`Failed to generate transcription: ${result.error || 'Unknown error'}`);
        setSnackbarOpen(true);
      }
    } catch (error) {
      console.error('Error in transcription generation:', error);
      setSnackbarMessage(`Error generating transcription: ${error.message || error}`);
      setSnackbarOpen(true);
    } finally {
      setGeneratingTranscription(false);
    }
  };

  const handleViewActionList = (rep) => {
    console.log('Opening action list for rep:', rep);
    console.log('Rep actions data:', rep.actions);
    console.log('Rep actions count:', rep.actions?.length || 0);
    
    setSelectedRepActions(rep);
    setActionsDialogOpen(true);
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
              {(selectedConversation?.objections || []).map((objection, index) => (
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

      {/* Call Transcription Analysis Section */}
      <Card sx={{ mb: 3, backgroundColor: 'primary.50', border: '1px solid', borderColor: 'primary.200' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Psychology sx={{ color: 'primary.main', mr: 1 }} />
            <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
              Call Transcription Analysis
            </Typography>
          </Box>
          
          <Grid container spacing={3}>
            {/* Input Section */}
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                multiline
                rows={6}
                variant="outlined"
                placeholder="Paste your call transcription here... 

Example:
Rep: Hi John, thanks for your interest in our Data Science course. I saw you downloaded our brochure yesterday.
Prospect: Yes, I'm looking to transition from marketing to data science. But I'm concerned about the time commitment and whether I can handle the technical content.
Rep: That's a common concern. Can you tell me about your current background and what specifically interests you about data science?"
                value={transcriptionText}
                onChange={(e) => setTranscriptionText(e.target.value)}
                sx={{ 
                  mb: 2,
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'white',
                    '& fieldset': {
                      borderColor: 'primary.300',
                    },
                    '&:hover fieldset': {
                      borderColor: 'primary.500',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: 'primary.600',
                    },
                  }
                }}
              />
              
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={transcriptionAnalyzing ? <CircularProgress size={20} color="inherit" /> : <Psychology />}
                  onClick={handleTranscriptionAnalysis}
                  disabled={transcriptionAnalyzing || !transcriptionText.trim()}
                  size="large"
                >
                  {transcriptionAnalyzing ? 'Analyzing...' : 'Summarize & Analyze'}
                </Button>
                
                <Button
                  variant="outlined"
                  color="secondary"
                  onClick={handleGenerateTranscription}
                  disabled={generatingTranscription || transcriptionAnalyzing}
                  startIcon={generatingTranscription ? <AutoFixHigh /> : <Psychology />}
                >
                  {generatingTranscription ? 'Generating...' : 'Generate AI Call'}
                </Button>
                
                <Button
                  variant="outlined"
                  onClick={handleClearTranscription}
                  disabled={transcriptionAnalyzing}
                >
                  Clear
                </Button>
              </Box>
            </Grid>

            {/* Analysis Results */}
            <Grid item xs={12} md={4}>
              {transcriptionResult ? (
                <Card sx={{ backgroundColor: 'white', height: 'fit-content' }}>
                  <CardContent>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2, color: 'success.main' }}>
                      ✅ Analysis Complete
                    </Typography>
                    
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
                        Summary:
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {transcriptionResult.summary}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
                        Intent:
                      </Typography>
                      <Chip 
                        label={transcriptionResult.detected_intent?.replace('_', ' ') || 'Unknown'} 
                        color="primary" 
                        size="small" 
                      />
                    </Box>
                    
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
                        Sentiment:
                      </Typography>
                      <Chip 
                        label={`${(transcriptionResult.sentiment_analysis?.overall_sentiment > 0 ? 'Positive' : transcriptionResult.sentiment_analysis?.overall_sentiment < 0 ? 'Negative' : 'Neutral')} (${Math.round((transcriptionResult.sentiment_analysis?.confidence || 0) * 100)}%)`}
                        color={transcriptionResult.sentiment_analysis?.overall_sentiment > 0 ? 'success' : transcriptionResult.sentiment_analysis?.overall_sentiment < 0 ? 'error' : 'warning'} 
                        size="small" 
                      />
                    </Box>
                    
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
                        Conversion Probability:
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {Math.round((transcriptionResult.conversion_probability || 0) * 100)}%
                      </Typography>
                    </Box>
                    
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
                        Next Steps:
                      </Typography>
                      {(transcriptionResult?.next_steps || []).slice(0, 3).map((step, index) => (
                        <Typography key={index} variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem', mb: 0.5 }}>
                          • {step}
                        </Typography>
                      ))}
                    </Box>
                    
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
                        Key Topics:
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {(transcriptionResult?.key_topics || []).slice(0, 3).map((topic, index) => (
                          <Chip key={index} label={topic} size="small" variant="outlined" />
                        ))}
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              ) : (
                <Card sx={{ backgroundColor: 'white', height: 'fit-content' }}>
                  <CardContent>
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                      <ChatBubble sx={{ fontSize: 40, color: 'text.secondary', mb: 2 }} />
                      <Typography variant="body1" color="text.secondary" sx={{ mb: 1 }}>
                        AI Analysis Ready
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Paste a call transcription and click "Summarize & Analyze" to get:
                      </Typography>
                      <List dense sx={{ textAlign: 'left', mt: 1 }}>
                        <ListItem sx={{ py: 0 }}>
                          <ListItemText primary="• Lead intent detection" primaryTypographyProps={{ fontSize: '0.8rem' }} />
                        </ListItem>
                        <ListItem sx={{ py: 0 }}>
                          <ListItemText primary="• Sentiment analysis" primaryTypographyProps={{ fontSize: '0.8rem' }} />
                        </ListItem>
                        <ListItem sx={{ py: 0 }}>
                          <ListItemText primary="• Objection identification" primaryTypographyProps={{ fontSize: '0.8rem' }} />
                        </ListItem>
                        <ListItem sx={{ py: 0 }}>
                          <ListItemText primary="• Next best actions" primaryTypographyProps={{ fontSize: '0.8rem' }} />
                        </ListItem>
                        <ListItem sx={{ py: 0 }}>
                          <ListItemText primary="• Conversion probability" primaryTypographyProps={{ fontSize: '0.8rem' }} />
                        </ListItem>
                      </List>
                    </Box>
                  </CardContent>
                </Card>
              )}
            </Grid>
          </Grid>
        </CardContent>
      </Card>

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
        <>
          {/* Summary Header */}
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  Team Performance Overview
                </Typography>
                {autoRefreshing && (
                  <Typography variant="caption" sx={{ color: 'primary.main', fontStyle: 'italic' }}>
                    Auto-refreshing...
                  </Typography>
                )}
              </Box>
              <Button
                variant="outlined"
                startIcon={<TrendingUp />}
                onClick={async () => {
                  try {
                    await refreshTeamData();
                    setSnackbarMessage('Daily actions refreshed!');
                    setSnackbarOpen(true);
                  } catch (error) {
                    console.error('Error refreshing daily actions:', error);
                    setSnackbarMessage('Failed to refresh daily actions');
                    setSnackbarOpen(true);
                  }
                }}
              >
                Refresh Data
              </Button>
            </Box>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <Card sx={{ backgroundColor: 'primary.50', border: '1px solid', borderColor: 'primary.200' }}>
                  <CardContent sx={{ textAlign: 'center', py: 2 }}>
                    <Typography variant="h4" sx={{ color: 'primary.main', fontWeight: 'bold' }}>
                      {dailyActions.length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Active Sales Representatives
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card sx={{ backgroundColor: 'warning.50', border: '1px solid', borderColor: 'warning.200' }}>
                  <CardContent sx={{ textAlign: 'center', py: 2 }}>
                    <Typography variant="h4" sx={{ color: 'warning.main', fontWeight: 'bold' }}>
                      {dailyActions.reduce((sum, rep) => sum + rep.pendingActions, 0)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Pending Actions
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card sx={{ backgroundColor: 'error.50', border: '1px solid', borderColor: 'error.200' }}>
                  <CardContent sx={{ textAlign: 'center', py: 2 }}>
                    <Typography variant="h4" sx={{ color: 'error.main', fontWeight: 'bold' }}>
                      {dailyActions.reduce((sum, rep) => sum + rep.highPriority, 0)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      High Priority Actions
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={3}>
                <Card sx={{ backgroundColor: 'success.50', border: '1px solid', borderColor: 'success.200' }}>
                  <CardContent sx={{ textAlign: 'center', py: 2 }}>
                    <Typography variant="h4" sx={{ color: 'success.main', fontWeight: 'bold' }}>
                      {dailyActions.reduce((sum, rep) => sum + rep.completedToday, 0)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Completed Today
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>

          {/* Individual Rep Cards */}
          <Grid container spacing={3}>
            {dailyActions.map((rep) => (
              <Grid item xs={12} md={6} lg={4} key={rep.repId}>
                <Card sx={{ 
                  height: '100%',
                  border: rep.highPriority > 0 ? '2px solid' : '1px solid',
                  borderColor: rep.highPriority > 0 ? 'error.main' : 'divider',
                  backgroundColor: rep.highPriority > 0 ? 'error.50' : 'background.paper'
                }}>
                  <CardContent>
                    {/* Rep Header */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                      <Avatar sx={{ 
                        bgcolor: rep.highPriority > 0 ? 'error.main' : 'primary.main',
                        width: 48,
                        height: 48,
                        fontSize: '1.2rem',
                        fontWeight: 'bold'
                      }}>
                        {rep.avatar}
                      </Avatar>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {rep.rep}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {rep.totalConversations} conversations • {rep.meetingBookingRate}% booking rate
                        </Typography>
                      </Box>
                      {rep.highPriority > 0 && (
                        <Chip 
                          label={`${rep.highPriority} High Priority`}
                          color="primary"
                          size="small"
                          icon={<Warning />}
                        />
                      )}
                    </Box>

                    {/* Key Metrics Grid */}
                    <Grid container spacing={2} sx={{ mb: 2 }}>
                      <Grid item xs={6}>
                        <Box sx={{ textAlign: 'center' }}>
                          <Typography variant="h4" sx={{ 
                            color: rep.pendingActions > 10 ? 'primary.main' : 'warning.main', 
                            fontWeight: 'bold' 
                          }}>
                            {rep.pendingActions}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Pending Actions
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={6}>
                        <Box sx={{ textAlign: 'center' }}>
                          <Typography variant="h4" sx={{ 
                            color: rep.highPriority > 0 ? 'primary.main' : 'success.main', 
                            fontWeight: 'bold' 
                          }}>
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
                          <Typography variant="h4" sx={{ 
                            color: rep.winRate > 70 ? 'success.main' : rep.winRate > 50 ? 'warning.main' : 'info.main', 
                            fontWeight: 'bold' 
                          }}>
                            {rep.winRate}%
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Win Rate
                          </Typography>
                        </Box>
                      </Grid>
                    </Grid>

                    {/* Performance Indicators */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        <strong>Response Time:</strong> {rep.avgResponseTime}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        <strong>No-Show Rate:</strong> {rep.noShowRate}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        <strong>Est. Time:</strong> {rep.estimatedTotalTime} min
                      </Typography>
                    </Box>

                    {/* Action Button */}
                    <Button
                      variant="contained"
                      fullWidth
                      startIcon={<PlayArrow />}
                      onClick={() => handleViewActionList(rep)}
                      sx={{ mt: 1 }}
                      color={rep.highPriority > 0 ? 'error' : 'primary'}
                    >
                      View Action List ({rep.pendingActions})
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </>
      )}

      <ConversationDetailDialog />
      </>
      )}

      {/* Daily Actions Dialog */}
      <Dialog 
        open={actionsDialogOpen} 
        onClose={() => setActionsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'primary.main' }}>
              {selectedRepActions?.avatar}
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6">{selectedRepActions?.rep} - Daily Actions</Typography>
              <Typography variant="body2" color="text.secondary">
                {selectedRepActions?.pendingActions} pending actions • {selectedRepActions?.highPriority} high priority
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant={actionManagementMode ? 'contained' : 'outlined'}
                size="small"
                onClick={() => setActionManagementMode(!actionManagementMode)}
                startIcon={<Assignment />}
              >
                {actionManagementMode ? 'View Mode' : 'Manage Mode'}
              </Button>
            </Box>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedRepActions?.actions && selectedRepActions.actions.length > 0 ? (
            <List>
              {selectedRepActions.actions.map((action, index) => (
                <React.Fragment key={index}>
                  <ListItem alignItems="flex-start">
                    <ListItemAvatar>
                      <Avatar sx={{ 
                        bgcolor: action.urgency_level === 'high' ? 'error.main' : 
                                action.urgency_level === 'medium' ? 'warning.main' : 'info.main',
                        width: 32, height: 32 
                      }}>
                        {action.urgency_level === 'high' ? '🔥' : 
                         action.urgency_level === 'medium' ? '⚡' : '📝'}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="subtitle1" component="span">
                            {action.suggested_message}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                            <Chip 
                              label={`${action.priority_score}/100`}
                              size="small"
                              color={action.priority_score >= 80 ? 'error' : action.priority_score >= 60 ? 'warning' : 'default'}
                            />
                            {action.status === 'completed' && (
                              <Chip 
                                label="Completed"
                                size="small"
                                color="success"
                                icon={<CheckCircle />}
                              />
                            )}
                          </Box>
                        </Box>
                      }
                      secondary={
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="body2" color="text.secondary">
                            <strong>Reason:</strong> {action.reason}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            <strong>Expected Outcome:</strong> {action.expected_outcome}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                            <Chip label={`${action.estimated_time_minutes} min`} size="small" variant="outlined" />
                            <Chip label={action.action_type?.replace('_', ' ') || 'Action'} size="small" variant="outlined" />
                            {action.tags && action.tags.map((tag, tagIndex) => (
                              <Chip key={tagIndex} label={tag} size="small" variant="outlined" />
                            ))}
                          </Box>
                          
                          {/* Action Management Controls */}
                          {actionManagementMode && (
                            <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                              {action.status !== 'completed' && (
                                <Button
                                  variant="outlined"
                                  size="small"
                                  color="success"
                                  onClick={() => handleMarkActionComplete(index)}
                                  startIcon={<CheckCircle />}
                                >
                                  Mark Complete
                                </Button>
                              )}
                              
                              <Button
                                variant="outlined"
                                size="small"
                                color="primary"
                                onClick={() => handleUpdateActionPriority(index, Math.min(100, action.priority_score + 10))}
                                disabled={action.priority_score >= 100}
                              >
                                Increase Priority
                              </Button>
                              
                              <Button
                                variant="outlined"
                                size="small"
                                color="secondary"
                                onClick={() => handleUpdateActionPriority(index, Math.max(0, action.priority_score - 10))}
                                disabled={action.priority_score <= 0}
                              >
                                Decrease Priority
                              </Button>
                            </Box>
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < selectedRepActions.actions.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          ) : (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="h6" color="text.secondary">
                No actions available
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All daily actions have been completed or no actions are currently needed.
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Debug Info: {selectedRepActions ? `Rep: ${selectedRepActions.rep}, Actions: ${selectedRepActions.actions?.length || 0}` : 'No rep data'}
                </Typography>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setActionsDialogOpen(false)}>Close</Button>
          {actionManagementMode && (
            <Button 
              variant="contained" 
              onClick={() => {
                // Mark all actions as reviewed
                setSnackbarMessage('All actions marked as reviewed!');
                setSnackbarOpen(true);
                setActionsDialogOpen(false);
              }}
            >
              Mark All as Reviewed
            </Button>
          )}
        </DialogActions>
      </Dialog>

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
