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
        "*",  # Allow all origins in development
        "http://localhost",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8000",
        "tauri://localhost", 
        "tauri://127.0.0.1"
    ]
    
    # MongoDB Settings
    MONGO_URI: str = config("MONGO_URI", default="mongodb://localhost:27017")
    MONGO_DB: str = config("MONGO_DB", default="Lab2")

# Create global settings instance
settings = Settings()
