#!/usr/bin/env python3
"""
Generate EdTech-focused CreatorFit dataset
Focused on educational platform with realistic Indian creator ecosystem
"""

import pandas as pd
import numpy as np
import random
from pathlib import Path

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_edtech_creator_data(n_creators=1500):
    """Generate realistic EdTech creator campaign data."""
    
    # PURE EDTECH TOPICS - No gaming/entertainment
    edtech_topics = [
        "Python", "Data Science", "Machine Learning", "Frontend Development",
        "Backend Development", "JavaScript", "React", "Node.js", "SQL",
        "Statistics", "Deep Learning", "Web Development", "Mobile Development",
        "DevOps", "Cloud Computing", "Artificial Intelligence", "Analytics",
        "Database Management", "Software Engineering", "Programming Fundamentals",
        "Java", "C++", "Django", "Flask", "MongoDB", "PostgreSQL",
        "Career Guidance", "Interview Preparation", "Coding Practice",
        "System Design", "Algorithms", "Data Structures"
    ]
    
    # Topic-to-transcript mapping for consistent data
    topic_transcript_mapping = {
        "Python": [
            "Complete Python programming masterclass: from basics to advanced projects including web scraping and automation",
            "Data analysis with Python: exploratory data analysis, visualization with matplotlib and seaborn",
            "Machine learning algorithms deep dive: linear regression to neural networks with Python implementation"
        ],
        "Data Science": [
            "Data Science career roadmap 2024: statistics, pandas, machine learning, and real industry projects",
            "Machine learning algorithms deep dive: linear regression to neural networks with Python implementation",
            "Data analysis with Python: exploratory data analysis, visualization with matplotlib and seaborn"
        ],
        "Machine Learning": [
            "Machine learning algorithms deep dive: linear regression to neural networks with Python implementation",
            "Deep learning with PyTorch and TensorFlow: computer vision and NLP projects from scratch",
            "Data Science career roadmap 2024: statistics, pandas, machine learning, and real industry projects"
        ],
        "JavaScript": [
            "JavaScript complete guide: ES6+, async programming, DOM manipulation, and modern frameworks",
            "Frontend development with React and Redux: building scalable web applications with modern practices",
            "Full-stack development bootcamp: MERN stack with authentication and deployment strategies"
        ],
        "React": [
            "Frontend development with React and Redux: building scalable web applications with modern practices",
            "React Native mobile development: cross-platform apps with navigation and state management",
            "Full-stack development bootcamp: MERN stack with authentication and deployment strategies"
        ],
        "Node.js": [
            "Backend development masterclass: Node.js, Express, MongoDB, and RESTful API design patterns",
            "Full-stack development bootcamp: MERN stack with authentication and deployment strategies",
            "JavaScript complete guide: ES6+, async programming, DOM manipulation, and modern frameworks"
        ],
        "SQL": [
            "SQL for data analysis: advanced queries, window functions, and database optimization techniques",
            "Database design fundamentals: normalization, indexing, and performance optimization strategies",
            "Data Science career roadmap 2024: statistics, pandas, machine learning, and real industry projects"
        ],
        "Frontend Development": [
            "Frontend development with React and Redux: building scalable web applications with modern practices",
            "JavaScript complete guide: ES6+, async programming, DOM manipulation, and modern frameworks",
            "Web development portfolio: 10 projects to showcase your skills and impress employers"
        ],
        "Backend Development": [
            "Backend development masterclass: Node.js, Express, MongoDB, and RESTful API design patterns",
            "Database design fundamentals: normalization, indexing, and performance optimization strategies",
            "System design interview masterclass: scalability patterns and distributed systems architecture"
        ],
        "Web Development": [
            "Full-stack development bootcamp: MERN stack with authentication and deployment strategies",
            "Frontend development with React and Redux: building scalable web applications with modern practices",
            "Web development portfolio: 10 projects to showcase your skills and impress employers"
        ],
        "Mobile Development": [
            "React Native mobile development: cross-platform apps with navigation and state management",
            "Frontend development with React and Redux: building scalable web applications with modern practices",
            "Full-stack development bootcamp: MERN stack with authentication and deployment strategies"
        ],
        "DevOps": [
            "DevOps engineering essentials: Docker containers, Kubernetes orchestration, and CI/CD automation",
            "AWS cloud computing: EC2, S3, Lambda, and serverless architecture implementation guide",
            "System design interview masterclass: scalability patterns and distributed systems architecture"
        ],
        "Cloud Computing": [
            "AWS cloud computing: EC2, S3, Lambda, and serverless architecture implementation guide",
            "DevOps engineering essentials: Docker containers, Kubernetes orchestration, and CI/CD automation",
            "System design interview masterclass: scalability patterns and distributed systems architecture"
        ],
        "Artificial Intelligence": [
            "Deep learning with PyTorch and TensorFlow: computer vision and NLP projects from scratch",
            "Machine learning algorithms deep dive: linear regression to neural networks with Python implementation",
            "Data Science career roadmap 2024: statistics, pandas, machine learning, and real industry projects"
        ],
        "Deep Learning": [
            "Deep learning with PyTorch and TensorFlow: computer vision and NLP projects from scratch",
            "Machine learning algorithms deep dive: linear regression to neural networks with Python implementation",
            "Data Science career roadmap 2024: statistics, pandas, machine learning, and real industry projects"
        ],
        "Analytics": [
            "Data analysis with Python: exploratory data analysis, visualization with matplotlib and seaborn",
            "SQL for data analysis: advanced queries, window functions, and database optimization techniques",
            "Data Science career roadmap 2024: statistics, pandas, machine learning, and real industry projects"
        ],
        "Database": [
            "Database design fundamentals: normalization, indexing, and performance optimization strategies",
            "SQL for data analysis: advanced queries, window functions, and database optimization techniques",
            "Backend development masterclass: Node.js, Express, MongoDB, and RESTful API design patterns"
        ],
        "Career Guidance": [
            "Career transition to tech: portfolio building, networking, and landing your first developer job",
            "Coding interview bootcamp: problem-solving techniques and whiteboard coding strategies",
            "Web development portfolio: 10 projects to showcase your skills and impress employers"
        ],
        "Interview Preparation": [
            "Coding interview bootcamp: problem-solving techniques and whiteboard coding strategies",
            "Data structures and algorithms: coding interview preparation with 200+ practice problems",
            "System design interview masterclass: scalability patterns and distributed systems architecture"
        ],
        "System Design": [
            "System design interview masterclass: scalability patterns and distributed systems architecture",
            "Database design fundamentals: normalization, indexing, and performance optimization strategies",
            "DevOps engineering essentials: Docker containers, Kubernetes orchestration, and CI/CD automation"
        ],
        "Algorithms": [
            "Data structures and algorithms: coding interview preparation with 200+ practice problems",
            "Coding interview bootcamp: problem-solving techniques and whiteboard coding strategies",
            "Machine learning algorithms deep dive: linear regression to neural networks with Python implementation"
        ],
        "Software Engineering": [
            "Software engineering best practices: clean code, testing, and agile development methodologies",
            "System design interview masterclass: scalability patterns and distributed systems architecture",
            "Full-stack development bootcamp: MERN stack with authentication and deployment strategies"
        ],
        "Java": [
            "Software engineering best practices: clean code, testing, and agile development methodologies",
            "Data structures and algorithms: coding interview preparation with 200+ practice problems",
            "System design interview masterclass: scalability patterns and distributed systems architecture"
        ],
        "Flask": [
            "Backend development masterclass: Node.js, Express, MongoDB, and RESTful API design patterns",
            "Complete Python programming masterclass: from basics to advanced projects including web scraping and automation",
            "Full-stack development bootcamp: MERN stack with authentication and deployment strategies"
        ]
    }
    
    # Indian languages for EdTech platform
    languages = ["English", "Hindi", "Telugu"]
    language_weights = [0.5, 0.3, 0.2]  # English dominant, Hindi/Telugu significant
    
    # Educational content categories
    category_tags = [
        "tutorial", "beginner-friendly", "advanced", "project-based",
        "interview-prep", "career-guidance", "hands-on", "theory",
        "practical", "step-by-step", "comprehensive", "quick-start"
    ]
    
    creators = []
    
    for i in range(n_creators):
        creator_id = f"EDU_{i+1:04d}"
        
        # Select primary topic
        primary_topic = np.random.choice(edtech_topics)
        
        # 40% chance of multi-topic creators (more specialized)
        if np.random.random() < 0.4:
            secondary_topic = np.random.choice([t for t in edtech_topics if t != primary_topic])
            topic = f"{primary_topic};{secondary_topic}"
        else:
            topic = primary_topic
        
        # Select appropriate transcript based on primary topic
        def get_relevant_transcript(topic_string):
            # Extract primary topic (before semicolon if multi-topic)
            primary = topic_string.split(';')[0]
            
            # Get relevant transcripts for this topic
            if primary in topic_transcript_mapping:
                return np.random.choice(topic_transcript_mapping[primary])
            else:
                # Fallback: use a general tech transcript
                fallback_transcripts = [
                    "Software engineering best practices: clean code, testing, and agile development methodologies",
                    "Career transition to tech: portfolio building, networking, and landing your first developer job",
                    "Web development portfolio: 10 projects to showcase your skills and impress employers"
                ]
                return np.random.choice(fallback_transcripts)
        
        transcript = get_relevant_transcript(topic)
        
        # Posting cadence - PURE INTEGERS (days between posts)
        posting_cadence = np.random.choice([1, 2, 3, 4, 5, 6, 7, 10, 14], 
                                         p=[0.1, 0.2, 0.25, 0.2, 0.15, 0.05, 0.03, 0.015, 0.005])
        
        # Realistic view distribution for REPUTED EdTech company (Odin School scale)
        # Mix of established creators (lakhs) and growing creators (thousands)
        creator_tier = np.random.choice(['established', 'growing', 'emerging'], 
                                      p=[0.2, 0.5, 0.3])
        
        if creator_tier == 'established':
            # Top creators: 1L to 10L+ views
            views_90d = int(np.random.lognormal(mean=11.5, sigma=0.8))  # ~100K median
            views_90d = max(50000, min(2000000, views_90d))
        elif creator_tier == 'growing':
            # Mid-tier creators: 10K to 1L views  
            views_90d = int(np.random.lognormal(mean=10.5, sigma=0.7))  # ~35K median
            views_90d = max(8000, min(150000, views_90d))
        else:
            # Emerging creators: 1K to 20K views
            views_90d = int(np.random.lognormal(mean=9.0, sigma=0.6))  # ~8K median
            views_90d = max(1000, min(25000, views_90d))
        
        # Language selection
        language = np.random.choice(languages, p=language_weights)
        
        # Performance calculation based on topic relevance
        # High-demand topics perform better
        high_demand_topics = ["Python", "Data Science", "Machine Learning", "JavaScript", 
                             "React", "SQL", "Career Guidance", "Interview Preparation"]
        
        if any(topic_word in topic for topic_word in high_demand_topics):
            base_performance = 0.8  # High performance for in-demand topics
        else:
            base_performance = 0.5  # Medium performance for other topics
        
        # Language impact (English performs slightly better for tech content)
        lang_multiplier = {"English": 1.2, "Hindi": 1.0, "Telugu": 0.9}[language]
        
        # Posting frequency impact
        freq_multiplier = max(0.5, 1.5 - (posting_cadence / 10))  # More frequent = better
        
        # Calculate realistic performance metrics for reputed EdTech platform
        performance_factor = base_performance * lang_multiplier * freq_multiplier
        
        # Realistic CTR for EdTech content (0.8% to 5% - higher than general content)
        base_ctr = 0.008 + (performance_factor * 0.042)
        # Add some realistic variance
        ctr = base_ctr + np.random.normal(0, 0.006)
        ctr = max(0.003, min(0.08, ctr))  # Clip to realistic bounds
        clicks = int(views_90d * ctr)
        
        # Lead conversion rate (4% to 18% of clicks - EdTech has higher intent)
        base_lead_rate = 0.04 + (performance_factor * 0.14)
        lead_rate = base_lead_rate + np.random.normal(0, 0.025)
        lead_rate = max(0.015, min(0.25, lead_rate))
        leads = max(1, int(clicks * lead_rate))
        
        # Qualification rate (50% to 85% - Odin School has good screening)
        base_qualified_rate = 0.5 + (performance_factor * 0.35)
        qualified_rate = base_qualified_rate + np.random.normal(0, 0.08)
        qualified_rate = max(0.3, min(0.9, qualified_rate))
        qualified_leads = max(1, int(leads * qualified_rate))
        
        # Enrollment rate (30% to 70% - realistic for paid courses)
        base_enrollment_rate = 0.3 + (performance_factor * 0.4)
        enrollment_rate = base_enrollment_rate + np.random.normal(0, 0.07)
        enrollment_rate = max(0.15, min(0.75, enrollment_rate))
        enrollments = int(qualified_leads * enrollment_rate)
        
        # Refund rate (2% to 12% - realistic for online courses)
        refund_rate = 0.02 + np.random.uniform(0, 0.1)
        refunds = int(enrollments * refund_rate)
        
        # All creators are in India (focused market)
        geography = "INDIA"
        
        # Category tags (1-2 tags)
        num_tags = np.random.choice([1, 2], p=[0.6, 0.4])
        selected_tags = np.random.choice(category_tags, size=num_tags, replace=False)
        category_tag = ";".join(selected_tags)
        
        creators.append({
            "creator_id": creator_id,
            "topic": topic,
            "recent_video_transcript": transcript,
            "posting_cadence_days": posting_cadence,  # Pure integer
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
    """Generate and save the EdTech-focused dataset."""
    print("🎓 Generating EdTech-focused CreatorFit dataset...")
    
    # Generate the dataset
    df = generate_edtech_creator_data(n_creators=1500)
    
    # Save to CSV
    output_path = Path("dataset/creator_campaign_audience_EDTECH.csv")
    output_path.parent.mkdir(exist_ok=True)
    df.to_csv(output_path, index=False)
    
    # Print summary statistics
    print(f"✅ EdTech dataset saved to: {output_path}")
    print(f"📊 Dataset shape: {df.shape}")
    print(f"\n🎯 Target variable (qualified_leads) statistics:")
    print(df['qualified_leads'].describe())
    
    print(f"\n📚 Topic distribution (top 10):")
    topic_counts = df['topic'].value_counts().head(10)
    for topic, count in topic_counts.items():
        print(f"  {topic}: {count}")
    
    print(f"\n🗣️ Language distribution:")
    lang_counts = df['language'].value_counts()
    for lang, count in lang_counts.items():
        print(f"  {lang}: {count} ({count/len(df)*100:.1f}%)")
    
    print(f"\n📅 Posting cadence distribution:")
    cadence_counts = df['posting_cadence_days'].value_counts().sort_index()
    for days, count in cadence_counts.items():
        print(f"  Every {days} days: {count} creators")
    
    print(f"\n🌍 Geography: {df['geography'].unique()}")
    
    # Show correlation with target
    numeric_cols = ['posting_cadence_days', 'views_90d', 'clicks', 'leads', 'qualified_leads']
    correlations = df[numeric_cols].corr()['qualified_leads'].sort_values(ascending=False)
    print(f"\n🔗 Correlations with qualified_leads:")
    for col, corr in correlations.items():
        if col != 'qualified_leads':
            print(f"  {col}: {corr:.3f}")

if __name__ == "__main__":
    main()
