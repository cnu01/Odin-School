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
  LinearProgress,
  Badge,
  Tooltip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
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
  const [analysisType, setAnalysisType] = useState('analyze'); // 'analyze' or 'forecast'
  
  // Results state
  const [analysisResults, setAnalysisResults] = useState(null);
  const [creators, setCreators] = useState([]);
  
  // Modal state for View Input
  const [inputModalOpen, setInputModalOpen] = useState(false);
  const [selectedCreatorInput, setSelectedCreatorInput] = useState(null);
  
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
        );
      } else {
        result = await creatorfitService.forecastLeads(
          selectedFile, 
          programType
        );
      }

             if (result.success) {
         setAnalysisResults(result);
         let formattedCreators = creatorfitService.formatCreatorResults(result.results || []);
         
         // Sort by recommendation priority for analyze endpoint
         if (analysisType === 'analyze') {
           const recommendationPriority = { 'BOOK': 1, 'REVIEW': 2, 'SKIP': 3 };
           formattedCreators.sort((a, b) => {
             const priorityA = recommendationPriority[a.recommendation] || 4;
             const priorityB = recommendationPriority[b.recommendation] || 4;
             return priorityA - priorityB;
           });
           
           // Update ranks after sorting
           formattedCreators.forEach((creator, index) => {
             creator.rank = index + 1;
           });
         }
         
         setCreators(formattedCreators);
         
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

  const handleViewInput = ({input_data}) => {

    const inputData = {
      creator_id: input_data?.creator_id ?? "Unknown Creator",
      topic: input_data?.topic ?? "Unknown Topic",
      recent_video_transcript: input_data?.recent_video_transcript || "Sample transcript data",
      posting_cadence_days: input_data?.posting_cadence_days ?? 0,
      views_90d: input_data?.views_90d ?? 0,
      clicks: input_data?.clicks ?? 0,
      leads: input_data?.leads ?? 0,
      qualified_leads: input_data?.qualified_leads ?? 0,
      enrollments: input_data?.enrollments ?? 0,
      refunds: input_data?.refunds ?? 0,
      geography: input_data?.geography ?? "Unknown",
      language: input_data?.language ?? "Unknown",
    };
    
    setSelectedCreatorInput(inputData);
    setInputModalOpen(true);
  };

  return (
    <Box p={3}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box sx={{ width: '100%' }}>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
            Influencer Hub - CreatorFit AI
          </Typography>
          <Typography variant="subtitle1" color="textSecondary">
            AI-powered influencer analysis and lead forecasting for EdTech campaigns
          </Typography>
        <Alert severity="info" sx={{ mb: 3, mt: 3, borderRadius: '4px', width: '100%' }}>
            <Typography variant="body2" component="div">
              <strong>What this analysis delivers</strong>
              <Box component="ul" sx={{ pl: 3, my: 0, mt: 1, '& > li': { mb: 1.25 } }}>
                <li>
                  <strong>Diagnosis</strong>: Reasons why some creators underperform
                </li>
                <li>
                  <strong>Solutions</strong>: AI-driven ways to score fit between creator content and programs
                </li>
                <li>
                  <strong>Forecast qualified leads</strong>: Forecast qualified leads before booking creators
                </li>
                
              </Box>
            </Typography>
        </Alert>
        </Box>
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

      {/* Export Results */}
      {analysisResults && (
        <Box display="flex" justifyContent="flex-end" my={2}>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={exportResults}
          >
            Export Results
          </Button>
        </Box>
      )}

      {/* Creator Results Table */}
      {creators.length > 0 && (
        <Card>
          <CardContent>
                         <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
               <Box>
                 <Typography variant="h6">
                   Creator Analysis Results ({creators.length} creators)
                 </Typography>
                 {analysisType === 'analyze' && (
                   <Typography variant="caption" color="textSecondary">
                     Sorted by recommendation priority: BOOK → REVIEW → SKIP
                   </Typography>
                 )}
                 {analysisType === 'forecast' && (
                   <Typography variant="caption" color="textSecondary">
                     Sorted by predicted leads (highest first)
                   </Typography>
                 )}
               </Box>
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
                    {analysisType === 'forecast' && (
                      <TableCell>Predicted Leads</TableCell>
                    )}
                    <TableCell>Fit Score</TableCell>
                    <TableCell>Confidence</TableCell>
                    <TableCell>Topic</TableCell>
                    <TableCell>Views (90d)</TableCell>
                    <TableCell>Tier</TableCell>
                    <TableCell>Recommendation</TableCell>
                    <TableCell>Insights</TableCell>
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
                        {analysisType === 'forecast' && (
                          <TableCell>
                            <Typography variant="body1" color="primary">
                              {creator.formattedLeads}
                            </Typography>
                          </TableCell>
                        )}
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
                           <Tooltip title={`${creator.recommendation} - ${analysisType === 'analyze' ? 'Priority-based sorting' : 'Lead-based sorting'}`}>
                             <Chip
                               size="small"
                               label={creator.recommendation}
                               color={creator.statusColor}
                               icon={getStatusIcon(creator.recommendation)}
                               sx={{
                                 fontWeight: 'bold',
                                 ...(analysisType === 'analyze' && creator.recommendation === 'BOOK' && {
                                   border: '2px solid',
                                   borderColor: 'success.main'
                                 })
                               }}
                             />
                           </Tooltip>
                         </TableCell>
                        <TableCell padding="none">
                        <Box display="flex" justifyContent="flex-end" my={2} >
                        <Button
                          variant="outlined"
                          onClick={() => handleViewInput(creator)}
                          size="small"
                          sx={{ padding: "2px 6px" }}
                        >
                          View more
                        </Button>
                      </Box>
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

      {/* Input Data Modal */}
      <Dialog 
        open={inputModalOpen} 
        onClose={() => setInputModalOpen(false)} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            <InfoIcon color="primary" />
            <Typography variant="h6">
              Input CSV Data for Creator: {selectedCreatorInput?.creator_id}
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
            This shows the original CSV input values that were used to generate the AI analysis for this creator.
          </Typography>
          
          {selectedCreatorInput ? (
            <TableContainer component={Paper} sx={{ mt: 2 }}>
              <Table>
                <TableHead>
                  <TableRow sx={{ backgroundColor: 'grey.100' }}>
                    <TableCell sx={{ fontWeight: 600, fontSize: '0.875rem' }}>CSV Column</TableCell>
                    <TableCell sx={{ fontWeight: 600, fontSize: '0.875rem' }}>Input Value</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(selectedCreatorInput).map(([key, value]) => (
                    <TableRow key={key}>
                      <TableCell sx={{ 
                        fontWeight: 500, 
                        backgroundColor: 'grey.50', 
                        fontFamily: 'monospace',
                        fontSize: '0.875rem'
                      }}>
                        {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </TableCell>
                      <TableCell>
                        <TextField 
                          fullWidth 
                          size="small" 
                          value={value || ''} 
                          InputProps={{ readOnly: true }}
                          variant="outlined"
                          sx={{ 
                            '& .MuiInputBase-input': { 
                              backgroundColor: 'grey.50',
                              cursor: 'default',
                              fontFamily: 'monospace',
                              fontSize: '0.875rem'
                            }
                          }}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="textSecondary">
                No input data available for this creator.
              </Typography>
            </Box>
          )}

          <Box sx={{ mt: 3, p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2, color: 'primary.main' }}>
              📊 Output Values:
            </Typography>
            <Box component="ul" sx={{ pl: 3, my: 0, '& > li': { mb: 1.5 } }}>
              {analysisType === 'forecast' && (
                <li>
                  <Typography variant="h10">
                    1. Predicted Leads:
                  </Typography>
                  <Typography variant="body2" color="textSecondary" component="span" sx={{ ml: 1 }}>
                    qualified_leads × fit_score × random_factor(0.9-1.1)
                  </Typography>
                </li>
              )}
              <li>
                <Typography variant="h10">
                  {analysisType === 'forecast' ? '2. Confidence:' : '1. Confidence:'}
                </Typography> 
                <Typography variant="body2" color="textSecondary" component="span" sx={{ ml: 1 }}>
                  Calculates relation between user engagement (clicks), posting stability and semantic fit
                </Typography>
              </li>
              <li>
                <Typography variant="h10">
                  {analysisType === 'forecast' ? '3. Tier:' : '2. Tier:'}
                </Typography> 
                <Typography variant="body2" color="textSecondary" component="span" sx={{ ml: 1 }}>
                  Based on views_90d: ≥100k=Established, ≥25k=Growing, &lt;25k=Emerging
                </Typography>
              </li>
              <li>
                <Typography variant="h10">
                  {analysisType === 'forecast' ? '4. Recommendation:' : '3. Recommendation:'}
                </Typography> 
                <Typography variant="body2" color="textSecondary" component="span" sx={{ ml: 1 }}>
                  {analysisType === 'forecast' 
                    ? 'BOOK if leads > 100 & confidence > 0.8, else REVIEW if leads > 50, else SKIP'
                    : 'BOOK if confidence > 0.8, else REVIEW if confidence > 0.6, else SKIP'
                  }
                </Typography>
              </li>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInputModalOpen(false)} variant="contained">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default InfluencerHub;
