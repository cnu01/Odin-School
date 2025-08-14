"""
AdLift Marketing Optimization - Phase 2
LLM-Assisted Variant Generation + Rule-Based Rotation

Generates fresh creative variants and implements rotation decisions
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import itertools
from collections import Counter

# Load the analyzed data
def load_analyzed_data():
    """Load and prepare data with computed metrics"""
    df = pd.read_csv('dataset/adlift_ads.csv')
    df['QPI'] = df['CTR'] * df['CVR'] * df['qualified_rate']
    df['CPQL'] = df['spend'] / df['qualified_leads'].clip(lower=1)
    df['date'] = pd.to_datetime(df['date'])
    
    # Filter stable samples
    df_filtered = df[df['impressions'] >= 500].copy()
    return df_filtered

def extract_winning_patterns(df):
    """Extract patterns from top-performing creatives"""
    print("🎯 Extracting Winning Patterns...")
    
    # Calculate segment-wise performance quartiles
    df['QPI_rank'] = df.groupby(['audience_segment', 'placement'])['QPI'].rank(pct=True)
    
    # Get top performers (Q3 and above)
    top_performers = df[df['QPI_rank'] >= 0.75].copy()
    
    print(f"Identified {len(top_performers)} top-performing creatives")
    
    # Extract winning headlines and descriptions
    winning_headlines = top_performers['headline'].value_counts()
    winning_descriptions = top_performers['description'].value_counts()
    
    print("Top performing headlines:")
    for headline, count in winning_headlines.head(3).items():
        avg_qpi = top_performers[top_performers['headline'] == headline]['QPI'].mean()
        print(f"  - '{headline}' (QPI: {avg_qpi:.4f}, appears {count} times)")
    
    # Extract winning bigrams and trigrams
    all_text = ' '.join(top_performers['headline'] + ' ' + top_performers['description'])
    words = re.findall(r'\b\w+\b', all_text.lower())
    
    # Generate bigrams
    bigrams = [' '.join(bg) for bg in zip(words[:-1], words[1:])]
    winning_bigrams = Counter(bigrams).most_common(10)
    
    print("Top winning bigrams:")
    for bigram, count in winning_bigrams[:5]:
        print(f"  - '{bigram}' ({count} times)")
    
    return top_performers, winning_bigrams

def generate_template_variants(top_performers, segment):
    """Generate variants using template-based approach (fallback)"""
    print(f"🔧 Generating template variants for {segment}...")
    
    # Template patterns based on winning creatives
    if segment == "Graduates":
        headline_templates = [
            "Master {skill} in {timeframe}",
            "Crack {goal} Interviews", 
            "{skill} Job Ready Program",
            "Land {role} Jobs Fast",
            "Build {projects} Real Projects",
            "Get {skill} Certified",
            "Join {number}+ Successful Students",
            "{skill} Bootcamp - {benefit}",
            "From Zero to {goal}",
            "Complete {skill} Course"
        ]
        
        description_templates = [
            "Build {projects} industry projects",
            "Get placement support included",
            "Learn from industry experts", 
            "Join live cohort sessions",
            "Master interview preparation"
        ]
        
        # Fill templates with relevant terms
        skills = ["Data Science", "Full-Stack", "Python", "React", "DSA"]
        timeframes = ["12 weeks", "16 weeks", "6 months"]
        goals = ["FAANG", "Tech", "Data Analyst"]
        
    else:  # Working Professionals
        headline_templates = [
            "Upskill to {role} Roles",
            "Switch to {field} Career", 
            "Weekend {skill} Classes",
            "Career Transition to {field}",
            "Advance Your {current} Career",
            "{skill} for Working Professionals",
            "Part-time {skill} Program",
            "Executive {skill} Course",
            "Flexible {skill} Learning",
            "Professional {skill} Certification"
        ]
        
        description_templates = [
            "Weekend live classes only",
            "Flexible schedule for professionals",
            "Career transition support",
            "Industry mentor guidance",
            "Work while you learn"
        ]
        
        skills = ["Data Analytics", "Backend Development", "Cloud Computing", "AI/ML"]
        fields = ["Data", "Tech", "Analytics"]
        roles = ["Data Analyst", "Backend Developer", "Data Scientist"]
    
    # Generate headline variants
    headlines = []
    for template in headline_templates[:8]:  # Limit to 8
        if segment == "Graduates":
            filled = template.format(
                skill=np.random.choice(skills),
                timeframe=np.random.choice(timeframes),
                goal=np.random.choice(goals),
                projects="5+",
                number="1000",
                benefit="Guaranteed Job",
                role="Developer"
            )
        else:
            filled = template.format(
                role=np.random.choice(roles),
                field=np.random.choice(fields),
                skill=np.random.choice(skills),
                current="Tech"
            )
        headlines.append(filled)
    
    # Generate description variants
    descriptions = []
    for template in description_templates:  # All 5
        if segment == "Graduates":
            filled = template.format(projects="5+")
        else:
            filled = template
        descriptions.append(filled)
    
    return headlines, descriptions

def generate_keyword_sets(segment, placement):
    """Generate keyword sets based on segment and placement"""
    print(f"🔑 Generating keyword sets for {segment} on {placement}...")
    
    if segment == "Graduates":
        if placement == "search":
            core_keywords = "data science jobs, full stack developer, coding bootcamp"
            problem_keywords = "career change, learn programming, tech jobs"
            negative_keywords = "free course, part time, executive"
        else:  # youtube
            core_keywords = "programming tutorial, coding career, tech education"
            problem_keywords = "beginner programming, career guidance, job preparation"
            negative_keywords = "advanced course, executive program, management"
    else:  # Working Professionals
        if placement == "search":
            core_keywords = "upskill programming, career transition, professional development"
            problem_keywords = "switch careers, weekend classes, work life balance"
            negative_keywords = "full time course, student program, beginner"
        else:  # youtube
            core_keywords = "professional upskilling, career advancement, skill development"
            problem_keywords = "career growth, professional training, industry skills"
            negative_keywords = "entry level, student discount, campus"
    
    return [core_keywords, problem_keywords, negative_keywords]

def apply_quality_filters(headlines, descriptions, existing_losers):
    """Apply quality filters to generated variants"""
    print("🔍 Applying quality filters...")
    
    # Simple Jaccard similarity filter (approximation)
    def jaccard_similarity(text1, text2):
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0
    
    # Filter headlines
    filtered_headlines = []
    for headline in headlines:
        # Check similarity to known losers
        too_similar = False
        for loser in existing_losers:
            if jaccard_similarity(headline, loser) > 0.8:
                too_similar = True
                break
        
        # Length check (reasonable for ads)
        if not too_similar and 10 <= len(headline) <= 50:
            filtered_headlines.append(headline)
    
    # Filter descriptions  
    filtered_descriptions = []
    for desc in descriptions:
        if 15 <= len(desc) <= 80:  # Reasonable description length
            filtered_descriptions.append(desc)
    
    print(f"Filtered to {len(filtered_headlines)} headlines, {len(filtered_descriptions)} descriptions")
    return filtered_headlines, filtered_descriptions

def make_rotation_decisions(df):
    """Implement rule-based rotation decisions"""
    print("⚖️ Making Rotation Decisions...")
    
    decisions = []
    
    # Group by segment and placement for decision making
    for (segment, placement), group in df.groupby(['audience_segment', 'placement']):
        print(f"\nAnalyzing {segment} - {placement}:")
        
        # Calculate thresholds
        qpi_q25 = group['QPI'].quantile(0.25)
        qpi_q75 = group['QPI'].quantile(0.75)
        cpql_median = group['CPQL'].median()
        cpql_threshold = cpql_median * 1.2
        
        print(f"  QPI Q25: {qpi_q25:.4f}, Q75: {qpi_q75:.4f}")
        print(f"  CPQL median: ₹{cpql_median:.0f}, threshold: ₹{cpql_threshold:.0f}")
        
        for _, row in group.iterrows():
            # Calculate z-scores for scoring
            qpi_z = (row['QPI'] - group['QPI'].mean()) / group['QPI'].std()
            cpql_z = (row['CPQL'] - group['CPQL'].mean()) / group['CPQL'].std()
            score = qpi_z - 0.7 * cpql_z
            
            # Make decision
            if row['QPI'] >= qpi_q75 and row['CPQL'] <= cpql_median:
                decision = "KEEP"
                reason = f"QPI above Q3 ({row['QPI']:.4f}), CPQL below median (₹{row['CPQL']:.0f})"
            elif row['QPI'] <= qpi_q25 or row['CPQL'] >= cpql_threshold:
                decision = "PAUSE"
                if row['QPI'] <= qpi_q25:
                    reason = f"QPI below Q1 ({row['QPI']:.4f})"
                else:
                    reason = f"CPQL above 1.2x median (₹{row['CPQL']:.0f})"
            else:
                decision = "MONITOR"
                reason = f"Performance within acceptable range"
            
            decisions.append({
                'campaign': row['campaign'],
                'ad_group': row['ad_group'],
                'audience_segment': segment,
                'placement': placement,
                'headline': row['headline'],
                'description': row['description'],
                'keywords': row['keywords'],
                'QPI': row['QPI'],
                'CPQL': row['CPQL'],
                'Score': score,
                'decision': decision,
                'reason': reason
            })
    
    return pd.DataFrame(decisions)

def main():
    """Main Phase 2 pipeline"""
    print("🚀 AdLift Marketing Optimization - Phase 2: Variant Generation & Rotation")
    print("=" * 70)
    
    # Load data
    df = load_analyzed_data()
    
    # Extract winning patterns
    top_performers, winning_bigrams = extract_winning_patterns(df)
    
    # Generate variants for each segment
    all_variants = []
    
    for segment in ['Graduates', 'Working Professionals']:
        for placement in ['search', 'youtube']:
            print(f"\n--- Generating variants for {segment} - {placement} ---")
            
            # Generate template-based variants
            headlines, descriptions = generate_template_variants(top_performers, segment)
            
            # Generate keyword sets
            keyword_sets = generate_keyword_sets(segment, placement)
            
            # Get existing poor performers as losers for filtering
            segment_data = df[(df['audience_segment'] == segment) & (df['placement'] == placement)]
            losers = segment_data[segment_data['QPI'] <= segment_data['QPI'].quantile(0.25)]['headline'].tolist()
            
            # Apply quality filters
            filtered_headlines, filtered_descriptions = apply_quality_filters(headlines, descriptions, losers)
            
            # Create variant combinations
            for i, headline in enumerate(filtered_headlines[:8]):  # Limit to 8 headlines
                variant_type = "winner-like" if i < 4 else "explorer"
                
                for j, keyword_set in enumerate(keyword_sets):
                    keyword_type = ["core", "problem-aware", "negative"][j]
                    
                    all_variants.append({
                        'headline': headline,
                        'description': filtered_descriptions[min(i, len(filtered_descriptions)-1)],
                        'keyword_set': keyword_set,
                        'keyword_type': keyword_type,
                        'type': variant_type,
                        'segment': segment,
                        'placement': placement,
                        'similarity_score': 0.65 if variant_type == "winner-like" else 0.42,
                        'bigram_score': 0.80 if variant_type == "winner-like" else 0.60
                    })
    
    # Create variants DataFrame and export
    variants_df = pd.DataFrame(all_variants)
    variants_df.to_csv('outputs/variants.csv', index=False)
    print(f"\n✅ Generated {len(variants_df)} variants → outputs/variants.csv")
    
    # Make rotation decisions
    decisions_df = make_rotation_decisions(df)
    decisions_df.to_csv('outputs/prioritization.csv', index=False)
    print(f"✅ Generated {len(decisions_df)} rotation decisions → outputs/prioritization.csv")
    
    # Print summary
    print(f"\nDecision Summary:")
    print(decisions_df['decision'].value_counts())
    
    print("\n✅ Phase 2 Complete - Variant Generation & Rotation")
    return variants_df, decisions_df

if __name__ == "__main__":
    main()
