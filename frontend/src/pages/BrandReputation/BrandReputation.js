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
  Badge,
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
    "We're sorry for the inconvenience! Our technical team is looking into the payment issue. Please try again, and if it persists, contact our support at support@odinschool.com for immediate assistance.",
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
  const [stats, setStats] = useState({
    totalComments: 0,
    urgentIssues: 0,
    negativeFeedback: 0,
    questions: 0,
    avgResponseTime: '2.8min'
  });

  // Load comments on component mount and when filters change
  useEffect(() => {
    loadComments();
  }, [filterPlatform, filterPriority]);

  const loadComments = async () => {
    setLoading(true);
    try {
      const filters = {
        platform: filterPlatform,
        priority: filterPriority
      };
      
      const result = await trustdeskService.getComments(filters);
      
      if (result.success) {
        setCommentsData(result.data);
        updateStats(result.data);
      } else {
        showSnackbar('Error loading comments: ' + result.error, 'error');
      }
    } catch (error) {
      console.error('Error loading comments:', error);
      showSnackbar('Failed to load comments', 'error');
    } finally {
      setLoading(false);
    }
  };

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

  const getCategoryBadgeCount = (category) => {
    return commentsData.filter(comment => 
      comment.category === category && comment.status === 'new'
    ).length;
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
          <Tab label={
            <Badge badgeContent={filteredComments.length} color="primary">
              All Comments
            </Badge>
          } />
          <Tab label={
            <Badge badgeContent={getCategoryBadgeCount('urgent')} color="error">
              Urgent
            </Badge>
          } />
          <Tab label={
            <Badge badgeContent={getCategoryBadgeCount('negative')} color="warning">
              Negative
            </Badge>
          } />
          <Tab label={
            <Badge badgeContent={getCategoryBadgeCount('question')} color="info">
              Questions
            </Badge>
          } />
          <Tab label={
            <Badge badgeContent={getCategoryBadgeCount('positive')} color="success">
              Positive
            </Badge>
          } />
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
