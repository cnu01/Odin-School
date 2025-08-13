import React, { useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Alert,
  CircularProgress,
  Button,
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Divider,
  LinearProgress,
  Badge,
  Tooltip,
  IconButton
} from '@mui/material';

import {
  CloudUpload as UploadIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  Person as PersonIcon,
  Assessment as AssessmentIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Cancel as CancelIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon
} from '@mui/icons-material';

import creatorfitService from '../../services/creatorfitService';

const InfluencerHub = () => {
  // State management
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // File upload state
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  
  // Analysis configuration
  const [programType, setProgramType] = useState('data_science');
  const [campaignBudget, setCampaignBudget] = useState(100000);
  const [analysisType, setAnalysisType] = useState('analyze'); // 'analyze' or 'forecast'
  
  // Results state
  const [analysisResults, setAnalysisResults] = useState(null);
  const [creators, setCreators] = useState([]);
  const [businessMetrics, setBusinessMetrics] = useState(null);
  
  // Table pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // Available programs
  const [programs] = useState([
    { value: 'data_science', label: 'Data Science' },
    { value: 'web_development', label: 'Web Development' },
    { value: 'digital_marketing', label: 'Digital Marketing' },
    { value: 'ai_ml', label: 'AI/ML' }
  ]);

  // Utility functions
  const showError = (message) => {
    setError(message);
    setSuccess(null);
  };

  const showSuccess = (message) => {
    setSuccess(message);
    setError(null);
  };

  // File handling
  const handleFileSelect = (file) => {
    const validation = creatorfitService.validateCSVFile(file);
    
    if (!validation.isValid) {
      showError(validation.errors.join(', '));
      return;
    }
    
    setSelectedFile(file);
    setError(null);
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFileSelect(files[0]);
    }
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setDragActive(false);
  }, []);

  // Analysis functions
  const runAnalysis = async () => {
    if (!selectedFile) {
      showError('Please select a CSV file first');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      let result;
      if (analysisType === 'analyze') {
        result = await creatorfitService.analyzeCreators(
          selectedFile, 
          programType, 
          campaignBudget
        );
      } else {
        result = await creatorfitService.forecastLeads(
          selectedFile, 
          programType
        );
      }

      if (result.success) {
        setAnalysisResults(result);
        setCreators(creatorfitService.formatCreatorResults(result.results || []));
        setBusinessMetrics(creatorfitService.formatBusinessMetrics(result.summary));
        
        const analysisTypeLabel = analysisType === 'analyze' ? 'Analysis' : 'Forecasting';
        showSuccess(`${analysisTypeLabel} completed successfully! Found ${result.results?.length || 0} creators.`);
      } else {
        showError(result.error || 'Analysis failed');
      }
    } catch (error) {
      showError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Table pagination handlers
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Get status icon
  const getStatusIcon = (recommendation) => {
    switch (recommendation) {
      case 'BOOK': return <CheckCircleIcon color="success" />;
      case 'REVIEW': return <ScheduleIcon color="warning" />;
      case 'SKIP': return <CancelIcon color="error" />;
      default: return <InfoIcon />;
    }
  };

  // Export results
  const exportResults = () => {
    if (!analysisResults) return;
    
    const dataStr = JSON.stringify(analysisResults, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `creatorfit_${analysisType}_results_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <Box p={3}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            🎯 Influencer Hub - CreatorFit AI
          </Typography>
          <Typography variant="subtitle1" color="textSecondary">
            AI-powered influencer analysis and lead forecasting for EdTech campaigns
          </Typography>
        </Box>
        
        {analysisResults && (
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={exportResults}
          >
            Export Results
          </Button>
        )}
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Configuration Panel */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            📊 Analysis Configuration
          </Typography>
          
          <Grid container spacing={3}>
            {/* File Upload */}
            <Grid item xs={12} md={6}>
              <Paper
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                sx={{
                  border: '2px dashed',
                  borderColor: dragActive ? 'primary.main' : 'grey.300',
                  borderRadius: 2,
                  p: 3,
                  textAlign: 'center',
                  bgcolor: dragActive ? 'action.hover' : 'transparent',
                  cursor: 'pointer'
                }}
                onClick={() => document.getElementById('file-upload').click()}
              >
                <input
                  id="file-upload"
                  type="file"
                  accept=".csv"
                  style={{ display: 'none' }}
                  onChange={(e) => e.target.files[0] && handleFileSelect(e.target.files[0])}
                />
                
                <UploadIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
                
                {selectedFile ? (
                  <Box>
                    <Typography variant="body1" color="primary">
                      ✅ {selectedFile.name}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </Typography>
                  </Box>
                ) : (
                  <Box>
                    <Typography variant="body1" gutterBottom>
                      Drop CSV file here or click to upload
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Supports up to 10MB CSV files
                    </Typography>
                  </Box>
                )}
              </Paper>
            </Grid>

            {/* Configuration Options */}
            <Grid item xs={12} md={6}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Analysis Type</InputLabel>
                    <Select
                      value={analysisType}
                      onChange={(e) => setAnalysisType(e.target.value)}
                      label="Analysis Type"
                    >
                      <MenuItem value="analyze">
                        📊 Comprehensive Analysis
                      </MenuItem>
                      <MenuItem value="forecast">
                        📈 Lead Forecasting
                      </MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Program Type</InputLabel>
                    <Select
                      value={programType}
                      onChange={(e) => setProgramType(e.target.value)}
                      label="Program Type"
                    >
                      {programs.map((program) => (
                        <MenuItem key={program.value} value={program.value}>
                          {program.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                
                {analysisType === 'analyze' && (
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Campaign Budget (₹)"
                      type="number"
                      value={campaignBudget}
                      onChange={(e) => setCampaignBudget(Number(e.target.value))}
                      InputProps={{
                        inputProps: { min: 1000, step: 1000 }
                      }}
                    />
                  </Grid>
                )}
              </Grid>
            </Grid>
          </Grid>

          <Box mt={3}>
            <Button
              variant="contained"
              size="large"
              onClick={runAnalysis}
              disabled={!selectedFile || loading}
              startIcon={loading ? <CircularProgress size={20} /> : <AnalyticsIcon />}
            >
              {loading ? 'Processing...' : `Run ${analysisType === 'analyze' ? 'Analysis' : 'Forecasting'}`}
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Loading Progress */}
      {loading && (
        <Box mb={3}>
          <LinearProgress />
          <Typography variant="body2" align="center" mt={1}>
            Running AI analysis on creators... This may take up to 60 seconds.
          </Typography>
        </Box>
      )}

      {/* Business Metrics Summary */}
      {businessMetrics && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              📈 Business Intelligence Summary
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <TrendingUpIcon color="primary" sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="h5" color="primary">
                    {businessMetrics.totalLeads}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Predicted Leads
                  </Typography>
                </Paper>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <PersonIcon color="success" sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="h5" color="success.main">
                    {businessMetrics.estimatedEnrollments}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Est. Enrollments
                  </Typography>
                </Paper>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <AnalyticsIcon color="info" sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="h5" color="info.main">
                    {businessMetrics.estimatedCPL}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Est. CPL
                  </Typography>
                </Paper>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <AssessmentIcon color="warning" sx={{ fontSize: 32, mb: 1 }} />
                  <Typography variant="h5" color="warning.main">
                    {businessMetrics.estimatedROI}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Est. ROI
                  </Typography>
                </Paper>
              </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="body2" color="textSecondary">
                  Campaign Budget: <strong>{businessMetrics.campaignBudget}</strong>
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Average Confidence: <strong>{businessMetrics.avgConfidence}</strong>
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="body2" color="textSecondary">
                  High Performers: <strong>{businessMetrics.distribution.high_performers || 0}</strong>
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Medium Performers: <strong>{businessMetrics.distribution.medium_performers || 0}</strong>
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Creator Results Table */}
      {creators.length > 0 && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                🎭 Creator Analysis Results ({creators.length} creators)
              </Typography>
              <Tooltip title="Refresh results">
                <IconButton onClick={runAnalysis} disabled={loading}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            </Box>
            
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Rank</TableCell>
                    <TableCell>Creator ID</TableCell>
                    <TableCell>Predicted Leads</TableCell>
                    <TableCell>Fit Score</TableCell>
                    <TableCell>Confidence</TableCell>
                    <TableCell>Topic</TableCell>
                    <TableCell>Views (90d)</TableCell>
                    <TableCell>Tier</TableCell>
                    <TableCell>Recommendation</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {creators
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((creator) => (
                      <TableRow key={creator.creator_id} hover>
                        <TableCell>
                          <Badge badgeContent={creator.rank} color="primary">
                            <Box width={24} />
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {creator.creator_id}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body1" color="primary">
                            {creator.formattedLeads}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {creator.formattedFitScore}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {creator.formattedConfidence}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" noWrap sx={{ maxWidth: 150 }}>
                            {creator.topic}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {creator.formattedViews}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip size="small" label={creator.creator_tier} />
                        </TableCell>
                        <TableCell>
                          <Tooltip title={creator.recommendation}>
                            <Chip
                              size="small"
                              label={creator.recommendation}
                              color={creator.statusColor}
                              icon={getStatusIcon(creator.recommendation)}
                            />
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>
            
            <TablePagination
              rowsPerPageOptions={[5, 10, 25, 50]}
              component="div"
              count={creators.length}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
            />
          </CardContent>
        </Card>
      )}

      {/* No Results State */}
      {!loading && !analysisResults && (
        <Paper sx={{ p: 4, textAlign: 'center', mt: 3 }}>
          <AnalyticsIcon sx={{ fontSize: 64, color: 'grey.400', mb: 2 }} />
          <Typography variant="h6" color="textSecondary" gutterBottom>
            Ready to Analyze Influencers
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Upload a CSV file with creator data to get started with AI-powered analysis
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default InfluencerHub;
