import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  LinearProgress,
  Tooltip,
  Badge,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Snackbar,
  useTheme
} from '@mui/material';
import {
  Upload as UploadIcon,
  Psychology as PsychologyIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Analytics as AnalyticsIcon,
  AutoFixHigh as AutoFixHighIcon,
  Assessment as AssessmentIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  PauseCircle as PauseIcon,
  PlayArrow as PlayIcon,
  SwapHoriz as SwapIcon,
  Visibility as VisibilityIcon,
  Speed as SpeedIcon,
  MonetizationOn as MoneyIcon,
  Group as GroupIcon,
  Campaign as CampaignIcon,
  ContentCopy as CopyIcon
} from '@mui/icons-material';
import adliftService from '../../services/adliftService';

// Tab panel component
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`adlift-tabpanel-${index}`}
      aria-labelledby={`adlift-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function AdLift() {
  const theme = useTheme();
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [uploadDialog, setUploadDialog] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  useEffect(() => {
    // Load demo data on component mount
    loadDemoData();
  }, []);

  const loadDemoData = () => {
    try {
      const mockResults = adliftService.createMockAnalysisResults();
      const processedResults = adliftService.processAnalysisResults(mockResults);
      setAnalysisResults(processedResults);
    } catch (error) {
      console.error('Error loading demo data:', error);
      showSnackbar('Error loading demo data', 'warning');
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      showSnackbar('Please select a CSV file first', 'warning');
      return;
    }

    try {
      setAnalyzing(true);
      const response = await adliftService.analyzeCSVFile(selectedFile);
      
      if (response.success) {
        const processedResults = adliftService.processAnalysisResults(response);
        setAnalysisResults(processedResults);
        setUploadDialog(false);
        setSelectedFile(null);
        showSnackbar('Analysis completed successfully!', 'success');
      } else {
        showSnackbar(response.message || 'Analysis failed', 'error');
      }
    } catch (error) {
      console.error('Error analyzing file:', error);
      showSnackbar('Error analyzing file. Using demo data.', 'warning');
      loadDemoData();
    } finally {
      setAnalyzing(false);
    }
  };

  const downloadSampleCSV = () => {
    const csvContent = adliftService.generateSampleCSV();
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'adlift_sample_data.csv';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    showSnackbar('Sample CSV downloaded', 'success');
  };

  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
            AdLift - Marketing Optimization
          </Typography>
          <Typography variant="body2" color="text.secondary">
            AI-powered ad performance analysis and creative optimization
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={downloadSampleCSV}
          >
            Sample CSV
          </Button>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadDemoData}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<UploadIcon />}
            onClick={() => setUploadDialog(true)}
          >
            Upload & Analyze
          </Button>
        </Box>
      </Box>

      {/* Key Metrics */}
      {analysisResults && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Campaigns
                </Typography>
                <Typography variant="h4" color="primary">
                  {analysisResults.performanceVariance?.total_campaigns || 24}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Under analysis
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  CTR Range
                </Typography>
                <Typography variant="h4" color="warning.main">
                  {analysisResults.performanceVariance?.ctr_range || '0.7% - 3.8%'}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Performance variance
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Decisions Made
                </Typography>
                <Typography variant="h4" color="success.main">
                  {analysisResults.decisionsCount || 24}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Optimization actions
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Expected CTR Lift
                </Typography>
                <Typography variant="h4" color="success.main">
                  +{analysisResults.expectedImpact?.ctr_improvement || '25%'}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  In {analysisResults.expectedImpact?.timeline || '30 days'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* AI Insights Alert */}
      {analysisResults && (
        <Alert severity="info" icon={<PsychologyIcon />} sx={{ mb: 4 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
            AI Analysis Summary
          </Typography>
          <Typography variant="body2">
            Identified {analysisResults.rootCauses?.length || 0} root causes for performance variance. 
            Expected improvements: {analysisResults.expectedImpact?.ctr_improvement || '25%'} CTR increase and {analysisResults.expectedImpact?.cpql_reduction || '20%'} CPQL reduction 
            with {analysisResults.variantsCount || 45} AI-generated variants.
          </Typography>
        </Alert>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Performance Analysis" />
          <Tab label="Creative Fatigue" />
          <Tab label="Root Causes" />
          <Tab label="AI Variants & Decisions" />
        </Tabs>
      </Box>

      {/* Performance Analysis Tab */}
      <TabPanel value={tabValue} index={0}>
        <PerformanceAnalysisView 
          analysisResults={analysisResults}
          onAnalyze={() => setUploadDialog(true)}
        />
      </TabPanel>

      {/* Creative Fatigue Tab */}
      <TabPanel value={tabValue} index={1}>
        <CreativeFatigueView 
          fatigueData={analysisResults?.fatigueDetection || []}
        />
      </TabPanel>

      {/* Root Causes Tab */}
      <TabPanel value={tabValue} index={2}>
        <RootCausesView 
          rootCauses={analysisResults?.rootCauses || []}
        />
      </TabPanel>

      {/* AI Variants & Decisions Tab */}
      <TabPanel value={tabValue} index={3}>
        <AIVariantsView 
          analysisResults={analysisResults}
        />
      </TabPanel>

      {/* Upload Dialog */}
      <Dialog 
        open={uploadDialog} 
        onClose={() => !analyzing && setUploadDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <UploadIcon />
            Upload Ad Performance Data
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ p: 2 }}>
            <Typography variant="body2" sx={{ mb: 2 }}>
              Upload a CSV file with your ad performance data for AI analysis.
            </Typography>
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Required columns:
              </Typography>
              <Typography variant="body2" color="text.secondary">
                date, campaign, ad_group, headline, description, keywords, audience_segment, 
                placement, impressions, clicks, spend, leads, qualified_leads, CTR, CPC, CVR, qualified_rate
              </Typography>
            </Box>

            <input
              type="file"
              accept=".csv"
              onChange={(e) => setSelectedFile(e.target.files[0])}
              style={{ marginBottom: '16px' }}
            />

            {selectedFile && (
              <Alert severity="info" sx={{ mt: 2 }}>
                Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
              </Alert>
            )}

            {analyzing && (
              <Box sx={{ mt: 2, textAlign: 'center' }}>
                <CircularProgress />
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Analyzing ad performance data...
                </Typography>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialog(false)} disabled={analyzing}>
            Cancel
          </Button>
          <Button 
            onClick={downloadSampleCSV} 
            variant="outlined"
            disabled={analyzing}
          >
            Download Sample
          </Button>
          <Button 
            onClick={handleFileUpload} 
            variant="contained"
            disabled={!selectedFile || analyzing}
          >
            {analyzing ? 'Analyzing...' : 'Analyze'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
}

// Performance Analysis Component
const PerformanceAnalysisView = ({ analysisResults, onAnalyze }) => {
  if (!analysisResults) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <PsychologyIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          No Analysis Data Available
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Upload your ad performance CSV to get AI-powered insights
        </Typography>
        <Button variant="contained" onClick={onAnalyze} startIcon={<UploadIcon />}>
          Upload & Analyze Data
        </Button>
      </Box>
    );
  }

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Performance Variance Analysis
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                CTR Range: {analysisResults.performanceVariance?.ctr_range || 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                CPQL Variance: {analysisResults.performanceVariance?.cpql_variance || 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Average QPI: {(analysisResults.performanceVariance?.qpi_average * 1000)?.toFixed(3) || 'N/A'} per mille
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Campaign Decisions Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="error.main">
                    {analysisResults.campaignDecisions?.pause_count || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pause
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="success.main">
                    {analysisResults.campaignDecisions?.keep_count || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Keep
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="warning.main">
                    {analysisResults.campaignDecisions?.monitor_count || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Monitor
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Expected Impact Projections
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={6} md={3}>
                <Box>
                  <Typography variant="h5" color="success.main">
                    +{analysisResults.expectedImpact?.ctr_improvement || '25%'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    CTR Improvement
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box>
                  <Typography variant="h5" color="success.main">
                    -{analysisResults.expectedImpact?.cpql_reduction || '20%'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    CPQL Reduction
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box>
                  <Typography variant="h5" color="primary.main">
                    +{analysisResults.expectedImpact?.qualified_leads_improvement || '30%'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Qualified Leads
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box>
                  <Typography variant="h5" color="info.main">
                    {analysisResults.expectedImpact?.timeline || '30 days'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Timeline
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

// Creative Fatigue Component
const CreativeFatigueView = ({ fatigueData }) => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>
          Creative Fatigue Detection
        </Typography>
        {fatigueData.length === 0 ? (
          <Alert severity="info">
            No creative fatigue detected in current campaigns.
          </Alert>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Campaign</TableCell>
                  <TableCell>Days Live</TableCell>
                  <TableCell>Performance Drop</TableCell>
                  <TableCell>Original CTR</TableCell>
                  <TableCell>Current CTR</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {fatigueData.map((item, index) => {
                  const fatigueStatus = adliftService.getFatigueStatus(item);
                  return (
                    <TableRow key={index}>
                      <TableCell>{item.campaign}</TableCell>
                      <TableCell>{item.days_live}</TableCell>
                      <TableCell>
                        <Typography color="error.main">
                          -{(item.performance_drop * 100).toFixed(1)}%
                        </Typography>
                      </TableCell>
                      <TableCell>{(item.original_ctr * 100).toFixed(2)}%</TableCell>
                      <TableCell>{(item.current_ctr * 100).toFixed(2)}%</TableCell>
                      <TableCell>
                        <Chip 
                          label={fatigueStatus.status}
                          size="small"
                          sx={{ 
                            backgroundColor: fatigueStatus.color,
                            color: 'white'
                          }}
                        />
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Grid>
    </Grid>
  );
};

// Root Causes Component
const RootCausesView = ({ rootCauses }) => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" gutterBottom>
          Identified Root Causes
        </Typography>
        {rootCauses.map((cause, index) => (
          <Card key={index} sx={{ mb: 2 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                <Typography variant="h6" color="error">
                  {cause.name}
                </Typography>
                <Chip 
                  label={`${cause.case_count} cases`}
                  size="small"
                  color="warning"
                />
              </Box>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {cause.description}
              </Typography>
              
              {cause.evidence && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Evidence:
                  </Typography>
                  {cause.evidence.map((evidence, evidenceIndex) => (
                    <Typography key={evidenceIndex} variant="body2" color="text.secondary">
                      • {evidence.metric}: {evidence.value} {evidence.note && `(${evidence.note})`}
                    </Typography>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        ))}
      </Grid>
    </Grid>
  );
};

// AI Variants Component
const AIVariantsView = ({ analysisResults }) => {
  if (!analysisResults) {
    return <Typography>No variant data available</Typography>;
  }

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              AI-Generated Variants
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="h4" color="primary">
                {analysisResults.variantsCount || 45}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                New variants created
              </Typography>
            </Box>
            <Typography variant="body2">
              AI has generated fresh headlines, descriptions, and keyword sets 
              based on winning patterns and performance analysis.
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Rotation Decisions
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="h4" color="success.main">
                {analysisResults.decisionsCount || 24}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Decisions made
              </Typography>
            </Box>
            <Typography variant="body2">
              Automated recommendations for pausing, keeping, or replacing 
              campaigns based on performance and fatigue analysis.
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Alert severity="success" icon={<AutoFixHighIcon />}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
            AI Optimization Complete
          </Typography>
          <Typography variant="body2">
            Analysis complete with {analysisResults.variantsCount || 45} AI variants generated. 
            Expected improvements: {analysisResults.expectedImpact?.ctr_improvement || '25%'} CTR increase, 
            {analysisResults.expectedImpact?.cpql_reduction || '20%'} CPQL reduction in {analysisResults.expectedImpact?.timeline || '30 days'}.
          </Typography>
        </Alert>
      </Grid>
    </Grid>
  );
};

export default AdLift;
