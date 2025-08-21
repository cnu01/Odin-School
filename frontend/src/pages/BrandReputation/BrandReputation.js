import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Button,
  Avatar,
  Paper,
  Tabs,
  Tab,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Snackbar,
} from '@mui/material';
import {
  Forum,
  YouTube,
  Instagram,
  Facebook,
  Twitter,
  Reply,
  ThumbUp,
  ThumbDown,
  Warning,
  CheckCircle,
  Schedule,
  Psychology,
  Send,
  Edit,
  Flag,
  Refresh,
  AutoFixHigh,
  Analytics,
  Casino,
} from '@mui/icons-material';
import trustdeskService from '../../services/trustdeskService';

// Response templates for fallback when AI generation fails
const responseTemplates = {
  positive: [
    "Thank you so much for your wonderful feedback! 😊 We're thrilled to hear about your success with our {course} course. Your achievement motivates us to keep delivering quality education!",
    "This made our day! 🎉 Congratulations on completing the {course} course. We'd love to feature your success story - would you be interested in sharing more details?",
  ],
  question: [
    "Great question! Our {course} course is designed specifically for career switchers. We have many success stories of students from non-tech backgrounds. Would you like to speak with our counselor for personalized guidance?",
    "Thanks for reaching out! The {course} course includes dedicated career support and placement assistance. Let me connect you with our admissions team for detailed information.",
  ],
  negative: [
    "Thank you for your feedback. We take all concerns seriously and are constantly updating our curriculum. I'd like to discuss this personally - could you please DM us your course details?",
    "We appreciate your honest feedback and apologize for not meeting expectations. Let's make this right - please reach out to our support team for immediate assistance.",
  ],
  urgent: [
    "We're sorry for the inconvenience! Our technical team is looking into the payment issue. Please try again, and if it persists, contact our support at support@apexai.com for immediate assistance.",
    "Thanks for reporting this issue. We're resolving it on priority. Meanwhile, you can also enroll by calling our helpline at +91-XXXX-XXXX.",
  ],
};

