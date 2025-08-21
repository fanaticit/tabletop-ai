# app/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.config import settings

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    try:
        print(f"Connecting to MongoDB...")
        db.client = AsyncIOMotorClient(settings.mongodb_uri)
        db.database = db.client[settings.database_name]
        
        # Test connection
        await db.client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        print("Please check your MONGODB_URI in .env file")
        print("Example: MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/")
        # Don't raise in basic version - let API start anyway
        print("API will start without database connection for now...")

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")

def get_database():
    return db.database