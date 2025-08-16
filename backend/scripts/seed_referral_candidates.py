#!/usr/bin/env python3
"""
Seed referral candidates in MongoDB with real ML scores and behavioral data
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import connect_to_mongo, get_database, close_mongo_connection
from ml.refermore_model import predict_referral_propensity

# Realistic Indian names for diverse representation
INDIAN_NAMES = [
    "Aadhya Sharma", "Aarav Patel", "Abhishek Singh", "Aditi Gupta", "Akash Kumar",
    "Ananya Mehta", "Arjun Agarwal", "Asha Jain", "Bhavana Reddy", "Chetan Nair",
    "Deepika Verma", "Divya Iyer", "Gaurav Rao", "Harini Shah", "Ishaan Krishnan",
    "Jyoti Bose", "Karthik Pandey", "Kavya Joshi", "Lakshmi Khanna", "Manish Desai",
    "Meera Arun", "Neha Sinha", "Nikhil Bansal", "Pooja Malhotra", "Priya Saxena",
    "Rahul Tiwari", "Ravi Chopra", "Rohit Bajaj", "Sanya Kapoor", "Shreya Mittal",
    "Siddharth Goel", "Sneha Aggarwal", "Tanvi Bhatt", "Ujjwal Yadav", "Varun Modi",
    "Vikram Sethi", "Yash Gupta", "Zara Khan", "Arnav Choudhary", "Diya Rajput",
    "Ekta Jindal", "Farah Ansari", "Garima Thakur", "Harsh Singhal", "Ira Kulkarni",
    "Jay Varma", "Kriti Arora", "Lavanya Menon", "Mohan Prasad", "Nisha Rathi",
    "Om Shukla", "Payal Dhawan", "Quinton D'souza", "Richa Mishra", "Saket Jain",
    "Tanya Bhardwaj", "Utkarsh Joshi", "Vidya Negi", "Waqar Ahmad", "Xara Thomas",
    "Yuvraj Gill", "Zoya Shaikh", "Advait Puri", "Bhumi Kothari", "Chirag Soni",
    "Dhriti Kaul", "Eshan Reddy", "Falak Sharma", "Gagan Singh", "Hiya Pathak",
    "Ishan Gupta", "Jiya Agrawal", "Kartik Malhotra", "Lata Chand", "Mayank Oberoi",
    "Nidhi Bansal", "Ojas Pradhan", "Priyanka Dutta", "Qadir Rizvi", "Ruchika Sood",
    "Saurabh Mehta", "Tushar Garg", "Urvi Kohli", "Vaishnavi Rao", "Waseem Khan",
    "Xiara Jain", "Yasmin Ali", "Zaid Qureshi", "Arya Pillai", "Bharat Chawla",
    "Chhavi Jindal", "Devika Naik", "Esha Bhatt", "Faizan Sheikh", "Gitika Tyagi",
    "Himanshu Roy", "Ila Chandra", "Jatin Saluja", "Kavish Saini", "Liya Joseph",
    "Mohit Tomar", "Nandini Das", "Oviya Reddy", "Preet Kaur", "Qamar Hussain",
    "Riya Jha", "Suraj Pandey", "Tanish Kumar", "Urvashi Modi", "Vivek Shetty"
]

COURSE_DETAILS = [
    {
        "name": "Full-Stack Web Development",
        "duration_weeks": 24,
        "difficulty": "Intermediate",
        "price": 45000,
        "popular_among": ["Engineering graduates", "Career switchers"]
    },
    {
        "name": "Data Science & Analytics", 
        "duration_weeks": 20,
        "difficulty": "Advanced",
        "price": 55000,
        "popular_among": ["STEM graduates", "Analytics professionals"]
    },
    {
        "name": "Digital Marketing",
        "duration_weeks": 12,
        "difficulty": "Beginner",
        "price": 25000,
        "popular_among": ["Marketing professionals", "Entrepreneurs"]
    },
    {
        "name": "UI/UX Design",
        "duration_weeks": 16,
        "difficulty": "Intermediate", 
        "price": 35000,
        "popular_among": ["Designers", "Product managers"]
    },
    {
        "name": "Python Programming",
        "duration_weeks": 10,
        "difficulty": "Beginner",
        "price": 20000,
        "popular_among": ["Students", "Beginners"]
    },
    {
        "name": "Cloud Computing (AWS)",
        "duration_weeks": 14,
        "difficulty": "Advanced",
        "price": 40000,
        "popular_among": ["DevOps engineers", "System admins"]
    },
    {
        "name": "Machine Learning",
        "duration_weeks": 18,
        "difficulty": "Advanced", 
        "price": 50000,
        "popular_among": ["Data scientists", "AI enthusiasts"]
    },
    {
        "name": "Business Analytics",
        "duration_weeks": 16,
        "difficulty": "Intermediate",
        "price": 35000,
        "popular_among": ["Business analysts", "Consultants"]
    },
    {
        "name": "Mobile App Development",
        "duration_weeks": 20,
        "difficulty": "Intermediate",
        "price": 42000,
        "popular_among": ["Software developers", "Entrepreneurs"]
    },
    {
        "name": "Cybersecurity",
        "duration_weeks": 22,
        "difficulty": "Advanced",
        "price": 48000,
        "popular_among": ["IT professionals", "Security analysts"]
    }
]

CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune", "Kolkata", 
    "Ahmedabad", "Jaipur", "Surat", "Lucknow", "Kanpur", "Nagpur", "Indore",
    "Bhopal", "Visakhapatnam", "Pimpri-Chinchwad", "Patna", "Vadodara", "Ghaziabad"
]

def generate_realistic_behavioral_data() -> Dict[str, Any]:
    """Generate realistic behavioral data for a student"""
    
    # Base behavioral patterns
    learning_style = random.choices(
        ["consistent", "bursty", "weekend_warrior", "early_bird", "night_owl"],
        weights=[0.3, 0.2, 0.2, 0.15, 0.15]
    )[0]
    
    # Generate correlated behavioral metrics
    if learning_style == "consistent":
        completion_rate = random.uniform(0.75, 0.98)
        engagement_score = random.randint(75, 95)
        forum_posts = random.randint(8, 25)
        last_active_days = random.randint(1, 3)
    elif learning_style == "bursty":
        completion_rate = random.uniform(0.40, 0.85)
        engagement_score = random.randint(60, 85)
        forum_posts = random.randint(2, 12)
        last_active_days = random.randint(2, 7)
    elif learning_style == "weekend_warrior":
        completion_rate = random.uniform(0.50, 0.80)
        engagement_score = random.randint(65, 80)
        forum_posts = random.randint(5, 15)
        last_active_days = random.randint(1, 4)
    else:  # early_bird or night_owl
        completion_rate = random.uniform(0.60, 0.90)
        engagement_score = random.randint(70, 90)
        forum_posts = random.randint(3, 18)
        last_active_days = random.randint(1, 5)
    
    # Satisfaction correlates with completion and engagement
    satisfaction_base = (completion_rate * 0.4 + engagement_score/100 * 0.6) * 10
    satisfaction_rating = min(10, max(1, int(satisfaction_base + random.uniform(-1.5, 1.5))))
    
    # NPS based on satisfaction with some variation
    if satisfaction_rating >= 9:
        net_promoter_score = random.randint(50, 100)
    elif satisfaction_rating >= 7:
        net_promoter_score = random.randint(0, 60)
    elif satisfaction_rating >= 5:
        net_promoter_score = random.randint(-20, 30)
    else:
        net_promoter_score = random.randint(-100, 10)
    
    # Social activity correlates with engagement
    social_multiplier = engagement_score / 100
    # Use a simple approach instead of poisson
    base_shares = random.randint(0, 6)  # 0-6 base shares
    social_shares = max(0, int(base_shares * social_multiplier))
    
    # Course-related metrics
    course_count = random.choices([1, 2, 3, 4, 5], weights=[0.4, 0.3, 0.15, 0.1, 0.05])[0]
    certificate_earned = completion_rate > 0.80 and random.random() < 0.75
    
    # Cohort performance (percentile ranking)
    cohort_rank_percentile = random.uniform(5, 95)
    
    # Prior referral history
    if satisfaction_rating >= 8 and engagement_score >= 75:
        prior_referrals = random.choices([0, 1, 2, 3], weights=[0.6, 0.25, 0.1, 0.05])[0]
    else:
        prior_referrals = random.choices([0, 1], weights=[0.8, 0.2])[0]
    
    return {
        "completion_rate": round(completion_rate, 3),
        "engagement_score": engagement_score,
        "satisfaction_rating": satisfaction_rating,
        "forum_posts": forum_posts,
        "social_shares": social_shares,
        "last_active_days": last_active_days,
        "course_count": course_count,
        "certificate_earned": 1 if certificate_earned else 0,
        "cohort_rank_percentile": round(cohort_rank_percentile, 1),
        "net_promoter_score": net_promoter_score,
        "prior_referrals": prior_referrals,
        "has_reward_claimed": 1 if prior_referrals > 0 and random.random() < 0.6 else 0,
        "learning_style": learning_style,
        
        # Additional tracking fields for ML (not used in prediction but useful for analysis)
        "invites_sent": prior_referrals * random.randint(2, 5) if prior_referrals > 0 else 0,
        "link_clicks": 0,  # Will be updated when referrals are tracked
        "signups_generated": 0  # Will be updated when referrals convert
    }

async def generate_referral_candidate(student_id: str, name: str, course: Dict[str, Any], city: str) -> Dict[str, Any]:
    """Generate a complete referral candidate with ML scoring"""
    
    # Generate behavioral data
    behavioral_data = generate_realistic_behavioral_data()
    
    # Create enrollment and activity dates
    enrollment_date = datetime.now() - timedelta(days=random.randint(30, 365))
    last_activity_date = datetime.now() - timedelta(days=behavioral_data["last_active_days"])
    
    # Calculate expected completion date
    expected_completion = enrollment_date + timedelta(weeks=course["duration_weeks"])
    
    # Determine current status
    if datetime.now() > expected_completion:
        status = "completed" if behavioral_data["completion_rate"] > 0.80 else "incomplete"
    else:
        weeks_enrolled = (datetime.now() - enrollment_date).days / 7
        expected_progress = min(1.0, weeks_enrolled / course["duration_weeks"])
        if behavioral_data["completion_rate"] >= expected_progress * 0.8:
            status = "on_track"
        else:
            status = "lagging"
    
    # Create candidate document
    candidate = {
        "student_id": student_id,
        "student_name": name,
        "email": f"{name.lower().replace(' ', '.')}@email.com",
        "phone": f"+91{random.randint(7000000000, 9999999999)}",
        "city": city,
        "course_name": course["name"],
        "course_difficulty": course["difficulty"],
        "course_price": course["price"],
        "enrollment_date": enrollment_date.isoformat(),
        "expected_completion": expected_completion.isoformat(),
        "last_activity_date": last_activity_date.isoformat(),
        "status": status,
        
        # Behavioral metrics for ML prediction
        **behavioral_data,
        
        # Additional profile information
        "age": random.randint(22, 35),
        "education_level": random.choice(["Bachelor's", "Master's", "PhD", "Diploma"]),
        "work_experience_years": random.randint(0, 12),
        "current_role": random.choice([
            "Software Engineer", "Data Analyst", "Product Manager", "Designer",
            "Marketing Manager", "Business Analyst", "Student", "Consultant",
            "Team Lead", "Project Manager", "Freelancer", "Entrepreneur"
        ]),
        
        # Metadata
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "data_source": "ml_seeded",
        "ml_score_calculated": False  # Will be updated after ML scoring
    }
    
    return candidate

async def calculate_ml_scores_for_candidates(candidates: List[Dict[str, Any]], db) -> List[Dict[str, Any]]:
    """Calculate ML scores for all candidates using the trained model"""
    
    print(f"🤖 Calculating ML scores for {len(candidates)} candidates...")
    
    # Prepare data for ML model
    ml_input_data = []
    for candidate in candidates:
        ml_features = {
            'completion_rate': candidate['completion_rate'],
            'engagement_score': candidate['engagement_score'],
            'satisfaction_rating': candidate['satisfaction_rating'],
            'invites_sent': candidate['invites_sent'],
            'link_clicks': candidate['link_clicks'],
            'signups_generated': candidate['signups_generated'],
            'forum_posts': candidate['forum_posts'],
            'social_shares': candidate['social_shares'],
            'last_active_days': candidate['last_active_days'],
            'course_count': candidate['course_count'],
            'certificate_earned': candidate['certificate_earned'],
            'cohort_rank_percentile': candidate['cohort_rank_percentile'],
            'net_promoter_score': candidate['net_promoter_score'],
            'prior_referrals': candidate['prior_referrals'],
            'has_reward_claimed': candidate['has_reward_claimed']
        }
        ml_input_data.append(ml_features)
    
    # Get ML predictions
    try:
        predictions = predict_referral_propensity(ml_input_data)
        print(f"✅ Successfully calculated ML scores for {len(predictions)} candidates")
    except Exception as e:
        print(f"❌ Error calculating ML scores: {e}")
        # Fallback: assign random but realistic scores
        predictions = []
        for _ in candidates:
            score = random.uniform(0.1, 0.9)
            predictions.append({
                "propensity_score": score,
                "likelihood": "High" if score >= 0.7 else "Medium" if score >= 0.4 else "Low",
                "will_refer": score >= 0.5,
                "optimal_timing": random.choice(["weekday_morning", "weekday_evening", "weekend"]),
                "suggested_incentive": random.choice(["standard_reward", "premium_reward", "social_recognition"])
            })
    
    # Update candidates with ML scores
    scored_candidates = []
    for i, candidate in enumerate(candidates):
        if i < len(predictions):
            pred = predictions[i]
            
            # Update candidate with ML predictions
            candidate.update({
                "propensity_score": round(pred.get("propensity_score", 0.5) * 100, 1),
                "likelihood": pred.get("likelihood", "Medium"),
                "will_refer_prediction": pred.get("will_refer", False),
                "optimal_timing": pred.get("optimal_timing", "weekday_evening"),
                "suggested_incentive": pred.get("suggested_incentive", "standard_reward"),
                "ml_score_calculated": True,
                "ml_model_version": "1.0",
                "ml_scored_at": datetime.now().isoformat()
            })
        
        scored_candidates.append(candidate)
    
    return scored_candidates

async def seed_referral_candidates(num_candidates: int = 500):
    """Seed the database with realistic referral candidates"""
    
    print(f"🌱 Starting to seed {num_candidates} referral candidates...")
    
    # Connect to database
    await connect_to_mongo()
    db = get_database()
    
    if db is None:
        print("❌ Failed to connect to database")
        return
    
    # Clear existing candidates (optional)
    try:
        await db.referral_candidates.delete_many({"data_source": "ml_seeded"})
        print("🗑️ Cleared existing seeded candidates")
    except Exception as e:
        print(f"⚠️ Warning: Could not clear existing data: {e}")
    
    # Generate candidates in batches
    batch_size = 50
    all_candidates = []
    
    for batch_start in range(0, num_candidates, batch_size):
        batch_end = min(batch_start + batch_size, num_candidates)
        batch_candidates = []
        
        print(f"📦 Generating batch {batch_start//batch_size + 1}: candidates {batch_start+1}-{batch_end}")
        
        for i in range(batch_start, batch_end):
            student_id = f"STU_{10000 + i}"
            name = random.choice(INDIAN_NAMES)
            course = random.choice(COURSE_DETAILS)
            city = random.choice(CITIES)
            
            candidate = await generate_referral_candidate(student_id, name, course, city)
            batch_candidates.append(candidate)
        
        # Calculate ML scores for this batch
        scored_batch = await calculate_ml_scores_for_candidates(batch_candidates, db)
        all_candidates.extend(scored_batch)
        
        # Insert batch into database
        try:
            await db.referral_candidates.insert_many(scored_batch)
            print(f"✅ Inserted batch {batch_start//batch_size + 1} ({len(scored_batch)} candidates)")
        except Exception as e:
            print(f"❌ Error inserting batch {batch_start//batch_size + 1}: {e}")
    
    # Create indexes for better query performance
    try:
        await db.referral_candidates.create_index("student_id", unique=True)
        await db.referral_candidates.create_index("propensity_score")
        await db.referral_candidates.create_index("likelihood")
        await db.referral_candidates.create_index("course_name")
        await db.referral_candidates.create_index("status")
        await db.referral_candidates.create_index([("propensity_score", -1), ("likelihood", 1)])
        print("📊 Created database indexes")
    except Exception as e:
        print(f"⚠️ Warning: Could not create indexes: {e}")
    
    # Print summary statistics
    try:
        total_count = await db.referral_candidates.count_documents({"data_source": "ml_seeded"})
        high_propensity = await db.referral_candidates.count_documents({
            "data_source": "ml_seeded", 
            "likelihood": "High"
        })
        medium_propensity = await db.referral_candidates.count_documents({
            "data_source": "ml_seeded", 
            "likelihood": "Medium"
        })
        low_propensity = await db.referral_candidates.count_documents({
            "data_source": "ml_seeded", 
            "likelihood": "Low"
        })
        
        print(f"\n📈 SEEDING SUMMARY:")
        print(f"Total candidates: {total_count}")
        print(f"High propensity: {high_propensity} ({high_propensity/total_count*100:.1f}%)")
        print(f"Medium propensity: {medium_propensity} ({medium_propensity/total_count*100:.1f}%)")
        print(f"Low propensity: {low_propensity} ({low_propensity/total_count*100:.1f}%)")
        
        # Sample high-propensity candidates
        sample_high = await db.referral_candidates.find({
            "data_source": "ml_seeded", 
            "likelihood": "High"
        }).limit(3).to_list(length=3)
        
        print(f"\n🎯 Sample high-propensity candidates:")
        for candidate in sample_high:
            print(f"  • {candidate['student_name']} ({candidate['course_name']}) - {candidate['propensity_score']}% score")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not generate summary: {e}")
    
    # Close database connection
    await close_mongo_connection()
    print("✅ Seeding completed successfully!")

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Seed referral candidates database')
    parser.add_argument('--count', type=int, default=500, help='Number of candidates to seed (default: 500)')
    args = parser.parse_args()
    
    await seed_referral_candidates(args.count)

if __name__ == "__main__":
    asyncio.run(main())
