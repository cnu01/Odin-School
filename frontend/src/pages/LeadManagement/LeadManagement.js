import React, { useState } from 'react';
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
} from '@mui/icons-material';

// Mock lead data with enhanced FirstTouch BOT data
const leadsData = [
  {
    id: 1,
    name: 'Rahul Sharma',
    email: 'rahul.sharma@gmail.com',
    phone: '+91 98765 43210',
    score: 9,
    status: 'new',
    source: 'Data Science Webinar',
    location: 'Mumbai',
    pageviews: 12,
    lastActivity: '2 hours ago',
    botStatus: 'attempted',
    botLastAttempt: '10:15 AM',
    program: 'Full Stack Development',
    avatar: 'RS',
    // Enhanced FirstTouch BOT data
    leadCreatedAt: '2024-01-15 09:45:00',
    firstCallAttempt: '2024-01-15 09:58:00',
    speedToLead: '13 minutes',
    callAttempts: 2,
    callDuration: '0 seconds',
    connectRate: 0,
    qualifiersCaptured: [],
    bookingOffered: false,
    humanHandoffRequested: false,
    botCost: '₹15',
    callOutcome: 'no_answer',
    nextRetry: '2024-01-15 12:15:00',
  },
  {
    id: 2,
    name: 'Priya Patel',
    email: 'priya.patel@outlook.com',
    phone: '+91 87654 32109',
    score: 8,
    status: 'contacted',
    source: 'Organic Search',
    location: 'Bangalore',
    pageviews: 8,
    lastActivity: '5 hours ago',
    botStatus: 'connected',
    botLastAttempt: '9:30 AM',
    program: 'Data Science',
    avatar: 'PP',
    // Enhanced FirstTouch BOT data
    leadCreatedAt: '2024-01-15 08:45:00',
    firstCallAttempt: '2024-01-15 08:52:00',
    speedToLead: '7 minutes',
    callAttempts: 1,
    callDuration: '3 min 45 sec',
    connectRate: 100,
    qualifiersCaptured: ['budget_confirmed', 'timeline_6months', 'background_engineering'],
    bookingOffered: true,
    humanHandoffRequested: false,
    botCost: '₹25',
    callOutcome: 'qualified_booked',
    nextRetry: null,
  },
  {
    id: 3,
    name: 'Amit Kumar',
    email: 'amit.kumar@yahoo.com',
    phone: '+91 76543 21098',
    score: 7,
    status: 'meeting_booked',
    source: 'Instagram Ad',
    location: 'Delhi',
    pageviews: 15,
    lastActivity: '1 day ago',
    botStatus: 'scheduled',
    botLastAttempt: '2:45 PM',
    program: 'AI & Machine Learning',
    avatar: 'AK',
    // Enhanced FirstTouch BOT data
    leadCreatedAt: '2024-01-14 14:30:00',
    firstCallAttempt: '2024-01-14 14:45:00',
    speedToLead: '15 minutes',
    callAttempts: 3,
    callDuration: '5 min 12 sec',
    connectRate: 33,
    qualifiersCaptured: ['budget_flexible', 'timeline_3months', 'background_marketing'],
    bookingOffered: true,
    humanHandoffRequested: true,
    botCost: '₹45',
    callOutcome: 'human_handoff',
    nextRetry: null,
  },
  {
    id: 4,
    name: 'Sneha Singh',
    email: 'sneha.singh@gmail.com',
    phone: '+91 65432 10987',
    score: 6,
    status: 'new',
    source: 'YouTube Video',
    location: 'Pune',
    pageviews: 6,
    lastActivity: '3 hours ago',
    botStatus: 'pending',
    botLastAttempt: null,
    program: 'Product Management',
    avatar: 'SS',
    // Enhanced FirstTouch BOT data
    leadCreatedAt: '2024-01-15 11:30:00',
    firstCallAttempt: null,
    speedToLead: 'Pending',
    callAttempts: 0,
    callDuration: '0 seconds',
    connectRate: 0,
    qualifiersCaptured: [],
    bookingOffered: false,
    humanHandoffRequested: false,
    botCost: '₹0',
    callOutcome: 'pending',
    nextRetry: '2024-01-15 14:30:00',
  },
];

// FirstTouch BOT Performance Metrics
const botMetrics = {
  totalLeads: 1247,
  contactedWithin15Min: 756,
  avgSpeedToLead: '12.3 minutes',
  connectRate: 22,
  avgCallDuration: '2min 34sec',
  totalCost: '₹28,450',
  avgCostPerConnect: '₹43',
  qualifiedBookings: 167,
  humanHandoffs: 89,
  retrySuccess: 34,
};

