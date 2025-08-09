from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: AsyncIOMotorClient = None
    database = None

# Database instance
db = Database()

async def connect_to_mongo():
    """Create database connection"""
    db.client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    db.database = db.client[os.getenv("DATABASE_NAME", "odin_school_db")]
    print("Connected to MongoDB")

async def close_mongo_connection():
    """Close database connection"""
    db.client.close()
    print("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return db.database
