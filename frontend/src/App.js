import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';

import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard/Dashboard';
import HotLead from './pages/HotLead/HotLead';
import InfluencerHub from './pages/InfluencerHub';
import BrandReputation from './pages/BrandReputation/BrandReputation';

import PricingInsights from './pages/PricingInsights/PricingInsights';
import CloseMore from './pages/CloseMore/CloseMore';
import OneTruth from './pages/OneTruth';
import ReferralManagement from './pages/ReferralManagement/ReferralManagement';
import FirstTouch from './pages/FirstTouch/FirstTouch';
import AdLift from './pages/AdLift/AdLift';

// Odin School brand theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Professional blue
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#ff9800', // Accent orange
      light: '#ffb74d',
      dark: '#f57c00',
    },
    background: {
      default: '#f8f9fa',
      paper: '#ffffff',
    },
    text: {
      primary: '#212529',
      secondary: '#6c757d',
    },
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: '12px',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/hotlead" element={<HotLead />} />
            <Route path="/influencers" element={<InfluencerHub />} />
            <Route path="/reputation" element={<BrandReputation />} />
            <Route path="/adlift" element={<AdLift />} />
            <Route path="/referrals" element={<ReferralManagement />} />
            <Route path="/pricing" element={<PricingInsights />} />
            <Route path="/firsttouch" element={<FirstTouch />} />
            <Route path="/onetruth" element={<OneTruth />} />
            <Route path="/closemore" element={<CloseMore />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
