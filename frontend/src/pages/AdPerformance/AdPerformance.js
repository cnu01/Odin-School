import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Chip,
  Button,
  Paper,
  Tabs,
  Tab,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Avatar,
  IconButton,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Psychology,
  AutoFixHigh,
  Share,
  Person,
  ContentCopy,
  Refresh,
  Add,
  Edit,
  Pause,
  PlayArrow,
  Download,
  WhatsApp,
  Email,
  Facebook,
  Instagram,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

// Mock ad performance data
const adCampaigns = [
  {
    id: 1,
    name: 'Data Science Masterclass 2024',
    platform: 'Facebook',
    status: 'active',
    budget: '₹50,000',
    spent: '₹32,450',
    impressions: '2.4M',
    clicks: '18,340',
    ctr: '0.76%',
    cpl: '₹485',
    leads: 67,
    conversions: 12,
    roas: '3.2x',
    image: 'https://via.placeholder.com/300x200',
    creativeScore: 85,
    fatigue: 'medium',
  },
  {
    id: 2,
    name: 'Full Stack Career Switch',
    platform: 'Instagram',
    status: 'active',
    budget: '₹75,000',
    spent: '₹68,200',
    impressions: '3.1M',
    clicks: '24,780',
    ctr: '0.80%',
    cpl: '₹520',
    leads: 131,
    conversions: 28,
    roas: '4.1x',
    image: 'https://via.placeholder.com/300x200',
    creativeScore: 92,
    fatigue: 'low',
  },
  {
    id: 3,
    name: 'AI & Machine Learning Bootcamp',
    platform: 'Google',
    status: 'paused',
    budget: '₹40,000',
    spent: '₹38,900',
    impressions: '1.8M',
    clicks: '12,650',
    ctr: '0.70%',
    cpl: '₹675',
    leads: 58,
    conversions: 8,
    roas: '2.1x',
    image: 'https://via.placeholder.com/300x200',
    creativeScore: 68,
    fatigue: 'high',
  },
];

// Mock referral data
const referralData = [
  {
    id: 1,
    name: 'Rahul Mehta',
    avatar: 'RM',
    course: 'Data Science',
    completionDate: '2 months ago',
    engagementScore: 95,
    referralProbability: 'High',
    totalReferrals: 3,
    successfulReferrals: 2,
    earnedRewards: '₹15,000',
    lastActivity: '1 week ago',
    preferredChannels: ['WhatsApp', 'LinkedIn'],
  },
  {
    id: 2,
    name: 'Priya Singh',
    avatar: 'PS',
    course: 'Full Stack Development',
    completionDate: '1 month ago',
    engagementScore: 88,
    referralProbability: 'High',
    totalReferrals: 5,
    successfulReferrals: 4,
    earnedRewards: '₹25,000',
    lastActivity: '3 days ago',
    preferredChannels: ['Instagram', 'WhatsApp'],
  },
  {
    id: 3,
    name: 'Amit Kumar',
    avatar: 'AK',
    course: 'AI & ML',
    completionDate: '3 weeks ago',
    engagementScore: 92,
    referralProbability: 'Medium',
    totalReferrals: 1,
    successfulReferrals: 1,
    earnedRewards: '₹7,500',
    lastActivity: '2 days ago',
    preferredChannels: ['Email', 'Facebook'],
  },
];

const performanceMetrics = [
  { month: 'Jan', adSpend: 125000, leads: 245, referralLeads: 89 },
  { month: 'Feb', adSpend: 140000, leads: 298, referralLeads: 112 },
  { month: 'Mar', adSpend: 135000, leads: 276, referralLeads: 95 },
  { month: 'Apr', adSpend: 165000, leads: 342, referralLeads: 128 },
  { month: 'May', adSpend: 180000, leads: 398, referralLeads: 156 },
];

const referralChannelData = [
  { channel: 'WhatsApp', referrals: 45, color: '#25d366' },
  { channel: 'Instagram', referrals: 32, color: '#e1306c' },
  { channel: 'LinkedIn', referrals: 28, color: '#0077b5' },
  { channel: 'Facebook', referrals: 22, color: '#1877f2' },
  { channel: 'Email', referrals: 18, color: '#ea4335' },
];

