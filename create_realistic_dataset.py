#!/usr/bin/env python3
"""
Generate a realistic CreatorFit dataset focused on India + English 
that will actually allow the ML model to learn meaningful patterns.

Key improvements:
1. Focus on India geography + English language for better targeting
2. Add realistic variance in views_90d (not all identical)
3. Create meaningful relationships between content fit and performance
4. Ensure proper correlation between features and qualified_leads
"""

import pandas as pd
import numpy as np
import random
from pathlib import Path

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_realistic_creator_data(n_creators=1500):
    """Generate realistic creator campaign data focused on Indian market."""
    
    # Data Science related topics (higher relevance to Odin School)
    data_science_topics = [
        "Data Science", "Machine Learning", "Python", "SQL", "Statistics",
        "AI Tools", "Career Advice", "EdTech", "Programming", "Analytics"
    ]
    
    # Other topics (lower relevance)
    other_topics = [
        "Finance", "Marketing", "Productivity", "Web Dev", "Design", 
        "Gaming", "Cooking", "Travel", "Health", "Fitness", "Crypto"
    ]
    
    # Realistic transcript templates for Data Science content
    ds_transcripts = [
        "Complete Python tutorial for data science beginners with practical examples",
        "Machine learning fundamentals explained with real-world projects",
        "SQL essentials for data analysis - from basics to advanced queries",
        "Statistics for data science - probability, distributions, and hypothesis testing",
        "Career roadmap for aspiring data scientists in 2024",
        "Data visualization masterclass using Python matplotlib and seaborn",
        "Feature engineering techniques for better machine learning models",
        "End-to-end data science project walkthrough from data to deployment",
        "Essential tools every data scientist should know",
        "Breaking into data science without a technical background"
    ]
    
    # Other content transcripts
    other_transcripts = [
        "Personal finance tips for young professionals in India",
        "Digital marketing strategies for small businesses",
        "Productivity hacks for remote workers",
        "Web development trends and best practices",
        "UI/UX design principles for beginners",
        "Gaming industry insights and career opportunities",
        "Healthy cooking recipes for busy professionals",
        "Budget travel guide across India",
        "Fitness routines for desk workers",
        "Cryptocurrency basics and investment strategies"
    ]
    
    category_tags = [
        "tutorial", "tips", "case-study", "how-to", "review", "interview",
        "deep-dive", "beginner-friendly", "advanced", "practical"
    ]
    
    creators = []
    
    for i in range(n_creators):
        creator_id = f"C{i+1}"
        
        # 70% chance of data science related content (higher relevance)
        is_ds_related = np.random.random() < 0.7
        
        if is_ds_related:
            # Data Science creator
            topic = np.random.choice(data_science_topics)
            transcript = np.random.choice(ds_transcripts)
            base_performance = 0.7  # Higher base performance for relevant content
        else:
            # Other topic creator
            topic = np.random.choice(other_topics)
            transcript = np.random.choice(other_transcripts)
            base_performance = 0.3  # Lower base performance for less relevant content
        
        # Add some multi-topic creators (30% chance)
        if np.random.random() < 0.3:
            second_topic = np.random.choice(data_science_topics if not is_ds_related else other_topics)
            topic = f"{topic};{second_topic}"
        
        # Realistic posting cadence (0.5 to 14 days)
        posting_cadence = np.random.uniform(0.5, 14.0)
        
        # Realistic views with variance (1K to 50K, log-normal distribution)
        views_90d = int(np.random.lognormal(mean=8.5, sigma=1.2))  # ~5K median, wide range
        views_90d = max(500, min(100000, views_90d))  # Clip to reasonable range
        
        # Calculate performance metrics based on content relevance and audience size
        
        # Click-through rate influenced by content relevance and views
        ctr_base = base_performance * 0.02  # 0.6-2% CTR range
        ctr_boost = min(0.01, views_90d / 200000)  # Higher views -> slightly better CTR
        ctr = ctr_base + ctr_boost + np.random.normal(0, 0.003)
        ctr = max(0.001, min(0.05, ctr))  # Clip to realistic range
        
        clicks = int(views_90d * ctr)
        
        # Lead conversion rate (2-8% of clicks become leads)
        lead_rate = 0.02 + base_performance * 0.06 + np.random.normal(0, 0.01)
        lead_rate = max(0.01, min(0.12, lead_rate))
        leads = max(1, int(clicks * lead_rate))
        
        # Qualified lead rate (30-70% of leads are qualified)
        qualified_rate = 0.3 + base_performance * 0.4 + np.random.normal(0, 0.1)
        qualified_rate = max(0.1, min(0.9, qualified_rate))
        qualified_leads = max(1, int(leads * qualified_rate))
        
        # Enrollment rate (20-50% of qualified leads enroll)
        enrollment_rate = 0.2 + base_performance * 0.3 + np.random.normal(0, 0.05)
        enrollment_rate = max(0.05, min(0.6, enrollment_rate))
        enrollments = int(qualified_leads * enrollment_rate)
        
        # Refund rate (0-15% of enrollments)
        refund_rate = np.random.uniform(0, 0.15)
        refunds = int(enrollments * refund_rate)
        
        # All creators are in India with English content (fixes geo/lang match)
        geography = "INDIA"
        language = "English"
        
        # Category tags
        num_tags = np.random.choice([1, 2, 3], p=[0.5, 0.3, 0.2])
        selected_tags = np.random.choice(category_tags, size=num_tags, replace=False)
        category_tag = ";".join(selected_tags)
        
        creators.append({
            "creator_id": creator_id,
            "topic": topic,
            "recent_video_transcript": transcript,
            "posting_cadence_days": round(posting_cadence, 1),
            "views_90d": views_90d,
            "clicks": clicks,
            "leads": leads,
            "qualified_leads": qualified_leads,
            "enrollments": enrollments,
            "refunds": refunds,
            "geography": geography,
            "language": language,
            "category_tag": category_tag
        })
    
    return pd.DataFrame(creators)

def main():
    """Generate and save the realistic dataset."""
    print("🔄 Generating realistic CreatorFit dataset...")
    
    # Generate the dataset
    df = generate_realistic_creator_data(n_creators=1500)
    
    # Save to CSV
    output_path = Path("dataset/creator_campaign_audience_realistic.csv")
    output_path.parent.mkdir(exist_ok=True)
    df.to_csv(output_path, index=False)
    
    # Print summary statistics
    print(f"✅ Dataset saved to: {output_path}")
    print(f"📊 Dataset shape: {df.shape}")
    print("\n📈 Target variable (qualified_leads) statistics:")
    print(df['qualified_leads'].describe())
    print(f"\n🎯 Views distribution:")
    print(f"Min: {df['views_90d'].min():,}")
    print(f"Median: {df['views_90d'].median():,}")
    print(f"Max: {df['views_90d'].max():,}")
    print(f"\n🌍 Geography: {df['geography'].unique()}")
    print(f"🗣️ Language: {df['language'].unique()}")
    print(f"\n💡 Data Science related creators: {df['topic'].str.contains('Data Science|Machine Learning|Python|SQL|Statistics|AI Tools|Analytics').sum()}")
    
    # Show correlation between features and target
    numeric_cols = ['posting_cadence_days', 'views_90d', 'clicks', 'leads', 'qualified_leads']
    correlations = df[numeric_cols].corr()['qualified_leads'].sort_values(ascending=False)
    print(f"\n🔗 Correlations with qualified_leads:")
    for col, corr in correlations.items():
        if col != 'qualified_leads':
            print(f"  {col}: {corr:.3f}")

if __name__ == "__main__":
    main()
