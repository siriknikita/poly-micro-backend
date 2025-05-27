import motor.motor_asyncio
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
class Database:
    client = None
    db = None

    @classmethod
    def get_client(cls):
        if cls.client is None:
            mongo_uri = os.getenv("MONGO_URI")
            if not mongo_uri:
                raise ValueError("MONGO_URI environment variable is not set")
            cls.client = motor.motor_asyncio.AsyncIOMotorClient(
                mongo_uri, server_api=ServerApi('1')
            )
        return cls.client

    @classmethod
    def get_db(cls):
        if cls.db is None:
            cls.db = cls.get_client().poly_micro_manager
        return cls.db

# Get DB instance
def get_database():
    return Database.get_db()
