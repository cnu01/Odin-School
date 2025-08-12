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
  TextField,
  Avatar,
  Paper,
  Tabs,
  Tab,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Divider,
} from '@mui/material';
import {
  Search,
  Analytics,
  TrendingUp,
  Visibility,
  ThumbUp,
  Share,
  Language,
  LocationOn,
  People,
  PlayArrow,
  Assessment,
  Psychology,
} from '@mui/icons-material';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';

// Mock creator data
const creatorsData = [
  {
    id: 1,
    name: 'TechGuruRaj',
    avatar: 'https://via.placeholder.com/100',
    platform: 'YouTube',
    followers: '2.5M',
    avgViews: '450K',
    engagement: '8.2%',
    niche: 'Technology',
    languages: ['Hindi', 'English'],
    location: 'Mumbai',
    fitScore: 92,
    estimatedCost: '₹2,50,000',
    lastCampaign: '3 months ago',
    tags: ['AI', 'Programming', 'Tech Reviews'],
  },
  {
    id: 2,
    name: 'DataScienceQueen',
    avatar: 'https://via.placeholder.com/100',
    platform: 'Instagram',
    followers: '850K',
    avgViews: '120K',
    engagement: '12.5%',
    niche: 'Data Science',
    languages: ['English'],
    location: 'Bangalore',
    fitScore: 89,
    estimatedCost: '₹1,75,000',
    lastCampaign: 'Never',
    tags: ['Python', 'Machine Learning', 'Career Tips'],
  },
  {
    id: 3,
    name: 'CodeWithArjun',
    avatar: 'https://via.placeholder.com/100',
    platform: 'YouTube',
    followers: '1.2M',
    avgViews: '280K',
    engagement: '6.8%',
    niche: 'Programming',
    languages: ['Hindi', 'English'],
    location: 'Delhi',
    fitScore: 85,
    estimatedCost: '₹2,00,000',
    lastCampaign: '6 months ago',
    tags: ['Web Development', 'JavaScript', 'React'],
  },
];

const audienceData = [
  { name: 'Tech Professionals', value: 35, color: '#1976d2' },
  { name: 'Students', value: 28, color: '#ff9800' },
  { name: 'Career Switchers', value: 22, color: '#4caf50' },
  { name: 'Entrepreneurs', value: 15, color: '#f44336' },
];

const geoData = [
  { location: 'Mumbai', percentage: 22 },
  { location: 'Bangalore', percentage: 18 },
  { location: 'Delhi', percentage: 16 },
  { location: 'Pune', percentage: 12 },
  { location: 'Hyderabad', percentage: 10 },
  { location: 'Others', percentage: 22 },
];

const performanceMetrics = [
  { metric: 'Content Relevance', score: 92, fullMark: 100 },
  { metric: 'Audience Alignment', score: 89, fullMark: 100 },
  { metric: 'Engagement Quality', score: 85, fullMark: 100 },
  { metric: 'Brand Safety', score: 95, fullMark: 100 },
  { metric: 'Cost Efficiency', score: 78, fullMark: 100 },
  { metric: 'Conversion Potential', score: 88, fullMark: 100 },
];

