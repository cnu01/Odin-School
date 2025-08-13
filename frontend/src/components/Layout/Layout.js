import React, { useState } from 'react';
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Avatar,
  Badge,
  Divider,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Star as StarIcon,
  Forum as ForumIcon,
  TrendingUp as TrendingUpIcon,
  Share as ShareIcon,
  AttachMoney as MoneyIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountIcon,
  ChatBubble as ChatIcon,
  Psychology as PsychologyIcon,
  Analytics as AnalyticsIcon,
  PersonAdd as PersonAddIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const drawerWidth = 260;

const menuItems = [
  {
    text: 'OneTruth Analytics',
    icon: <AnalyticsIcon />,
    path: '/onetruth',
    subtitle: 'Unified Intelligence',
  },
  {
    text: 'Dashboard',
    icon: <DashboardIcon />,
    path: '/dashboard',
    subtitle: 'Overview',
  },
  {
    text: 'Lead Management',
    icon: <PeopleIcon />,
    path: '/leads',
    subtitle: 'Lead Overview',
  },
  {
    text: 'FirstTouch AI',
    icon: <PsychologyIcon />,
    path: '/firsttouch',
    subtitle: 'Call Optimization',
  },
  {
    text: 'HotLead AI',
    icon: <PeopleIcon />,
    path: '/hotlead',
    subtitle: 'ML-Powered Scoring',
  },
  {
    text: 'Conversation Management',
    icon: <ChatIcon />,
    path: '/closemore',
    subtitle: 'CloseMore',
  },
  {
    text: 'Influencer Hub',
    icon: <StarIcon />,
    path: '/influencers',
    subtitle: 'CreatorFit',
  },
  {
    text: 'Brand Reputation',
    icon: <ForumIcon />,
    path: '/reputation',
    subtitle: 'TrustDesk',
  },
  {
    text: 'Ad Performance',
    icon: <TrendingUpIcon />,
    path: '/ads',
    subtitle: 'AdLift',
  },
  {
    text: 'Referral Management',
    icon: <PersonAddIcon />,
    path: '/referrals',
    subtitle: 'ReferMore AI',
  },
  {
    text: 'Pricing Insights',
    icon: <MoneyIcon />,
    path: '/pricing',
    subtitle: 'PriceSense',
  },
];

function Layout({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNavigation = (path) => {
    navigate(path);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
          Odin School
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Analytics Hub
        </Typography>
      </Box>
      
      <Divider />
      
      <List sx={{ flexGrow: 1, px: 1 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              onClick={() => handleNavigation(item.path)}
              selected={location.pathname === item.path}
              sx={{
                borderRadius: 2,
                '&.Mui-selected': {
                  backgroundColor: 'primary.main',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'white',
                  },
                },
              }}
            >
              <ListItemIcon>
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                secondary={item.subtitle}
                primaryTypographyProps={{
                  fontSize: '0.9rem',
                  fontWeight: 600,
                }}
                secondaryTypographyProps={{
                  fontSize: '0.75rem',
                  color: location.pathname === item.path ? 'rgba(255,255,255,0.7)' : 'text.secondary',
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          backgroundColor: 'white',
          color: 'text.primary',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {menuItems.find(item => item.path === location.pathname)?.text || 'Dashboard'}
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton color="inherit">
              <Badge badgeContent={3} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
            <IconButton color="inherit">
              <Avatar sx={{ width: 32, height: 32 }}>
                <AccountIcon />
              </Avatar>
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          backgroundColor: 'background.default',
        }}
      >
        <Toolbar />
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
}

export default Layout;
