import os
from typing import List
from decouple import config
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings"""
    
    # API Settings
    API_V1_STR: str = "/api"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:5174",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:*",
        "http://host.docker.internal:*",
        "*",  # In production, you should replace this with specific domains
    ]
    
    # MongoDB Settings
    MONGO_URI: str = config("MONGO_URI", default="mongodb://localhost:27017")
    MONGO_DB: str = config("MONGO_DB", default="Lab2")

# Create global settings instance
settings = Settings()
