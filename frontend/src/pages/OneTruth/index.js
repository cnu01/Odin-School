import React, { useState, useEffect, useCallback } from 'react';
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
  LinearProgress,
  Badge,
  Paper,
  Switch,
  FormControlLabel,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Analytics as AnalyticsIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon
} from '@mui/icons-material';
import onetruthService from '../../services/onetruthService';

const OneTruth = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Dashboard State
  const [dashboardData, setDashboardData] = useState(null);
  const [timeRange, setTimeRange] = useState('7d');
  const [includeAnomalies, setIncludeAnomalies] = useState(true);

  const showError = (message) => {
    setError(message);
    setTimeout(() => setError(null), 5000);
  };

  const showSuccess = (message) => {
    setSuccess(message);
    setTimeout(() => setSuccess(null), 3000);
  };

  // Dashboard Functions
  const loadDashboard = useCallback(async () => {
    const abortController = new AbortController();
    
    try {
      setLoading(true);
      
      // Add delay to prevent rapid duplicate requests
      await new Promise(resolve => setTimeout(resolve, 100));
      
      if (abortController.signal.aborted) return;
      
      const data = await onetruthService.getDashboard(timeRange, includeAnomalies);
      
      if (!abortController.signal.aborted) {
        setDashboardData(data);
      }
    } catch (error) {
      if (!abortController.signal.aborted && error.name !== 'CanceledError') {
        showError(error.message);
      }
    } finally {
      if (!abortController.signal.aborted) {
        setLoading(false);
      }
    }
    
    return () => {
      abortController.abort();
    };
  }, [timeRange, includeAnomalies]);

  // Load dashboard data on component mount with debounce
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      loadDashboard();
    }, 200); // Debounce filter changes
    
    return () => {
      clearTimeout(timeoutId);
    };
  }, [loadDashboard]);

  const getHealthColor = (score) => {
    if (score >= 85) return 'success';
    if (score >= 75) return 'info';
    if (score >= 65) return 'warning';
    return 'error';
  };

  const renderDashboard = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Unified Business Analytics Dashboard</Typography>
        <Box display="flex" gap={2} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <MenuItem value="7d">7 Days</MenuItem>
              <MenuItem value="30d">30 Days</MenuItem>
              <MenuItem value="90d">90 Days</MenuItem>
            </Select>
          </FormControl>
          <FormControlLabel
            control={
              <Switch
                checked={includeAnomalies}
                onChange={(e) => setIncludeAnomalies(e.target.checked)}
              />
            }
            label="Include Anomalies"
          />
          <Button variant="outlined" onClick={loadDashboard} disabled={loading}>
            Refresh
          </Button>
        </Box>
      </Box>

      {dashboardData && (
        <Grid container spacing={3}>
          {/* Business Health Score */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <SpeedIcon sx={{ mr: 1 }} />
                  <Typography variant="h6">Business Health Score</Typography>
                </Box>
                {dashboardData.business_health && (
                  <Box>
                    <Box display="flex" alignItems="center" mb={2}>
                      <Typography variant="h3" color={getHealthColor(dashboardData.business_health.overall_health_score)}>
                        {dashboardData.business_health.overall_health_score}%
                      </Typography>
                      <Chip 
                        label={dashboardData.business_health.health_grade}
                        color={getHealthColor(dashboardData.business_health.overall_health_score)}
                        sx={{ ml: 2 }}
                      />
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={dashboardData.business_health.overall_health_score} 
                      color={getHealthColor(dashboardData.business_health.overall_health_score)}
                      sx={{ mb: 2 }}
                    />
                    <Typography variant="body2" color="text.secondary">
                      Component Scores:
                    </Typography>
                    {Object.entries(dashboardData.business_health.component_scores || {}).map(([key, value]) => (
                      <Box key={key} display="flex" justifyContent="space-between" mt={1}>
                        <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                          {key.replace('_', ' ')}:
                        </Typography>
                        <Typography variant="body2" fontWeight="bold">
                          {value}%
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Key Performance Indicators */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <AnalyticsIcon sx={{ mr: 1 }} />
                  <Typography variant="h6">Key Performance Indicators</Typography>
                </Box>
                {dashboardData.key_metrics && (
                  <Grid container spacing={2}>
                    {Object.entries(dashboardData.key_metrics).map(([key, value]) => (
                      <Grid item xs={12} sm={6} key={key}>
                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="body2" color="text.secondary" sx={{ textTransform: 'capitalize' }}>
                            {key.replace(/_/g, ' ')}
                          </Typography>
                          <Typography variant="h6" fontWeight="bold">
                            {value}
                          </Typography>
                        </Paper>
                      </Grid>
                    ))}
                  </Grid>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Performance Trends */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <TrendingUpIcon sx={{ mr: 1 }} />
                  <Typography variant="h6">Performance Trends</Typography>
                </Box>
                {dashboardData.trends && (
                  <List>
                    {Object.entries(dashboardData.trends).map(([key, value]) => (
                      <ListItem key={key}>
                        <ListItemIcon>
                          {value > 0 ? (
                            <TrendingUpIcon color="success" />
                          ) : (
                            <TrendingDownIcon color="error" />
                          )}
                        </ListItemIcon>
                        <ListItemText
                          primary={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          secondary={`${value > 0 ? '+' : ''}${(value * 100).toFixed(1)}%`}
                        />
                      </ListItem>
                    ))}
                  </List>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Anomaly Summary */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <WarningIcon sx={{ mr: 1 }} />
                  <Typography variant="h6">Anomaly Detection</Typography>
                </Box>
                {dashboardData.anomalies && (
                  <Box>
                    <Box display="flex" alignItems="center" mb={2}>
                      <Badge badgeContent={dashboardData.anomalies.total_anomalies} color="error">
                        <WarningIcon />
                      </Badge>
                      <Typography variant="h4" sx={{ ml: 2 }}>
                        {dashboardData.anomalies.total_anomalies}
                      </Typography>
                      <Typography variant="body1" sx={{ ml: 1 }}>
                        anomalies detected
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Average Anomaly Score: {(dashboardData.anomalies.avg_anomaly_score || 0).toFixed(3)}
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Data Quality */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <SecurityIcon sx={{ mr: 1 }} />
                  <Typography variant="h6">Data Quality Metrics</Typography>
                </Box>
                {dashboardData.data_quality && (
                  <Grid container spacing={3}>
                    {Object.entries(dashboardData.data_quality).map(([key, value]) => (
                      <Grid item xs={12} sm={6} md={3} key={key}>
                        <Paper sx={{ p: 2, textAlign: 'center' }}>
                          <Typography variant="body2" color="text.secondary" sx={{ textTransform: 'capitalize' }}>
                            {key}
                          </Typography>
                          <Typography variant="h5" fontWeight="bold" color="primary">
                            {value}
                          </Typography>
                        </Paper>
                      </Grid>
                    ))}
                  </Grid>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );









  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" alignItems="center" mb={3}>
        <DashboardIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
        <Box>
          <Typography variant="h4" component="h1" fontWeight="bold">
            OneTruth Analytics
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Unified Marketing Intelligence with AI-Powered Anomaly Detection
          </Typography>
        </Box>
      </Box>

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



      {loading && (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      )}

      {!loading && renderDashboard()}
    </Box>
  );
};

export default OneTruth;