// Mock scripts and scheduling rules
const botScripts = {
  introduction: "Hi, this is Sarah calling from APEX AI. Am I speaking with {LEAD_NAME}? Great! I'm calling because you recently showed interest in our {PROGRAM_NAME} course. Do you have 2 minutes to discuss how we can help accelerate your career?",
  qualifiers: [
    "What's your current background - are you working in tech or looking to transition?",
    "What's your timeline for starting a new program - within 3 months or 6 months?",
    "What's your budget range for upskilling - under 50k, 50-100k, or above 100k?",
  ],
  booking: "Based on our conversation, I'd love to connect you with one of our career counselors who can provide a personalized roadmap. I have slots available today at 3 PM or tomorrow at 11 AM. Which works better for you?",
  humanHandoff: "I understand you have specific questions about {TOPIC}. Let me connect you with our specialist who can provide detailed information. Please hold for just a moment."
};

const schedulingRules = {
  callingHours: "9:00 AM - 8:00 PM",
  retryInterval: "2 hours",
  maxAttempts: 3,
  noCallDays: ["Sunday"],
  timeZoneHandling: "Lead's local timezone",
  priorityQueue: "Score 8+ gets immediate calling"
};

const activityData = [
  {
    type: 'pageview',
    title: 'Visited Pricing Page',
    time: '2 hours ago',
    icon: <Visibility />,
  },
  {
    type: 'email',
    title: 'Opened welcome email',
    time: '4 hours ago',
    icon: <Email />,
  },
  {
    type: 'bot',
    title: 'BOT: Qualified & booked meeting',
    time: '5 hours ago',
    icon: <SmartToy />,
  },
  {
    type: 'bot',
    title: 'BOT: Captured 3 key qualifiers',
    time: '5 hours ago',
    icon: <SmartToy />,
  },
  {
    type: 'registration',
    title: 'Registered for webinar',
    time: '1 day ago',
    icon: <Person />,
  },
];

