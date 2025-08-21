# APEX AI Analytics Hub

A comprehensive EdTech analytics and management platform built with React and Material-UI. This frontend application provides unified analytics, lead management, influencer analysis, brand reputation management, and pricing optimization tools.

## Features

### 🎯 OneTruth - Unified Analytics Dashboard
- Single source of truth for marketing analytics
- KPI scorecards with real-time metrics
- AI-generated executive briefs with anomaly detection
- Lead-to-enrollment funnel visualization
- Performance trends and source breakdowns

### 🔥 HotLead - AI-Powered Lead Management
- AI scoring system for lead prioritization (1-10 scale)
- Lead queue with filterable views
- Detailed lead profiles with activity timelines
- Next-best-action AI suggestions
- First Touch BOT integration and status tracking

### 🤖 FirstTouch BOT - AI Sales Automation
- Automated first-touch outbound calls within 15 minutes
- AI-powered conversation handling and lead qualification
- Smart booking system for counselor appointments
- Retry logic and scheduling optimization
- Integrated within HotLead management system

### 💬 CloseMore - Conversation Management
- AI-powered conversation summarization (calls, WhatsApp, email)
- Next-best-action recommendations per sales rep
- Smart nudges to reduce no-shows and improve follow-ups
- Objection handling and intent classification
- Win probability tracking and pipeline management

### ⭐ CreatorFit - Influencer Analysis Hub
- Creator database with profile management
- AI-powered fit scoring for brand alignment
- Performance forecasting and ROI predictions
- Audience insights and demographic analysis
- Campaign planning and budget optimization

### 🛡️ TrustDesk - Brand Reputation Management
- Unified inbox for social media comments/reviews
- AI-powered triage system (Urgent/Negative/Questions/Positive)
- Smart reply generator with brand voice alignment
- Sentiment analysis and response time tracking
- Multi-platform integration (YouTube, Instagram, Facebook, Twitter)

### 📈 AdLift - Ad Performance Optimization & ReferMore
- Creative performance tracking with fatigue detection
- AI-powered ad variant generator
- Campaign management with ROI analysis
- A/B testing insights and recommendations
- Likely referrer identification based on engagement
- Personalized referral message generation
- Multi-channel referral tracking
- Reward management and ROI analysis

### 💰 PriceSense - Dynamic Pricing Optimization
- AI-driven pricing recommendations
- Market demand analysis and competitor benchmarking
- Price elasticity modeling
- Interactive price simulation tools
- Revenue optimization scenarios

## Tech Stack

- **Frontend Framework**: React 18
- **UI Library**: Material-UI (MUI) v5
- **Routing**: React Router v6
- **Charts**: Recharts
- **Data Grid**: MUI X Data Grid
- **Icons**: Material-UI Icons
- **HTTP Client**: Axios
- **Date Handling**: date-fns

## Design Philosophy

- **Clean & Modern**: Professional interface with consistent spacing and typography
- **Data-Driven**: Emphasis on clear data visualization and actionable insights
- **AI-First**: Integration of AI suggestions and automation throughout
- **Responsive**: Fully responsive design for desktop, tablet, and mobile
- **Modular**: Component-based architecture for easy maintenance and scaling

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd apex-ai-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Build for production**
   ```bash
   npm run build
   ```

## Project Structure

```
src/
├── components/
│   └── Layout/
│       └── Layout.js          # Main navigation and layout
├── pages/
│   ├── Dashboard/
│   │   └── Dashboard.js       # OneTruth unified analytics dashboard
│   ├── LeadManagement/
│   │   └── LeadManagement.js  # HotLead AI scoring & FirstTouch BOT
│   ├── CloseMore/
│   │   └── CloseMore.js       # CloseMore conversation management
│   ├── InfluencerHub/
│   │   └── InfluencerHub.js   # CreatorFit influencer analysis
│   ├── BrandReputation/
│   │   └── BrandReputation.js # TrustDesk reputation management
│   ├── AdPerformance/
│   │   └── AdPerformance.js   # AdLift optimization & ReferMore
│   ├── ReferralManagement/
│   │   └── ReferralManagement.js # Redirect to AdPerformance
│   └── PricingInsights/
│       └── PricingInsights.js # PriceSense dynamic pricing
├── App.js                     # Main app component with routing
└── index.js                   # React app entry point
```

## Key Components

### Navigation
- Collapsible sidebar with module-based organization
- Mobile-responsive drawer navigation
- Active route highlighting
- Notification and profile management

### Dashboard Cards
- Reusable KPI cards with trend indicators
- Interactive charts and visualizations
- Real-time data updates
- Responsive grid layouts

### Data Tables
- Sortable and filterable data grids
- Action buttons for quick operations
- Pagination and search functionality
- Export capabilities

### AI Integration
- Smart suggestions and recommendations
- Automated content generation
- Anomaly detection and alerts
- Predictive analytics displays

## Customization

### Theme
The application uses a custom Material-UI theme with APEX AI branding:
- Primary color: Professional blue (#1976d2)
- Secondary color: Accent orange (#ff9800)
- Clean typography with Inter font family
- Consistent card styling and shadows

### Adding New Modules
1. Create new page component in `src/pages/`
2. Add route to `App.js`
3. Update navigation menu in `Layout.js`
4. Follow existing patterns for consistency

## API Integration

Currently uses mock data for demonstration. To integrate with real APIs:

1. Replace mock data objects with API calls using Axios
2. Add proper error handling and loading states
3. Implement authentication and authorization
4. Add data caching and state management (Redux/Context)

## Future Enhancements

- Real-time data synchronization with WebSockets
- Advanced filtering and search capabilities
- Export functionality for reports and analytics
- Mobile app version with React Native
- Advanced AI features and machine learning models
- Integration with popular EdTech and marketing tools

## Contributing

1. Follow React and Material-UI best practices
2. Maintain consistent code formatting
3. Add proper error handling and loading states
4. Write comprehensive component documentation
5. Test responsive design across devices

## License

This project is proprietary software for APEX AI.

---

**Note**: This is a frontend-only application with mock data for demonstration purposes. Backend integration and real data connections would be required for production use.
