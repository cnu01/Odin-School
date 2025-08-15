#!/usr/bin/env python3
"""
Enhanced Lead Data Generator for HotLead AI Solutions
Creates 5000 realistic leads with comprehensive features for advanced ML training
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

# Set random seeds for reproducibility
np.random.seed(42)
random.seed(42)

class EnhancedLeadGenerator:
    def __init__(self):
        self.sources = {
            'organic': {'weight': 0.35, 'conversion_rate': 0.26, 'avg_pageviews': 6},
            'referral': {'weight': 0.15, 'conversion_rate': 0.38, 'avg_pageviews': 8},
            'paid': {'weight': 0.25, 'conversion_rate': 0.18, 'avg_pageviews': 4},
            'social_organic': {'weight': 0.15, 'conversion_rate': 0.08, 'avg_pageviews': 3},
            'email': {'weight': 0.08, 'conversion_rate': 0.22, 'avg_pageviews': 5},
            'direct': {'weight': 0.02, 'conversion_rate': 0.45, 'avg_pageviews': 9}
        }
        
        self.utm_campaigns = {
            'organic': ['data-science-bootcamp', 'ai-career-change', 'investment-banking', 'analytics-program'],
            'referral': ['employee-referral', 'partner-program', 'alumni-network', 'corporate-partnership'],
            'paid': ['data-analytics-campaign', 'career-boost-ads', 'finance-professionals', 'tech-upskill'],
            'social_organic': ['career-change', 'tech-skills', 'finance-bootcamp', 'data-science-journey'],
            'email': ['newsletter-signup', 'course-launch', 'webinar-followup', 'career-guide'],
            'direct': ['brand-search', 'repeat-visitor', 'bookmark-return', 'word-of-mouth']
        }
        
        self.cities = {
            'Bangalore': {'weight': 0.25, 'conversion_boost': 1.2},
            'Mumbai': {'weight': 0.20, 'conversion_boost': 1.1},
            'Delhi': {'weight': 0.18, 'conversion_boost': 1.0},
            'Hyderabad': {'weight': 0.12, 'conversion_boost': 1.15},
            'Chennai': {'weight': 0.10, 'conversion_boost': 1.05},
            'Pune': {'weight': 0.08, 'conversion_boost': 1.1},
            'Kolkata': {'weight': 0.05, 'conversion_boost': 0.9},
            'Ahmedabad': {'weight': 0.02, 'conversion_boost': 0.95}
        }
        
        self.devices = {
            'desktop': {'weight': 0.55, 'conversion_boost': 1.3},
            'mobile': {'weight': 0.40, 'conversion_boost': 0.8},
            'tablet': {'weight': 0.05, 'conversion_boost': 1.0}
        }
        
        self.sales_reps = {
            'alice': {'experience': 'senior', 'conversion_rate': 0.42},
            'bob': {'experience': 'junior', 'conversion_rate': 0.28},
            'charlie': {'experience': 'medium', 'conversion_rate': 0.35},
            'diana': {'experience': 'senior', 'conversion_rate': 0.40},
            'ethan': {'experience': 'medium', 'conversion_rate': 0.32}
        }
        
        self.courses = [
            'data-science', 'ai-bootcamp', 'investment-banking', 'analytics',
            'finance', 'machine-learning', 'business-analytics', 'fintech'
        ]
        
        self.referrer_domains = [
            'google.com', 'linkedin.com', 'facebook.com', 'twitter.com',
            'youtube.com', 'medium.com', 'quora.com', 'stackoverflow.com'
        ]
        
        self.landing_pages = [
            '/', '/courses/data-science', '/courses/ai-bootcamp', '/courses/analytics',
            '/courses/finance', '/about', '/pricing', '/demo', '/blog'
        ]
        
        self.lost_reasons = [
            'price', 'timing', 'competition', 'unqualified', 'no_response', 'location'
        ]
        
        self.objection_types = [
            'cost_objection', 'time_constraint', 'experience_mismatch', 
            'location_issue', 'course_content', 'not_ready'
        ]
        
        # Indian names database
        self.first_names = [
            'Arjun', 'Priya', 'Rohit', 'Anita', 'Vikram', 'Sneha', 'Amit', 'Kavya',
            'Rajesh', 'Meera', 'Suresh', 'Divya', 'Kiran', 'Pooja', 'Anil', 'Renu',
            'Manoj', 'Sunita', 'Deepak', 'Nisha', 'Ravi', 'Geeta', 'Sanjay', 'Rekha',
            'Ashwin', 'Lakshmi', 'Naveen', 'Shanti', 'Prakash', 'Usha', 'Ramesh', 'Lata'
        ]
        
        self.last_names = [
            'Sharma', 'Patel', 'Kumar', 'Singh', 'Reddy', 'Gupta', 'Agarwal', 'Rao',
            'Iyer', 'Nair', 'Joshi', 'Mehta', 'Shah', 'Verma', 'Malhotra', 'Chopra',
            'Bansal', 'Jain', 'Srinivasan', 'Krishnan', 'Pillai', 'Menon', 'Bhat', 'Desai'
        ]

    def generate_lead(self, lead_id: int) -> Dict[str, Any]:
        """Generate a single realistic lead with all features"""
        
        # Basic info
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        name = f"{first_name} {last_name}"
        email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'])}"
        phone = f"+91-{random.randint(6000000000, 9999999999)}"
        
        # Source selection with realistic distribution
        source = np.random.choice(
            list(self.sources.keys()),
            p=[self.sources[s]['weight'] for s in self.sources.keys()]
        )
        
        # UTM parameters based on source
        utm_source = {
            'organic': 'google',
            'referral': 'linkedin', 
            'paid': 'google_ads',
            'social_organic': 'facebook',
            'email': 'newsletter',
            'direct': 'direct'
        }[source]
        
        utm_medium = {
            'organic': 'organic',
            'referral': 'referral',
            'paid': 'cpc',
            'social_organic': 'social', 
            'email': 'email',
            'direct': 'direct'
        }[source]
        
        utm_campaign = random.choice(self.utm_campaigns[source])
        
        # Geographic selection
        geography = np.random.choice(
            list(self.cities.keys()),
            p=[self.cities[c]['weight'] for c in self.cities.keys()]
        )
        
        # Device selection
        device = np.random.choice(
            list(self.devices.keys()),
            p=[self.devices[d]['weight'] for d in self.devices.keys()]
        )
        
        # Behavioral features with correlation to conversion
        base_pageviews = self.sources[source]['avg_pageviews']
        page_views = max(1, int(np.random.normal(base_pageviews, 2)))
        
        # Time on site correlated with page views
        time_on_site = max(30, int(page_views * np.random.normal(60, 20)))
        
        # Course pages viewed (subset of total page views)
        course_pages_viewed = min(page_views, max(0, int(np.random.normal(page_views * 0.4, 1))))
        
        # Demo requests (higher for high-intent leads)
        demo_request_probability = 0.05 + (page_views * 0.02) + (course_pages_viewed * 0.03)
        demo_requests = 1 if random.random() < demo_request_probability else 0
        
        # Contact timing (business hours bias)
        contact_hour = int(np.random.choice(range(9, 19), p=[0.05, 0.08, 0.12, 0.15, 0.15, 0.15, 0.12, 0.08, 0.05, 0.05]))
        contact_day = random.randint(1, 7)  # 1=Monday, 7=Sunday
        
        # Session behavior
        session_count = max(1, int(np.random.exponential(2)))
        days_since_first_visit = max(0, int(np.random.exponential(5)))
        
        # Form submissions
        form_submission_prob = 0.3 + (demo_requests * 0.4)
        form_submissions = max(1, int(np.random.normal(1.5, 0.5))) if random.random() < form_submission_prob else 1
        
        # Technical details
        referrer_domain = random.choice(self.referrer_domains)
        landing_page = random.choice(self.landing_pages)
        scroll_depth = max(10, min(100, int(np.random.normal(60, 20))))
        
        # Engagement metrics (mostly 0 for new leads)
        email_opens = random.randint(0, 2) if source == 'email' else 0
        email_clicks = min(email_opens, random.randint(0, 1))
        webinar_attendance = 1 if random.random() < 0.1 else 0
        social_engagement = random.randint(0, 5) if source == 'social_organic' else 0
        
        # Sales rep assignment
        rep_name = random.choice(list(self.sales_reps.keys()))
        rep_experience = self.sales_reps[rep_name]['experience']
        
        # Calculate conversion probability based on multiple factors
        base_conversion = self.sources[source]['conversion_rate']
        
        # Apply various multipliers
        city_multiplier = self.cities[geography]['conversion_boost']
        device_multiplier = self.devices[device]['conversion_boost']
        
        # Behavioral multipliers
        pageview_multiplier = 1 + (page_views - base_pageviews) * 0.05
        demo_multiplier = 1.8 if demo_requests > 0 else 1.0
        timing_multiplier = 1.2 if 9 <= contact_hour <= 17 and 1 <= contact_day <= 5 else 0.8
        rep_multiplier = self.sales_reps[rep_name]['conversion_rate'] / 0.35  # Normalize to average
        
        # Final conversion probability
        conversion_prob = (base_conversion * city_multiplier * device_multiplier * 
                          pageview_multiplier * demo_multiplier * timing_multiplier * rep_multiplier)
        conversion_prob = min(0.95, max(0.02, conversion_prob))  # Cap between 2% and 95%
        
        # Determine if lead converts
        enrolled = random.random() < conversion_prob
        
        # Sales process outcomes
        contacted = random.random() < 0.85  # 85% of leads get contacted
        
        if contacted:
            # Response time based on priority (high conversion prob = faster response)
            if conversion_prob > 0.7:
                response_time_hours = max(0.5, np.random.exponential(2))
            elif conversion_prob > 0.4:
                response_time_hours = max(1.0, np.random.exponential(6))
            else:
                response_time_hours = max(2.0, np.random.exponential(24))
            
            contact_attempts = max(1, int(np.random.normal(2, 1)))
            
            # Meeting scheduled if contacted and some probability
            meeting_prob = conversion_prob * 0.8  # 80% of conversion prob
            meeting_scheduled = contacted and (random.random() < meeting_prob)
        else:
            response_time_hours = 0
            contact_attempts = 0
            meeting_scheduled = False
        
        # Revenue (only if enrolled)
        if enrolled:
            revenue = random.choice([35000, 45000, 55000, 65000])  # Course prices
        else:
            revenue = 0
        
        # Lost reason and objections (only if not enrolled)
        if not enrolled and contacted:
            lost_reason = random.choice(self.lost_reasons)
            objection_type = random.choice(self.objection_types)
        else:
            lost_reason = ""
            objection_type = ""
        
        return {
            'lead_id': f"LEAD_20250814_{lead_id:06d}",
            'name': name,
            'email': email,
            'phone': phone,
            'source': source,
            'utm_source': utm_source,
            'utm_medium': utm_medium,
            'utm_campaign': utm_campaign,
            'page_views': page_views,
            'time_on_site': time_on_site,
            'course_pages_viewed': course_pages_viewed,
            'demo_requests': demo_requests,
            'contact_hour': contact_hour,
            'contact_day': contact_day,
            'geography': geography,
            'device': device,
            'session_count': session_count,
            'days_since_first_visit': days_since_first_visit,
            'form_submissions': form_submissions,
            'referrer_domain': referrer_domain,
            'landing_page': landing_page,
            'scroll_depth': scroll_depth,
            'email_opens': email_opens,
            'email_clicks': email_clicks,
            'webinar_attendance': webinar_attendance,
            'social_engagement': social_engagement,
            'rep_assigned': rep_name,
            'rep_experience_level': rep_experience,
            'response_time_hours': round(response_time_hours, 1),
            'contact_attempts': contact_attempts,
            'enrolled': enrolled,
            'contacted': contacted,
            'meeting_scheduled': meeting_scheduled,
            'revenue': revenue,
            'lost_reason': lost_reason,
            'objection_type': objection_type
        }

    def generate_dataset(self, num_leads: int = 5000) -> pd.DataFrame:
        """Generate complete dataset of realistic leads"""
        
        print(f"Generating {num_leads} realistic leads...")
        
        leads = []
        for i in range(1, num_leads + 1):
            if i % 500 == 0:
                print(f"Generated {i} leads...")
            
            lead = self.generate_lead(i)
            leads.append(lead)
        
        df = pd.DataFrame(leads)
        
        # Print statistics
        print("\n=== Dataset Statistics ===")
        print(f"Total leads: {len(df)}")
        print(f"Conversion rate: {df['enrolled'].mean():.1%}")
        print(f"Contact rate: {df['contacted'].mean():.1%}")
        print(f"Meeting rate: {df['meeting_scheduled'].mean():.1%}")
        
        print("\nSource distribution:")
        print(df['source'].value_counts())
        
        print("\nConversion by source:")
        conversion_by_source = df.groupby('source')['enrolled'].agg(['count', 'mean'])
        conversion_by_source['conversion_rate'] = (conversion_by_source['mean'] * 100).round(1)
        print(conversion_by_source[['count', 'conversion_rate']])
        
        print("\nGeography distribution:")
        print(df['geography'].value_counts().head())
        
        print("\nRevenue statistics:")
        print(f"Total revenue: ₹{df['revenue'].sum():,}")
        print(f"Average deal size: ₹{df[df['revenue'] > 0]['revenue'].mean():,.0f}")
        
        return df

def main():
    """Generate the enhanced lead dataset"""
    generator = EnhancedLeadGenerator()
    
    # Generate 5000 leads
    df = generator.generate_dataset(5000)
    
    # Save to CSV
    output_file = "/Users/batman/Movies/odinschool/Odin-School/backend/data/enhanced_leads_5000.csv"
    df.to_csv(output_file, index=False)
    print(f"\n✅ Dataset saved to: {output_file}")
    
    # Save metadata
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "total_leads": len(df),
        "conversion_rate": f"{df['enrolled'].mean():.1%}",
        "features": list(df.columns),
        "target_variable": "enrolled",
        "sources": list(df['source'].unique()),
        "cities": list(df['geography'].unique()),
        "description": "Enhanced realistic lead dataset for HotLead AI solutions training"
    }
    
    metadata_file = "/Users/batman/Movies/odinschool/Odin-School/backend/data/enhanced_leads_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Metadata saved to: {metadata_file}")
    print("\n🚀 Ready for ML training with enhanced features!")

if __name__ == "__main__":
    main()
