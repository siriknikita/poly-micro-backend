from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
from datetime import datetime, timedelta
import random

from app.api.routes import api_router
from app.db.database import get_database
from app.core.config import settings
from app.core.sample_data import generate_sample_data

app = FastAPI(
    title="Poly Micro Manager API",
    description="API for managing microservices architecture",
    version="1.0.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Poly Micro Manager API",
        "version": "1.0.0",
        "documentation": "/docs",
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Startup event to initialize sample data if needed
@app.on_event("startup")
async def startup_event():
    db = get_database()
    # Check if collections are empty and populate with sample data if needed
    if await db.projects.count_documents({}) == 0:
        await generate_sample_data()
        print("Sample data generated successfully")
