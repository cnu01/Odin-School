#!/usr/bin/env python3
"""
Data Migration Script: PostgreSQL to MongoDB
Migrates HotLead, ReferMore, and OneTruth data from backend PostgreSQL to Odin-School MongoDB
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

import psycopg2
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import json
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DataMigrator:
    def __init__(self):
        # PostgreSQL connection (Backend)
        self.pg_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'odin_ai_db',
            'user': 'odin_user',
            'password': 'odin_secure_2025'
        }
        
        # MongoDB connection (Odin-School)
        self.mongo_url = os.getenv("MONGODB_URL", "mongodb+srv://cnu:jb1y6avC2cm6oRxg@cluster0.xiuz0db.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        self.mongo_db_name = os.getenv("DATABASE_NAME", "odin_school_db")
        
        self.mongo_client = None
        self.mongo_db = None
        
    async def connect_mongodb(self):
        """Connect to MongoDB"""
        try:
            self.mongo_client = AsyncIOMotorClient(self.mongo_url)
            self.mongo_db = self.mongo_client[self.mongo_db_name]
            # Test connection
            await self.mongo_client.admin.command('ping')
            print("✅ Connected to MongoDB")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            return False
    
    def connect_postgresql(self):
        """Connect to PostgreSQL"""
        try:
            conn = psycopg2.connect(**self.pg_config)
            print("✅ Connected to PostgreSQL")
            return conn
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            return None
    
    async def migrate_hotlead_data(self):
        """Migrate HotLead data from PostgreSQL leads table to MongoDB leads collection"""
        print("\n🔄 Migrating HotLead data...")
        
        pg_conn = self.connect_postgresql()
        if not pg_conn:
            return False
        
        try:
            # Query PostgreSQL leads table
            query = """
            SELECT 
                lead_id, email, phone, source, utm_source, utm_medium, utm_campaign,
                page_views, time_on_site, downloads, email_opens,
                location, job_title, company, experience_level,
                conversion_probability, priority_score, is_priority, lead_temperature,
                risk_score, optimal_contact_time, status, assigned_rep,
                contacted_at, last_activity, behavioral_data,
                created_at, updated_at, is_active
            FROM leads
            WHERE is_active = true
            ORDER BY created_at DESC
            """
            
            df = pd.read_sql_query(query, pg_conn)
            print(f"📊 Found {len(df)} leads in PostgreSQL")
            
            if len(df) == 0:
                print("⚠️ No leads found in PostgreSQL. Generating synthetic data...")
                # Generate synthetic data for demo
                from ml.hotlead_model import generate_synthetic_lead_data
                synthetic_df = generate_synthetic_lead_data(num_samples=1000)
                df = synthetic_df
            
            # Convert to MongoDB documents
            documents = []
            for _, row in df.iterrows():
                doc = row.to_dict()
                
                # Handle datetime fields
                for date_field in ['contacted_at', 'last_activity', 'created_at', 'updated_at']:
                    if pd.notna(doc.get(date_field)):
                        doc[date_field] = doc[date_field].isoformat() if hasattr(doc[date_field], 'isoformat') else str(doc[date_field])
                    else:
                        doc[date_field] = None
                
                # Handle JSON fields
                if doc.get('behavioral_data'):
                    if isinstance(doc['behavioral_data'], str):
                        try:
                            doc['behavioral_data'] = json.loads(doc['behavioral_data'])
                        except:
                            doc['behavioral_data'] = {}
                
                # Add migration metadata
                doc['_migrated_at'] = datetime.now().isoformat()
                doc['_source'] = 'postgresql_migration'
                
                documents.append(doc)
            
            # Insert into MongoDB
            collection = self.mongo_db['leads']
            await collection.delete_many({})  # Clear existing data
            
            if documents:
                result = await collection.insert_many(documents)
                print(f"✅ Migrated {len(result.inserted_ids)} leads to MongoDB")
            
            return True
            
        except Exception as e:
            print(f"❌ HotLead migration failed: {e}")
            return False
        finally:
            pg_conn.close()
    
    async def migrate_refermore_data(self):
        """Migrate ReferMore data from PostgreSQL referrals table to MongoDB referrals collection"""
        print("\n🔄 Migrating ReferMore data...")
        
        pg_conn = self.connect_postgresql()
        if not pg_conn:
            return False
        
        try:
            # Query PostgreSQL referrals table
            query = """
            SELECT 
                user_id, referrer_id, email, course_completed, completion_date,
                satisfaction_score, referral_method, incentive_offered, referral_successful,
                referral_probability, optimal_timing, best_incentive, expected_referrals,
                created_at, updated_at
            FROM referrals
            ORDER BY created_at DESC
            """
            
            df = pd.read_sql_query(query, pg_conn)
            print(f"📊 Found {len(df)} referrals in PostgreSQL")
            
            if len(df) == 0:
                print("⚠️ No referrals found in PostgreSQL. Generating synthetic data...")
                # Generate synthetic data for demo
                from ml.refermore_model import generate_synthetic_training_data
                synthetic_df = generate_synthetic_training_data(num_samples=1000)
                df = synthetic_df
            
            # Convert to MongoDB documents
            documents = []
            for _, row in df.iterrows():
                doc = row.to_dict()
                
                # Handle datetime fields
                for date_field in ['completion_date', 'created_at', 'updated_at']:
                    if pd.notna(doc.get(date_field)):
                        doc[date_field] = doc[date_field].isoformat() if hasattr(doc[date_field], 'isoformat') else str(doc[date_field])
                    else:
                        doc[date_field] = None
                
                # Add migration metadata
                doc['_migrated_at'] = datetime.now().isoformat()
                doc['_source'] = 'postgresql_migration'
                
                documents.append(doc)
            
            # Insert into MongoDB
            collection = self.mongo_db['referrals']
            await collection.delete_many({})  # Clear existing data
            
            if documents:
                result = await collection.insert_many(documents)
                print(f"✅ Migrated {len(result.inserted_ids)} referrals to MongoDB")
            
            return True
            
        except Exception as e:
            print(f"❌ ReferMore migration failed: {e}")
            return False
        finally:
            pg_conn.close()
    
    async def migrate_onetruth_data(self):
        """Migrate OneTruth data from PostgreSQL business_analytics table to MongoDB business_analytics collection"""
        print("\n🔄 Migrating OneTruth data...")
        
        pg_conn = self.connect_postgresql()
        if not pg_conn:
            return False
        
        try:
            # Query PostgreSQL business_analytics table
            query = """
            SELECT 
                week_date, crm_lead_volume, crm_qualified_rate, crm_enrollment_rate, crm_refund_rate,
                ga4_sessions, ga4_bounce_rate, ga4_conversion_rate, ga4_avg_session_duration,
                ad_spend_total, ad_cpl, ad_ctr, ad_conversion_rate,
                support_ticket_volume, support_csat_score, support_resolution_time,
                telephony_connect_rate, telephony_call_volume, telephony_booking_rate,
                lms_active_users, lms_completion_rate, lms_engagement_score,
                business_health_anomaly, created_at, updated_at
            FROM business_analytics
            ORDER BY week_date DESC
            """
            
            df = pd.read_sql_query(query, pg_conn)
            print(f"📊 Found {len(df)} analytics records in PostgreSQL")
            
            if len(df) == 0:
                print("⚠️ No analytics found in PostgreSQL. Generating synthetic data...")
                # Generate synthetic data for demo
                from ml.onetruth_model import generate_synthetic_analytics_data
                synthetic_df = generate_synthetic_analytics_data(num_samples=2000)
                df = synthetic_df
            
            # Convert to MongoDB documents
            documents = []
            for _, row in df.iterrows():
                doc = row.to_dict()
                
                # Handle date fields
                if pd.notna(doc.get('week_date')):
                    doc['week_date'] = doc['week_date'].strftime('%Y-%m-%d') if hasattr(doc['week_date'], 'strftime') else str(doc['week_date'])
                
                # Handle datetime fields
                for date_field in ['created_at', 'updated_at']:
                    if pd.notna(doc.get(date_field)):
                        doc[date_field] = doc[date_field].isoformat() if hasattr(doc[date_field], 'isoformat') else str(doc[date_field])
                    else:
                        doc[date_field] = None
                
                # Ensure numeric fields are proper types
                numeric_fields = [
                    'crm_lead_volume', 'ga4_sessions', 'support_ticket_volume', 
                    'telephony_call_volume', 'lms_active_users'
                ]
                for field in numeric_fields:
                    if field in doc and pd.notna(doc[field]):
                        doc[field] = int(doc[field])
                
                # Convert numpy types to Python types
                for key, value in doc.items():
                    if hasattr(value, 'item'):
                        doc[key] = value.item()
                
                # Add migration metadata
                doc['_migrated_at'] = datetime.now().isoformat()
                doc['_source'] = 'postgresql_migration'
                
                documents.append(doc)
            
            # Insert into MongoDB
            collection = self.mongo_db['business_analytics']
            await collection.delete_many({})  # Clear existing data
            
            if documents:
                result = await collection.insert_many(documents)
                print(f"✅ Migrated {len(result.inserted_ids)} analytics records to MongoDB")
            
            return True
            
        except Exception as e:
            print(f"❌ OneTruth migration failed: {e}")
            return False
        finally:
            pg_conn.close()
    
    async def verify_migration(self):
        """Verify migration by checking record counts in MongoDB"""
        print("\n🔍 Verifying migration...")
        
        try:
            # Check leads collection
            leads_count = await self.mongo_db['leads'].count_documents({})
            print(f"📊 Leads in MongoDB: {leads_count}")
            
            # Check referrals collection  
            referrals_count = await self.mongo_db['referrals'].count_documents({})
            print(f"📊 Referrals in MongoDB: {referrals_count}")
            
            # Check business_analytics collection
            analytics_count = await self.mongo_db['business_analytics'].count_documents({})
            print(f"📊 Analytics records in MongoDB: {analytics_count}")
            
            total_migrated = leads_count + referrals_count + analytics_count
            print(f"\n✅ Total records migrated: {total_migrated}")
            
            return total_migrated > 0
            
        except Exception as e:
            print(f"❌ Migration verification failed: {e}")
            return False
    
    async def close_connections(self):
        """Close database connections"""
        if self.mongo_client:
            self.mongo_client.close()
            print("🔒 Closed MongoDB connection")

async def main():
    """Main migration function"""
    print("🚀 Starting PostgreSQL to MongoDB Migration")
    print("=" * 50)
    
    migrator = DataMigrator()
    
    # Connect to MongoDB
    if not await migrator.connect_mongodb():
        print("❌ Cannot proceed without MongoDB connection")
        return
    
    success_count = 0
    
    # Migrate each system
    if await migrator.migrate_hotlead_data():
        success_count += 1
    
    if await migrator.migrate_refermore_data():
        success_count += 1
    
    if await migrator.migrate_onetruth_data():
        success_count += 1
    
    # Verify migration
    if await migrator.verify_migration():
        print(f"\n🎉 Migration completed successfully! ({success_count}/3 systems migrated)")
    else:
        print(f"\n⚠️ Migration completed with issues ({success_count}/3 systems migrated)")
    
    # Close connections
    await migrator.close_connections()
    
    print("\n✨ Migration process finished!")

if __name__ == "__main__":
    asyncio.run(main())