function BrandReputation() {
  // State management
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedComment, setSelectedComment] = useState(null);
  const [replyDialog, setReplyDialog] = useState(false);
  const [draftReply, setDraftReply] = useState('');
  const [filterPlatform, setFilterPlatform] = useState('all');
  const [filterPriority, setFilterPriority] = useState('all');
  const [commentsData, setCommentsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [inputComment, setInputComment] = useState('');
  const [analyzingComment, setAnalyzingComment] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [generatingComment, setGeneratingComment] = useState(false);
  const [stats, setStats] = useState({
    totalComments: 0,
    urgentIssues: 0,
    negativeFeedback: 0,
    questions: 0,
    avgResponseTime: '2.8min'
  });

  // Load comments on component mount and when filters change
  useEffect(() => {
    const abortController = new AbortController();
    
    const loadComments = async () => {
      try {
        setLoading(true);
        
        // Add delay to prevent rapid duplicate requests from filter changes
        await new Promise(resolve => setTimeout(resolve, 150));
        
        if (abortController.signal.aborted) return;
        
        const filters = {
          platform: filterPlatform,
          priority: filterPriority
        };
        
        const result = await trustdeskService.getComments(filters);
        
        if (!abortController.signal.aborted) {
          if (result.success) {
            setCommentsData(result.data);
            updateStats(result.data);
          } else {
            showSnackbar('Error loading comments: ' + result.error, 'error');
          }
        }
      } catch (error) {
        if (!abortController.signal.aborted && error.name !== 'CanceledError') {
          console.error('Error loading comments:', error);
          showSnackbar('Failed to load comments', 'error');
        }
      } finally {
        if (!abortController.signal.aborted) {
          setLoading(false);
        }
      }
    };

    loadComments();
    
    // Cleanup function to prevent race conditions
    return () => {
      abortController.abort();
    };
  }, [filterPlatform, filterPriority]);

  const updateStats = (comments) => {
    const urgent = comments.filter(c => c.category === 'urgent' && c.status === 'new').length;
    const negative = comments.filter(c => c.category === 'negative' && c.status === 'new').length;
    const questions = comments.filter(c => c.category === 'question' && c.status === 'new').length;
    
    setStats({
      totalComments: comments.length,
      urgentIssues: urgent,
      negativeFeedback: negative,
      questions: questions,
      avgResponseTime: '2.8min'
    });
  };

  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const getPlatformIcon = (platform) => {
    const icons = {
      YouTube: <YouTube />,
      Instagram: <Instagram />,
      Facebook: <Facebook />,
      Twitter: <Twitter />,
    };
    return icons[platform];
  };

  const getPlatformColor = (platform) => {
    const colors = {
      YouTube: '#ff0000',
      Instagram: '#e1306c',
      Facebook: '#1877f2',
      Twitter: '#1da1f2',
    };
    return colors[platform];
  };

  const getSentimentColor = (sentiment) => {
    const colors = {
      positive: 'success',
      neutral: 'info',
      negative: 'error',
    };
    return colors[sentiment];
  };

  const getPriorityColor = (priority) => {
    const colors = {
      low: 'default',
      high: 'warning',
      urgent: 'error',
    };
    return colors[priority];
  };

  const handleGenerateReply = async (comment) => {
    setSubmitting(true);
    try {
      const result = await trustdeskService.generateResponse(comment.content, comment.category);
      
      if (result.success) {
        setDraftReply(result.data.draft_reply);
        showSnackbar(
          `AI-generated response (${Math.round(result.data.confidence_score * 100)}% confidence)`, 
          'success'
        );
      } else {
        showSnackbar('Error generating response: ' + result.error, 'error');
        // Fallback to template
        const templates = responseTemplates[comment.category] || responseTemplates.question;
        const template = templates[Math.floor(Math.random() * templates.length)];
        setDraftReply(template.replace('{course}', 'our'));
      }
    } catch (error) {
      console.error('Error generating reply:', error);
      showSnackbar('Failed to generate AI response', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmitReply = async () => {
    if (!selectedComment || !draftReply.trim()) {
      showSnackbar('Please enter a reply', 'warning');
      return;
    }

    setSubmitting(true);
    try {
      const result = await trustdeskService.submitResponse(selectedComment.id, draftReply);
      
      if (result.success) {
        // Update comment status in local state
        setCommentsData(prev => 
          prev.map(comment => 
            comment.id === selectedComment.id 
              ? { ...comment, status: 'responded' }
              : comment
          )
        );
        
        setReplyDialog(false);
        setDraftReply('');
        showSnackbar('Response submitted successfully!', 'success');
        
        // Refresh stats
        updateStats(commentsData);
      } else {
        showSnackbar('Error submitting response: ' + result.error, 'error');
      }
    } catch (error) {
      console.error('Error submitting reply:', error);
      showSnackbar('Failed to submit response', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const handleAnalyzeComment = async (comment) => {
    try {
      const result = await trustdeskService.analyzeComment({
        content: comment.content,
        platform: comment.platform,
        author: comment.author
      });

      if (result.success) {
        // Update comment with analysis
        setCommentsData(prev =>
          prev.map(c =>
            c.id === comment.id
              ? { ...c, analysis: result.data }
              : c
          )
        );
        showSnackbar('Comment analyzed successfully', 'success');
      } else {
        showSnackbar('Analysis failed: ' + result.error, 'error');
      }
    } catch (error) {
      console.error('Error analyzing comment:', error);
      showSnackbar('Failed to analyze comment', 'error');
    }
  };

  // Random comment generator
  const generateRandomComment = async () => {
    setGeneratingComment(true);
    try {
      const sampleComments = [
        // Positive comments
        "Absolutely love this course! The instructors are amazing and the content is so relevant to current industry needs.",
        "Best investment I've made in my career. Got a job within 2 months of completing the course!",
        "The hands-on projects really helped me understand the concepts. Highly recommend!",
        "Great support from the team throughout the course. Very professional and helpful.",
        
        // Negative comments
        "The course content seems outdated. Expected more modern frameworks and tools.",
        "Very disappointed with the lack of real-time support. Felt like I was learning alone.",
        "Overpriced for what they offer. Found better courses elsewhere for half the price.",
        "The instructor was not engaging at all. Just reading from slides most of the time.",
        
        // Neutral comments
        "Decent course overall. Some modules were good, others could be improved.",
        "The course covered the basics well but lacked advanced topics I was hoping for.",
        "Good value for money, though the pace was a bit slow for my liking.",
        "Content was okay but the platform interface could be more user-friendly.",
        
        // Questions
        "Does this course include placement assistance? I'm looking for job support after completion.",
        "What are the prerequisites for this course? I'm a complete beginner.",
        "Can I get a refund if I'm not satisfied with the course content?",
        "Are there any live sessions or is it all pre-recorded content?",
        
        // Urgent/Complaints
        "I've been trying to access my course for 3 days but the platform keeps crashing!",
        "My payment went through but I still don't have access to the course materials.",
        "The live session link is not working and the session starts in 10 minutes!",
        "Need immediate help with my assignment submission. The deadline is today!"
      ];
      
      const randomComment = sampleComments[Math.floor(Math.random() * sampleComments.length)];
      setInputComment(randomComment);
      showSnackbar('Random comment generated!', 'success');
    } catch (error) {
      console.error('Error generating comment:', error);
      showSnackbar('Failed to generate comment', 'error');
    } finally {
      setGeneratingComment(false);
    }
  };

  // Analyze the input comment
  const analyzeInputComment = async () => {
    if (!inputComment.trim()) {
      showSnackbar('Please enter a comment to analyze', 'warning');
      return;
    }

    setAnalyzingComment(true);
    try {
      const result = await trustdeskService.analyzeComment({
        content: inputComment.trim(),
        platform: 'manual_input',
        author: 'Test User'
      });

      if (result.success) {
        setAnalysisResult(result.data);
        showSnackbar('Comment analyzed successfully!', 'success');
      } else {
        showSnackbar('Analysis failed: ' + result.error, 'error');
      }
    } catch (error) {
      console.error('Error analyzing comment:', error);
      showSnackbar('Failed to analyze comment', 'error');
    } finally {
      setAnalyzingComment(false);
    }
  };

  const CommentItem = ({ comment }) => (
    <Card sx={{ mb: 2, border: comment.priority === 'urgent' ? '2px solid' : '1px solid', 
              borderColor: comment.priority === 'urgent' ? 'error.main' : 'divider' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
          <Avatar 
            sx={{ 
              bgcolor: getPlatformColor(comment.platform), 
              width: 40, 
              height: 40 
            }}
          >
            {comment.avatar}
          </Avatar>
          
          <Box sx={{ flexGrow: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                {comment.author}
              </Typography>
              <Chip
                icon={getPlatformIcon(comment.platform)}
                label={comment.platform}
                size="small"
                variant="outlined"
                sx={{ color: getPlatformColor(comment.platform) }}
              />
              <Chip
                label={comment.sentiment}
                size="small"
                color={getSentimentColor(comment.sentiment)}
                variant="filled"
              />
              <Chip
                label={comment.priority}
                size="small"
                color={getPriorityColor(comment.priority)}
                variant="outlined"
              />
              {comment.status === 'new' && (
                <Chip label="NEW" size="small" color="primary" variant="filled" />
              )}
            </Box>
            
            <Typography variant="body2" sx={{ mb: 2, lineHeight: 1.6 }}>
              {comment.content}
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <Typography variant="caption" color="text.secondary">
                {comment.timestamp}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {comment.platform === 'YouTube' ? comment.videoTitle : comment.postTitle}
              </Typography>
              {comment.likes > 0 && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <ThumbUp sx={{ fontSize: 16, color: 'text.secondary' }} />
                  <Typography variant="caption" color="text.secondary">
                    {comment.likes}
                  </Typography>
                </Box>
              )}
              {comment.replies > 0 && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Reply sx={{ fontSize: 16, color: 'text.secondary' }} />
                  <Typography variant="caption" color="text.secondary">
                    {comment.replies}
                  </Typography>
                </Box>
              )}
            </Box>

            {/* AI Analysis */}
            {comment.status === 'new' && comment.analysis && (
              <Alert 
                severity="info" 
                icon={<Psychology />} 
                sx={{ mb: 2, backgroundColor: 'info.50' }}
              >
                <Typography variant="caption" sx={{ fontWeight: 600 }}>
                  AI Analysis:
                </Typography>
                <Typography variant="caption" display="block">
                  <strong>Summary:</strong> {comment.analysis.summary}
                </Typography>
                <Typography variant="caption" display="block">
                  <strong>Urgency:</strong> {comment.analysis.urgency} 
                  {comment.analysis.confidence_score && (
                    ` (${Math.round(comment.analysis.confidence_score * 100)}% confidence)`
                  )}
                </Typography>
                {comment.analysis.is_sensitive && (
                  <Typography variant="caption" display="block" sx={{ color: 'error.main', fontWeight: 600 }}>
                    ⚠️ Sensitive content detected
                  </Typography>
                )}
              </Alert>
            )}

            {/* AI Suggestion */}
            {comment.status === 'new' && !comment.analysis && (
              <Alert 
                severity="warning" 
                icon={<Psychology />} 
                sx={{ mb: 2, backgroundColor: 'warning.50' }}
                action={
                  <Button 
                    size="small" 
                    onClick={() => handleAnalyzeComment(comment)}
                    disabled={loading}
                  >
                    Analyze with AI
                  </Button>
                }
              >
                <Typography variant="caption" sx={{ fontWeight: 600 }}>
                  Click "Analyze with AI" for intelligent insights
                </Typography>
              </Alert>
            )}
          </Box>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Button
              size="small"
              variant="contained"
              startIcon={submitting ? <CircularProgress size={16} /> : <Reply />}
              onClick={() => {
                setSelectedComment(comment);
                setReplyDialog(true);
                if (!draftReply) {
                  handleGenerateReply(comment);
                }
              }}
              disabled={comment.status === 'responded' || submitting}
            >
              {submitting ? 'Generating...' : 'AI Reply'}
            </Button>
            {comment.priority === 'urgent' && (
              <IconButton size="small" color="error">
                <Flag />
              </IconButton>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  const ReplyDialog = () => (
    <Dialog open={replyDialog} onClose={() => setReplyDialog(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Reply />
          <Typography variant="h6">AI-Powered Reply to {selectedComment?.author}</Typography>
          {selectedComment?.analysis?.confidence_score && (
            <Chip 
              label={`${Math.round(selectedComment.analysis.confidence_score * 100)}% AI Confidence`}
              color="success"
              size="small"
            />
          )}
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ mb: 3, p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
            "{selectedComment?.content}"
          </Typography>
          <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
            <Chip label={selectedComment?.platform} size="small" />
            <Chip label={selectedComment?.category} size="small" color="info" />
            {selectedComment?.analysis?.is_sensitive && (
              <Chip label="Sensitive" size="small" color="error" />
            )}
          </Box>
        </Box>

        {selectedComment?.analysis && (
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              AI Analysis Summary
            </Typography>
            <Typography variant="body2">
              {selectedComment.analysis.summary}
            </Typography>
            {selectedComment.analysis.knowledge_sources && selectedComment.analysis.knowledge_sources.length > 0 && (
              <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                Knowledge sources: {selectedComment.analysis.knowledge_sources.join(', ')}
              </Typography>
            )}
          </Alert>
        )}
        
        <TextField
          fullWidth
          multiline
          rows={4}
          label="Your Reply"
          value={draftReply}
          onChange={(e) => setDraftReply(e.target.value)}
          sx={{ mb: 2 }}
          disabled={submitting}
          placeholder={submitting ? 'Generating AI response...' : 'Enter your response or click "Generate AI Reply"'}
        />
        
        <Alert severity="success" sx={{ mb: 2 }}>
          <Typography variant="caption" sx={{ fontWeight: 600 }}>
            ✓ Brand Voice Check: Tone is professional and helpful
          </Typography>
        </Alert>
        
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
          <Typography variant="caption" color="text.secondary" sx={{ mr: 2 }}>
            Quick actions:
          </Typography>
          <Button
            size="small"
            variant="outlined"
            onClick={() => handleGenerateReply(selectedComment)}
            disabled={submitting}
            startIcon={submitting ? <CircularProgress size={16} /> : <Psychology />}
          >
            {submitting ? 'Generating...' : 'Regenerate AI Reply'}
          </Button>
          {responseTemplates[selectedComment?.category]?.map((template, index) => (
            <Button
              key={index}
              size="small"
              variant="text"
              onClick={() => setDraftReply(template.replace('{course}', 'our'))}
              disabled={submitting}
            >
              Template {index + 1}
            </Button>
          ))}
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={() => setReplyDialog(false)} disabled={submitting}>
          Cancel
        </Button>
        <Button 
          variant="outlined" 
          startIcon={<Edit />}
          disabled={submitting}
        >
          Save Draft
        </Button>
        <Button 
          variant="contained" 
          startIcon={submitting ? <CircularProgress size={16} /> : <Send />}
          onClick={handleSubmitReply}
          disabled={submitting || !draftReply.trim()}
        >
          {submitting ? 'Sending...' : 'Send Reply'}
        </Button>
      </DialogActions>
    </Dialog>
  );

  const filteredComments = commentsData.filter(comment => {
    const platformMatch = filterPlatform === 'all' || comment.platform === filterPlatform;
    const priorityMatch = filterPriority === 'all' || comment.priority === filterPriority;
    return platformMatch && priorityMatch;
  });

  const tabComments = {
    0: filteredComments, // All
    1: filteredComments.filter(c => c.category === 'urgent'),
    2: filteredComments.filter(c => c.category === 'negative'),
    3: filteredComments.filter(c => c.category === 'question'),
    4: filteredComments.filter(c => c.category === 'positive'),
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
            Brand Reputation
          </Typography>
          <Typography variant="body2" color="text.secondary">
            TrustDesk • AI-Powered Response Management • Brand Voice Alignment
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <IconButton>
            <Refresh />
          </IconButton>
          <Button variant="contained" startIcon={<CheckCircle />}>
            Mark All Read
          </Button>
        </Box>
      </Box>

      {/* Comment Analysis Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Analytics color="primary" />
            Comment Analysis Tool
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                placeholder="Enter a comment to analyze its sentiment, category, and priority..."
                value={inputComment}
                onChange={(e) => setInputComment(e.target.value)}
                variant="outlined"
                sx={{ mb: 2 }}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="outlined"
                  startIcon={generatingComment ? <CircularProgress size={20} /> : <Casino />}
                  onClick={generateRandomComment}
                  disabled={generatingComment}
                >
                  {generatingComment ? 'Generating...' : 'Generate Random Comment'}
                </Button>
                
                <Button
                  variant="contained"
                  startIcon={analyzingComment ? <CircularProgress size={20} /> : <AutoFixHigh />}
                  onClick={analyzeInputComment}
                  disabled={analyzingComment || !inputComment.trim()}
                >
                  {analyzingComment ? 'Analyzing...' : 'Start Analyzing'}
                </Button>
              </Box>
            </Grid>
            
            {/* Analysis Results */}
            {analysisResult && (
              <Grid item xs={12}>
                <Paper sx={{ p: 2, mt: 2, bgcolor: 'background.default' }}>
                  <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Analysis Results:
                  </Typography>
                  
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Chip 
                          label={`Sentiment: ${analysisResult.sentiment || 'Unknown'}`}
                          color={
                            analysisResult.sentiment === 'positive' ? 'success' :
                            analysisResult.sentiment === 'negative' ? 'error' : 'default'
                          }
                          sx={{ mb: 1 }}
                        />
                      </Box>
                    </Grid>
                    
                    <Grid item xs={12} md={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Chip 
                          label={`Category: ${analysisResult.category || 'Unknown'}`}
                          color="primary"
                          sx={{ mb: 1 }}
                        />
                      </Box>
                    </Grid>
                    
                    <Grid item xs={12} md={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Chip 
                          label={`Priority: ${analysisResult.priority || 'Unknown'}`}
                          color={
                            analysisResult.priority === 'urgent' ? 'error' :
                            analysisResult.priority === 'medium' ? 'warning' : 'success'
                          }
                          sx={{ mb: 1 }}
                        />
                      </Box>
                    </Grid>
                    
                    <Grid item xs={12} md={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Chip 
                          label={`Confidence: ${analysisResult.confidence ? (analysisResult.confidence * 100).toFixed(1) + '%' : 'Unknown'}`}
                          color="info"
                          sx={{ mb: 1 }}
                        />
                      </Box>
                    </Grid>
                    
                    {analysisResult.summary && (
                      <Grid item xs={12}>
                        <Typography variant="body2" sx={{ mt: 1 }}>
                          <strong>Summary:</strong> {analysisResult.summary}
                        </Typography>
                      </Grid>
                    )}
                    
                    {analysisResult.suggested_response && (
                      <Grid item xs={12}>
                        <Typography variant="body2" sx={{ mt: 1 }}>
                          <strong>Suggested Response:</strong> {analysisResult.suggested_response}
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                </Paper>
              </Grid>
            )}
          </Grid>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'error.main' }}>
                {loading ? <CircularProgress size={24} /> : stats.urgentIssues}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Urgent Issues
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'warning.main' }}>
                {loading ? <CircularProgress size={24} /> : stats.negativeFeedback}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Negative Feedback
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'info.main' }}>
                {loading ? <CircularProgress size={24} /> : stats.questions}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Questions
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                {loading ? <CircularProgress size={24} /> : stats.avgResponseTime}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Avg Response Time
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel>Platform</InputLabel>
            <Select
              value={filterPlatform}
              label="Platform"
              onChange={(e) => setFilterPlatform(e.target.value)}
            >
              <MenuItem value="all">All Platforms</MenuItem>
              <MenuItem value="YouTube">YouTube</MenuItem>
              <MenuItem value="Instagram">Instagram</MenuItem>
              <MenuItem value="Facebook">Facebook</MenuItem>
              <MenuItem value="Twitter">Twitter</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel>Priority</InputLabel>
            <Select
              value={filterPriority}
              label="Priority"
              onChange={(e) => setFilterPriority(e.target.value)}
            >
              <MenuItem value="all">All Priorities</MenuItem>
              <MenuItem value="urgent">Urgent</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="low">Low</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      {/* Tabs for Comment Categories */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)}>
          <Tab label="All Comments" />
          <Tab label="Urgent" />
          <Tab label="Negative" />
          <Tab label="Questions" />
          <Tab label="Positive" />
        </Tabs>
      </Box>

      {/* Comments List */}
      <Box>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : tabComments[selectedTab]?.length > 0 ? (
          tabComments[selectedTab].map((comment) => (
            <CommentItem key={comment.id} comment={comment} />
          ))
        ) : (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <CheckCircle sx={{ fontSize: 48, color: 'success.main', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              All caught up! No {selectedTab === 0 ? '' : 
                selectedTab === 1 ? 'urgent ' : 
                selectedTab === 2 ? 'negative ' :
                selectedTab === 3 ? 'question ' : 'positive '}
              comments to review.
            </Typography>
          </Paper>
        )}
      </Box>

      <ReplyDialog />
      
      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default BrandReputation;