function LeadManagement() {
  const [selectedLead, setSelectedLead] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterScore, setFilterScore] = useState('all');
  const [tabValue, setTabValue] = useState(0);
  const [botSettingsOpen, setBotSettingsOpen] = useState(false);

  const getScoreColor = (score) => {
    if (score >= 8) return 'error'; // Hot
    if (score >= 6) return 'warning'; // Warm
    return 'default'; // Cold
  };

  const getScoreLabel = (score) => {
    if (score >= 8) return 'Hot';
    if (score >= 6) return 'Warm';
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

  const getBotStatusColor = (status) => {
    const colors = {
      pending: 'default',
      attempted: 'warning',
      connected: 'success',
      scheduled: 'info',
      failed: 'error',
    };
    return colors[status] || 'default';
  };

  const handleLeadClick = (lead) => {
    setSelectedLead(lead);
    setDialogOpen(true);
  };

  const filteredLeads = leadsData.filter(lead => {
    const statusMatch = filterStatus === 'all' || lead.status === filterStatus;
    const scoreMatch = filterScore === 'all' || 
      (filterScore === 'hot' && lead.score >= 8) ||
      (filterScore === 'warm' && lead.score >= 6 && lead.score < 8) ||
      (filterScore === 'cold' && lead.score < 6);
    return statusMatch && scoreMatch;
  });

  const LeadDetailDialog = () => (
    <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar>{selectedLead?.avatar}</Avatar>
          <Box>
            <Typography variant="h6">{selectedLead?.name}</Typography>
            <Typography variant="body2" color="text.secondary">
              {selectedLead?.email}
            </Typography>
          </Box>
          <Box sx={{ ml: 'auto' }}>
            <Chip
              label={`${getScoreLabel(selectedLead?.score)} Lead (${selectedLead?.score}/10)`}
              color={getScoreColor(selectedLead?.score)}
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
                AI-Generated Lead Summary
              </Typography>
              <Typography variant="body2">
                <strong>Hot Lead (9/10):</strong> Visited pricing page 3 times, attended 'Data Science Webinar', 
                from high-performing source. High engagement with course content. Strong conversion potential.
              </Typography>
            </Alert>
          </Grid>

          {/* Next Best Action */}
          <Grid item xs={12}>
            <Card sx={{ backgroundColor: 'success.50', border: '1px solid', borderColor: 'success.200' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <TrendingUp sx={{ color: 'success.main', mr: 1 }} />
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'success.main' }}>
                    Next Best Action Suggestion
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ mb: 2 }}>
                  <strong>Recommendation:</strong> Send 'Webinar Follow-up' email template immediately. 
                  This lead attended the 'AI in Finance' webinar and hasn't been contacted yet.
                </Typography>
                <Button variant="contained" color="success" size="small">
                  Send Suggested Email
                </Button>
              </CardContent>
            </Card>
          </Grid>

          {/* Enhanced First Touch BOT Status */}
          <Grid item xs={12}>
            <Card sx={{ backgroundColor: 'warning.50', border: '1px solid', borderColor: 'warning.200' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <SmartToy sx={{ color: 'warning.main', mr: 1 }} />
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'warning.main' }}>
                    FirstTouch BOT Performance
                  </Typography>
                </Box>
                
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>Speed to Lead:</strong> {selectedLead?.speedToLead}
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>Call Attempts:</strong> {selectedLead?.callAttempts}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Connect Rate:</strong> {selectedLead?.connectRate}%
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>Call Duration:</strong> {selectedLead?.callDuration}
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>Cost:</strong> {selectedLead?.botCost}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Outcome:</strong> {selectedLead?.callOutcome?.replace('_', ' ')}
                    </Typography>
                  </Grid>
                </Grid>

                {selectedLead?.qualifiersCaptured?.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                      Qualifiers Captured:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selectedLead.qualifiersCaptured.map((qualifier, index) => (
                        <Chip
                          key={index}
                          label={qualifier.replace('_', ' ')}
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Box>
                )}

                {selectedLead?.bookingOffered && (
                  <Alert severity="success" sx={{ mt: 2 }}>
                    <Typography variant="body2">
                      <strong>Booking Offered:</strong> Counselor slot successfully scheduled
                    </Typography>
                  </Alert>
                )}

                {selectedLead?.humanHandoffRequested && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    <Typography variant="body2">
                      <strong>Human Handoff:</strong> Transferred to specialist for complex queries
                    </Typography>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Key Information */}
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
              Lead Information
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Phone sx={{ fontSize: 16, color: 'text.secondary' }} />
                <Typography variant="body2">{selectedLead?.phone}</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <LocationOn sx={{ fontSize: 16, color: 'text.secondary' }} />
                <Typography variant="body2">{selectedLead?.location}</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Language sx={{ fontSize: 16, color: 'text.secondary' }} />
                <Typography variant="body2">Source: {selectedLead?.source}</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Visibility sx={{ fontSize: 16, color: 'text.secondary' }} />
                <Typography variant="body2">{selectedLead?.pageviews} page views</Typography>
              </Box>
            </Box>
          </Grid>

          {/* Activity Timeline */}
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
              Activity Timeline
            </Typography>
            <List sx={{ width: '100%' }}>
              {activityData.map((activity, index) => (
                <ListItem key={index} sx={{ pl: 0 }}>
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                      {activity.icon}
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={activity.title}
                    secondary={activity.time}
                    primaryTypographyProps={{
                      fontSize: '0.875rem',
                      fontWeight: 500,
                    }}
                    secondaryTypographyProps={{
                      fontSize: '0.75rem',
                      color: 'text.secondary',
                    }}
                  />
                </ListItem>
              ))}
            </List>
          </Grid>
        </Grid>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={() => setDialogOpen(false)}>Close</Button>
        <Button variant="contained" startIcon={<Phone />}>
          Call Now
        </Button>
        <Button variant="contained" startIcon={<Email />}>
          Send Email
        </Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
            Lead Management & FirstTouch BOT
          </Typography>
          <Typography variant="body2" color="text.secondary">
            HotLead AI Scoring • FirstTouch BOT Automation • Speed-to-Lead Optimization
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<Settings />} onClick={() => setBotSettingsOpen(true)}>
            Bot Settings
          </Button>
          <Button variant="contained" startIcon={<Assignment />}>
            Assign Leads
          </Button>
        </Box>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Lead Queue" />
          <Tab label="Bot Dashboard" />
          <Tab label="Scripts & Rules" />
        </Tabs>
      </Box>

      {/* Lead Queue Tab */}
      {tabValue === 0 && (
        <>
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
                  <MenuItem value="hot">Hot Leads (8-10)</MenuItem>
                  <MenuItem value="warm">Warm Leads (6-7)</MenuItem>
                  <MenuItem value="cold">Cold Leads (1-5)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                size="small"
                placeholder="Search leads by name, email, or source..."
                InputProps={{
                  startAdornment: <Search sx={{ color: 'text.secondary', mr: 1 }} />,
                }}
              />
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
                      <TableCell>BOT Status</TableCell>
                      <TableCell>Speed to Lead</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredLeads.map((lead) => (
                      <TableRow key={lead.id} hover>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Avatar sx={{ width: 40, height: 40 }}>{lead.avatar}</Avatar>
                            <Box>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                                {lead.name}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {lead.email}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {lead.location} • {lead.pageviews} views
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={`${lead.score}/10`}
                            color={getScoreColor(lead.score)}
                            variant="filled"
                            size="small"
                          />
                          <Typography variant="caption" display="block" color="text.secondary">
                            {getScoreLabel(lead.score)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">{lead.source}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {lead.program}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={lead.status.replace('_', ' ')}
                            color={getStatusColor(lead.status)}
                            variant="outlined"
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Badge badgeContent={lead.botStatus === 'attempted' ? '!' : null} color="warning">
                            <Chip
                              label={lead.botStatus}
                              color={getBotStatusColor(lead.botStatus)}
                              variant="outlined"
                              size="small"
                              icon={<SmartToy />}
                            />
                          </Badge>
                          {lead.botLastAttempt && (
                            <Typography variant="caption" display="block" color="text.secondary">
                              {lead.botLastAttempt}
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ 
                            color: lead.speedToLead === 'Pending' ? 'warning.main' : 
                                   lead.speedToLead.includes('7') ? 'success.main' : 
                                   lead.speedToLead.includes('13') ? 'warning.main' : 'primary.main'
                          }}>
                            {lead.speedToLead}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {lead.callAttempts} attempts
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

      {/* Bot Dashboard Tab */}
      {tabValue === 1 && (
        <>
          {/* Bot Performance Metrics */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Speed sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                  <Typography variant="h4" sx={{ color: 'primary.main', fontWeight: 'bold' }}>
                    {Math.round((botMetrics.contactedWithin15Min / botMetrics.totalLeads) * 100)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Contacted within 15min
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Target: 85%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Timer sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                  <Typography variant="h4" sx={{ color: 'warning.main', fontWeight: 'bold' }}>
                    {botMetrics.avgSpeedToLead}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg Speed to Lead
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Target: &lt;10min
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <CallReceived sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                  <Typography variant="h4" sx={{ color: 'success.main', fontWeight: 'bold' }}>
                    {botMetrics.connectRate}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Connect Rate
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Target: 30%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <AttachMoney sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
                  <Typography variant="h4" sx={{ color: 'info.main', fontWeight: 'bold' }}>
                    {botMetrics.avgCostPerConnect}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Cost per Connect
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Target: ≤₹40
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Additional Metrics */}
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Call Outcomes</Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Qualified Bookings</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: 'success.main' }}>
                      {botMetrics.qualifiedBookings}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Human Handoffs</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: 'info.main' }}>
                      {botMetrics.humanHandoffs}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Retry Success</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: 'warning.main' }}>
                      {botMetrics.retrySuccess}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Cost Analysis</Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Total Monthly Cost</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {botMetrics.totalCost}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Avg Call Duration</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {botMetrics.avgCallDuration}
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={75} 
                    sx={{ mt: 1 }}
                    color="success"
                  />
                  <Typography variant="caption" color="text.secondary">
                    Within budget (₹35k monthly)
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>Bot Status</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ 
                      width: 12, 
                      height: 12, 
                      borderRadius: '50%', 
                      backgroundColor: 'success.main',
                      mr: 1
                    }} />
                    <Typography variant="body2">
                      Active & Processing Leads
                    </Typography>
                  </Box>
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Auto-calling enabled"
                    sx={{ mb: 1 }}
                  />
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Retry logic active"
                  />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </>
      )}

      {/* Scripts & Rules Tab */}
      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Bot Scripts</Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                    Introduction Script
                  </Typography>
                  <Typography variant="body2" sx={{ 
                    backgroundColor: 'grey.50', 
                    p: 2, 
                    borderRadius: 1,
                    fontSize: '0.875rem'
                  }}>
                    {botScripts.introduction}
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                    Key Qualifiers
                  </Typography>
                  {botScripts.qualifiers.map((qualifier, index) => (
                    <Typography key={index} variant="body2" sx={{ 
                      backgroundColor: 'grey.50', 
                      p: 1, 
                      borderRadius: 1,
                      mb: 1,
                      fontSize: '0.875rem'
                    }}>
                      {index + 1}. {qualifier}
                    </Typography>
                  ))}
                </Box>
                <Button variant="outlined" startIcon={<RecordVoiceOver />}>
                  Edit Scripts
                </Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Scheduling Rules</Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Calling Hours:</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {schedulingRules.callingHours}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Retry Interval:</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {schedulingRules.retryInterval}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Max Attempts:</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {schedulingRules.maxAttempts}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Priority Queue:</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {schedulingRules.priorityQueue}
                    </Typography>
                  </Box>
                </Box>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                  Voice AI Configuration
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  STT/TTS integration active with telephony API
                </Typography>
                <Button variant="outlined" startIcon={<Settings />}>
                  Configure Rules
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <LeadDetailDialog />
    </Box>
  );
}

export default LeadManagement;