function AdPerformance() {
  const [selectedTab, setSelectedTab] = useState(0);
  const [variantDialog, setVariantDialog] = useState(false);
  const [selectedAd, setSelectedAd] = useState(null);
  const [referralDialog, setReferralDialog] = useState(false);
  const [selectedReferrer, setSelectedReferrer] = useState(null);
  const [generatedMessage, setGeneratedMessage] = useState('');

  const getStatusColor = (status) => {
    const colors = {
      active: 'success',
      paused: 'warning',
      ended: 'error',
    };
    return colors[status] || 'default';
  };

  const getFatigueColor = (fatigue) => {
    const colors = {
      low: 'success',
      medium: 'warning',
      high: 'error',
    };
    return colors[fatigue] || 'default';
  };

  const getProbabilityColor = (probability) => {
    const colors = {
      High: 'success',
      Medium: 'warning',
      Low: 'error',
    };
    return colors[probability] || 'default';
  };

  const generateAdVariants = (ad) => {
    const variants = [
      {
        headline: 'Transform Your Career in 6 Months',
        description: 'Join thousands who switched to tech careers with our industry-proven curriculum.',
        cta: 'Start Your Journey Today',
      },
      {
        headline: 'Land Your Dream Tech Job',
        description: 'From zero to hero - our graduates get 40% salary hikes on average.',
        cta: 'Claim Your Spot Now',
      },
      {
        headline: 'Master In-Demand Skills Fast',
        description: 'Live projects, expert mentors, and guaranteed placement support included.',
        cta: 'Enroll Now & Save 30%',
      },
    ];
    return variants;
  };

  const generateReferralMessage = (referrer) => {
    const messages = [
      `Hey! I just completed the ${referrer.course} course at Odin School and it was incredible! The hands-on projects and mentorship really helped me level up my skills. Thought you might be interested too! 🚀`,
      `Just wanted to share - I recently finished the ${referrer.course} program at Odin School. The curriculum is so practical and industry-relevant. They're offering some great courses that might align with your career goals!`,
      `Hi! Remember how I was planning to upskill in tech? Well, I just completed the ${referrer.course} course at Odin School and I'm amazed by the transformation! The projects were real-world and the support was fantastic. Check it out!`,
    ];
    return messages[Math.floor(Math.random() * messages.length)];
  };

  const AdCard = ({ ad }) => (
    <Card sx={{ height: '100%' }}>
      <CardMedia
        component="img"
        height="160"
        image={ad.image}
        alt={ad.name}
      />
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '1rem' }}>
            {ad.name}
          </Typography>
          <Chip
            label={ad.status}
            color={getStatusColor(ad.status)}
            size="small"
            variant="filled"
          />
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">Platform</Typography>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>{ad.platform}</Typography>
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">CTR</Typography>
          <Typography variant="body2" sx={{ fontWeight: 600, color: 'success.main' }}>
            {ad.ctr}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">CPL</Typography>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>{ad.cpl}</Typography>
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="body2" color="text.secondary">ROAS</Typography>
          <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main' }}>
            {ad.roas}
          </Typography>
        </Box>

        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">Creative Score</Typography>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>{ad.creativeScore}%</Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={ad.creativeScore}
            color={ad.creativeScore >= 80 ? 'success' : ad.creativeScore >= 60 ? 'warning' : 'error'}
            sx={{ height: 6, borderRadius: 3 }}
          />
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="body2" color="text.secondary">Creative Fatigue</Typography>
          <Chip
            label={ad.fatigue}
            color={getFatigueColor(ad.fatigue)}
            size="small"
            variant="outlined"
          />
        </Box>

        <Divider sx={{ my: 2 }} />

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            size="small"
            variant="contained"
            startIcon={<AutoFixHigh />}
            onClick={() => {
              setSelectedAd(ad);
              setVariantDialog(true);
            }}
            disabled={ad.fatigue === 'low'}
          >
            Generate Variants
          </Button>
          <IconButton size="small" color="primary">
            <Edit />
          </IconButton>
          <IconButton size="small" color={ad.status === 'active' ? 'warning' : 'success'}>
            {ad.status === 'active' ? <Pause /> : <PlayArrow />}
          </IconButton>
        </Box>
      </CardContent>
    </Card>
  );

  const ReferrerCard = ({ referrer }) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>{referrer.avatar}</Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
              {referrer.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {referrer.course} • Completed {referrer.completionDate}
            </Typography>
          </Box>
          <Chip
            label={referrer.referralProbability}
            color={getProbabilityColor(referrer.referralProbability)}
            size="small"
            variant="filled"
          />
        </Box>

        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Engagement Score
            </Typography>
            <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
              {referrer.engagementScore}%
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Success Rate
            </Typography>
            <Typography variant="h6" sx={{ fontWeight: 600, color: 'success.main' }}>
              {Math.round((referrer.successfulReferrals / referrer.totalReferrals) * 100)}%
            </Typography>
          </Grid>
        </Grid>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Total Referrals: {referrer.totalReferrals}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Earned: {referrer.earnedRewards}
          </Typography>
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Preferred Channels
          </Typography>
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            {referrer.preferredChannels.map((channel, index) => (
              <Chip key={index} label={channel} size="small" variant="outlined" />
            ))}
          </Box>
        </Box>

        <Button
          fullWidth
          variant="contained"
          startIcon={<Share />}
          onClick={() => {
            setSelectedReferrer(referrer);
            setGeneratedMessage(generateReferralMessage(referrer));
            setReferralDialog(true);
          }}
        >
          Generate Referral Message
        </Button>
      </CardContent>
    </Card>
  );

  const AdVariantDialog = () => (
    <Dialog open={variantDialog} onClose={() => setVariantDialog(false)} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Psychology />
          <Typography variant="h6">AI-Generated Ad Variants</Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            Your current ad shows signs of creative fatigue. Here are AI-generated variants 
            to refresh your campaign and combat declining performance.
          </Typography>
        </Alert>

        <Grid container spacing={2}>
          {generateAdVariants(selectedAd).map((variant, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Paper sx={{ p: 2, border: '1px solid', borderColor: 'divider' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                  Variant {index + 1}
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 1, fontSize: '1rem' }}>
                  {variant.headline}
                </Typography>
                <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
                  {variant.description}
                </Typography>
                <Button variant="contained" size="small" fullWidth>
                  {variant.cta}
                </Button>
                <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                  <Button size="small" variant="outlined" startIcon={<ContentCopy />}>
                    Copy
                  </Button>
                  <Button size="small" variant="outlined" startIcon={<Edit />}>
                    Edit
                  </Button>
                </Box>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={() => setVariantDialog(false)}>Close</Button>
        <Button variant="contained">Apply Selected Variants</Button>
      </DialogActions>
    </Dialog>
  );

  const ReferralMessageDialog = () => (
    <Dialog open={referralDialog} onClose={() => setReferralDialog(false)} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Typography variant="h6">Personalized Referral Message</Typography>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
            For: {selectedReferrer?.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            High engagement learner with {selectedReferrer?.referralProbability.toLowerCase()} referral probability
          </Typography>
        </Box>

        <TextField
          fullWidth
          multiline
          rows={4}
          label="Generated Message"
          value={generatedMessage}
          onChange={(e) => setGeneratedMessage(e.target.value)}
          sx={{ mb: 2 }}
        />

        <Alert severity="success" sx={{ mb: 2 }}>
          <Typography variant="caption">
            ✓ Message is authentic and personal ✓ Mentions specific course experience
          </Typography>
        </Alert>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button size="small" variant="outlined" onClick={() => setGeneratedMessage(generateReferralMessage(selectedReferrer))}>
            Generate New
          </Button>
          <Button size="small" variant="outlined" startIcon={<ContentCopy />}>
            Copy Message
          </Button>
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={() => setReferralDialog(false)}>Close</Button>
        <Button variant="contained" startIcon={<WhatsApp />}>
          Send via WhatsApp
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
            Ad & Referral Performance
          </Typography>
          <Typography variant="body2" color="text.secondary">
            AdLift Creative Optimization • ReferMore Referral Management
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<Download />}>
            Export Report
          </Button>
          <Button variant="contained" startIcon={<Add />}>
            New Campaign
          </Button>
        </Box>
      </Box>

      {/* Performance Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                Performance Trends
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceMetrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Bar yAxisId="left" dataKey="adSpend" fill="#1976d2" name="Ad Spend (₹)" />
                  <Line yAxisId="right" type="monotone" dataKey="leads" stroke="#ff9800" strokeWidth={3} name="Paid Leads" />
                  <Line yAxisId="right" type="monotone" dataKey="referralLeads" stroke="#4caf50" strokeWidth={3} name="Referral Leads" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} lg={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                Referral Channels
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={referralChannelData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="referrals"
                    label={({ channel, referrals }) => `${channel}: ${referrals}`}
                  >
                    {referralChannelData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)}>
          <Tab label="Ad Campaigns (AdLift)" />
          <Tab label="Referral Program (ReferMore)" />
        </Tabs>
      </Box>

      {/* Ad Campaigns Tab */}
      {selectedTab === 0 && (
        <Grid container spacing={3}>
          {adCampaigns.map((ad) => (
            <Grid item xs={12} md={6} lg={4} key={ad.id}>
              <AdCard ad={ad} />
            </Grid>
          ))}
        </Grid>
      )}

      {/* Referral Program Tab */}
      {selectedTab === 1 && (
        <Box>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                  156
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Referrals This Month
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                  78%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Conversion Rate
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'warning.main' }}>
                  ₹3.2L
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Rewards Paid Out
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'info.main' }}>
                  4.2x
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Referral Program ROI
                </Typography>
              </Paper>
            </Grid>
          </Grid>

          <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
            Likely Referrers - High Engagement Learners
          </Typography>
          
          <Grid container spacing={3}>
            {referralData.map((referrer) => (
              <Grid item xs={12} md={6} lg={4} key={referrer.id}>
                <ReferrerCard referrer={referrer} />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      <AdVariantDialog />
      <ReferralMessageDialog />
    </Box>
  );
}

export default AdPerformance;