function InfluencerHub() {
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedCreator, setSelectedCreator] = useState(null);
  const [analyzeDialogOpen, setAnalyzeDialogOpen] = useState(false);
  const [analyzeUrl, setAnalyzeUrl] = useState('');
  const [filterNiche, setFilterNiche] = useState('all');

  const getFitScoreColor = (score) => {
    if (score >= 90) return 'success';
    if (score >= 80) return 'warning';
    return 'error';
  };

  const CreatorCard = ({ creator }) => (
    <Card sx={{ height: '100%', cursor: 'pointer' }} onClick={() => setSelectedCreator(creator)}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar src={creator.avatar} sx={{ width: 60, height: 60, mr: 2 }}>
            {creator.name[0]}
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              {creator.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {creator.platform} • {creator.followers} followers
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
              <LocationOn sx={{ fontSize: 16, color: 'text.secondary' }} />
              <Typography variant="caption">{creator.location}</Typography>
            </Box>
          </Box>
          <Chip
            label={`${creator.fitScore}%`}
            color={getFitScoreColor(creator.fitScore)}
            variant="filled"
            size="small"
          />
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Fit Score
          </Typography>
          <LinearProgress
            variant="determinate"
            value={creator.fitScore}
            color={getFitScoreColor(creator.fitScore)}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>

        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Avg Views
            </Typography>
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              {creator.avgViews}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Engagement
            </Typography>
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              {creator.engagement}
            </Typography>
          </Grid>
        </Grid>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Topics
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {creator.tags.map((tag, index) => (
              <Chip key={index} label={tag} size="small" variant="outlined" />
            ))}
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="subtitle2" color="text.secondary">
            Est. Cost: {creator.estimatedCost}
          </Typography>
          <Button size="small" variant="outlined">
            View Details
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  const CreatorAnalysisDialog = () => (
    <Dialog open={!!selectedCreator} onClose={() => setSelectedCreator(null)} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar src={selectedCreator?.avatar} sx={{ width: 50, height: 50 }}>
            {selectedCreator?.name[0]}
          </Avatar>
          <Box>
            <Typography variant="h6">{selectedCreator?.name}</Typography>
            <Typography variant="body2" color="text.secondary">
              {selectedCreator?.platform} • {selectedCreator?.followers} followers
            </Typography>
          </Box>
          <Box sx={{ ml: 'auto' }}>
            <Chip
              label={`Fit Score: ${selectedCreator?.fitScore}%`}
              color={getFitScoreColor(selectedCreator?.fitScore)}
              variant="filled"
            />
          </Box>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Grid container spacing={3}>
          {/* AI Analysis */}
          <Grid item xs={12}>
            <Alert severity="success" icon={<Psychology />}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                AI-Powered Creator Analysis
              </Typography>
              <Typography variant="body2">
                <strong>High Fit Score (92%):</strong> Content aligns perfectly with Odin School's target audience. 
                Recent videos on "Career Switch to Tech" and "AI Fundamentals" show strong engagement from our 
                demographic. Audience is 65% career switchers aged 22-35.
              </Typography>
            </Alert>
          </Grid>

          {/* Performance Radar Chart */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Performance Metrics
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={performanceMetrics}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="metric" />
                  <PolarRadiusAxis domain={[0, 100]} />
                  <Radar
                    dataKey="score"
                    stroke="#1976d2"
                    fill="#1976d2"
                    fillOpacity={0.3}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>

          {/* Audience Breakdown */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Audience Breakdown
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={audienceData}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {audienceData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>

          {/* Geographic Distribution */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Geographic Distribution
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {geoData.map((item, index) => (
                  <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Typography variant="body2" sx={{ minWidth: 80 }}>
                      {item.location}
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={item.percentage}
                      sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                    />
                    <Typography variant="body2" sx={{ minWidth: 40 }}>
                      {item.percentage}%
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Paper>
          </Grid>

          {/* Campaign Forecast */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Campaign Forecast
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Estimated Reach</Typography>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    380K - 450K
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Predicted Leads</Typography>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'success.main' }}>
                    450 - 650
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Estimated CPL</Typography>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    ₹385 - ₹555
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">ROI Projection</Typography>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'success.main' }}>
                    2.8x - 3.5x
                  </Typography>
                </Box>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={() => setSelectedCreator(null)}>Close</Button>
        <Button variant="outlined">Save to Shortlist</Button>
        <Button variant="contained">Start Campaign</Button>
      </DialogActions>
    </Dialog>
  );

  const AnalyzeCreatorDialog = () => (
    <Dialog open={analyzeDialogOpen} onClose={() => setAnalyzeDialogOpen(false)} maxWidth="sm" fullWidth>
      <DialogTitle>Analyze New Creator</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 2 }}>
          <TextField
            fullWidth
            label="Creator Profile URL"
            placeholder="https://youtube.com/@creator or https://instagram.com/creator"
            value={analyzeUrl}
            onChange={(e) => setAnalyzeUrl(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Typography variant="body2" color="text.secondary">
            Enter a YouTube, Instagram, or other social media profile URL to get AI-powered analysis 
            of fit score, audience alignment, and performance predictions.
          </Typography>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setAnalyzeDialogOpen(false)}>Cancel</Button>
        <Button variant="contained" disabled={!analyzeUrl}>
          Analyze Creator
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
            Influencer Hub
          </Typography>
          <Typography variant="body2" color="text.secondary">
            CreatorFit AI • Performance Forecasting • Audience Insights
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Psychology />}
          onClick={() => setAnalyzeDialogOpen(true)}
        >
          Analyze New Creator
        </Button>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)}>
          <Tab label="Creator Database" />
          <Tab label="Performance Analytics" />
          <Tab label="Campaign Planner" />
        </Tabs>
      </Box>

      {/* Creator Database Tab */}
      {selectedTab === 0 && (
        <Box>
          {/* Search and Filters */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                placeholder="Search creators by name, niche, or location..."
                InputProps={{
                  startAdornment: <Search sx={{ color: 'text.secondary', mr: 1 }} />,
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Niche</InputLabel>
                <Select
                  value={filterNiche}
                  label="Niche"
                  onChange={(e) => setFilterNiche(e.target.value)}
                >
                  <MenuItem value="all">All Niches</MenuItem>
                  <MenuItem value="technology">Technology</MenuItem>
                  <MenuItem value="data-science">Data Science</MenuItem>
                  <MenuItem value="programming">Programming</MenuItem>
                  <MenuItem value="career">Career</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <Button variant="outlined" fullHeight startIcon={<Analytics />}>
                Advanced Filters
              </Button>
            </Grid>
          </Grid>

          {/* Creator Cards */}
          <Grid container spacing={3}>
            {creatorsData.map((creator) => (
              <Grid item xs={12} md={6} lg={4} key={creator.id}>
                <CreatorCard creator={creator} />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Performance Analytics Tab */}
      {selectedTab === 1 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 3 }}>
            Creator Performance Analytics
          </Typography>
          {/* Add analytics content here */}
        </Box>
      )}

      {/* Campaign Planner Tab */}
      {selectedTab === 2 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 3 }}>
            Campaign Planning & Budgeting
          </Typography>
          {/* Add campaign planner content here */}
        </Box>
      )}

      <CreatorAnalysisDialog />
      <AnalyzeCreatorDialog />
    </Box>
  );
}

export default InfluencerHub;
