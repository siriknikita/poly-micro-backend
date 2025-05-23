"""Configuration for pytest fixtures."""
import os
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
from fastapi import FastAPI
from mongomock_motor import AsyncMongoMockClient

from app.main import app as fastapi_app
from app.db.database import get_database
from app.core.sample_data import generate_sample_data
from app.db.repositories.log_repository import LogRepository


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def app():
    """Get FastAPI application for testing."""
    # Override the database dependency to use in-memory MongoDB
    async def get_test_database():
        return AsyncMongoMockClient()["test_db"]

    # Override the get_database dependency in the app
    fastapi_app.dependency_overrides[get_database] = get_test_database
    
    yield fastapi_app


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Get test database instance."""
    db = AsyncMongoMockClient()["test_db"]
    yield db
    
    # Clean up the database after each test
    collections = await db.list_collection_names()
    for collection in collections:
        await db[collection].delete_many({})


@pytest_asyncio.fixture(scope="function")
async def populate_test_db(test_db):
    """Populate test database with sample data."""
    # Override the get_database function for sample data generation
    original_get_db = get_database
    
    async def test_get_database():
        return test_db
    
    # Override the dependency
    fastapi_app.dependency_overrides[get_database] = test_get_database
    
    # Generate sample data
    await generate_sample_data()
    
    yield
    
    # Restore original dependency
    fastapi_app.dependency_overrides[get_database] = original_get_db


@pytest_asyncio.fixture(scope="function")
async def client(app, populate_test_db):
    """Get AsyncClient for making HTTP requests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
def log_repository(test_db):
    """Create a LogRepository instance for testing."""
    return LogRepository(test_db)
