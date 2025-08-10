from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: AsyncIOMotorClient | None = None
    database = None

# Database instance
db = Database()

async def connect_to_mongo():
    """Create database connection (non-fatal if unavailable)."""
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DATABASE_NAME", "odin_school_db")
    try:
        db.client = AsyncIOMotorClient(mongo_url)
        db.database = db.client[db_name]
        # Optional lightweight ping to verify server availability without failing app startup
        try:
            await db.client.admin.command("ping")
            print("Connected to MongoDB")
        except Exception as ping_err:
            # Database is not reachable right now; proceed but warn
            print(f"MongoDB not reachable yet: {ping_err}")
    except Exception as e:
        # Ensure attributes remain None on failure
        db.client = None
        db.database = None
        print(f"Failed to initialize MongoDB client: {e}")

async def close_mongo_connection():
    """Close database connection safely."""
    try:
        if db.client is not None:
            db.client.close()
            print("Disconnected from MongoDB")
    except Exception as e:
        print(f"Error during MongoDB disconnect: {e}")

def get_database():
    """Get database instance or None if not connected."""
    return db.database
