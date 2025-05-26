#!/usr/bin/env python3
"""
Demo Setup Script for Poly Micro Manager

This script creates a demo project with sample services, users, and
test data in the database to showcase the functionality of the application.

Run this script with:
python setup_demo.py
"""

import asyncio
import json
import os
import sys
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the current directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import necessary app modules
from app.core.config import settings
from app.db.database import get_database
from app.services.auth_service import AuthService
from app.services.project_service import ProjectService
from app.services.service_service import ServiceService
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.service_repository import ServiceRepository
from app.schemas.project import ProjectCreate
from app.schemas.service import ServiceCreate
from app.schemas.user import UserCreate

# Configure absolute path to the demo project
DEMO_PROJECT_PATH = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "demo-project"

# Demo data
DEMO_USER = {
    "email": "demo@example.com",
    "password": "demo123",
    "username": "demo_user",
    "full_name": "Demo User",
}

DEMO_PROJECT = {
    "name": "Demo Project",
    "description": "A demo project showcasing microservices and test discovery",
    "path": str(DEMO_PROJECT_PATH),
    "tests_dir_path": "tests"
}

DEMO_SERVICES = [
    {
        "name": "x-service",
        "description": "User authentication and management service",
        "url": "http://localhost:8001",
        "port": 8001,
        "status": "Running",
        "health": "Healthy",
        "version": "1.0.0",
        "uptime": "2h 15m",
        "last_deployment": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    },
    {
        "name": "y-service",
        "description": "Product catalog and management service",
        "url": "http://localhost:8002",
        "port": 8002,
        "status": "Running",
        "health": "Healthy",
        "version": "1.0.0",
        "uptime": "2h 15m",
        "last_deployment": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }
]


async def ensure_user_exists(user_repo: UserRepository) -> str:
    """Ensure demo user exists and return user ID."""
    print(f"Looking for demo user: {DEMO_USER['email']}...")
    user = await user_repo.get_user_by_email(DEMO_USER["email"])
    
    if not user:
        print("Creating demo user...")
        user_create = UserCreate(
            email=DEMO_USER["email"],
            username=DEMO_USER["username"],
            password=DEMO_USER["password"],
            full_name=DEMO_USER["full_name"]
        )
        # Convert Pydantic model to dict before inserting
        user_dict = user_create.dict()
        user = await user_repo.create(user_dict)
        # Handle either dictionary or object response
        if isinstance(user, dict):
            user_id = user.get('_id', user.get('id', 'unknown'))
        else:
            user_id = getattr(user, 'id', 'unknown')
        print(f"Demo user created with ID: {user_id}")
    else:
        # Handle either dictionary or object response
        if isinstance(user, dict):
            user_id = user.get('_id', user.get('id', 'unknown'))
        else:
            user_id = getattr(user, 'id', 'unknown')
        print(f"Demo user already exists with ID: {user_id}")
    
    return user_id


async def ensure_project_exists(project_service: ProjectService) -> str:
    """Ensure demo project exists and return project ID."""
    print(f"Looking for demo project: {DEMO_PROJECT['name']}...")
    projects = await project_service.get_all_projects()
    
    # Check if project exists by comparing name
    existing_project = next((p for p in projects if (isinstance(p, dict) and p.get('name') == DEMO_PROJECT["name"]) or 
                              (hasattr(p, 'name') and p.name == DEMO_PROJECT["name"])), None)
    
    if not existing_project:
        print("Creating demo project...")
        project_create = ProjectCreate(
            name=DEMO_PROJECT["name"],
            description=DEMO_PROJECT["description"],
            path=DEMO_PROJECT["path"],
            tests_dir_path=DEMO_PROJECT["tests_dir_path"]
        )
        # Convert Pydantic model to dict for older Pydantic version
        project_dict = project_create.dict()
        # Use the dict for creation
        project = await project_service.create_project(project_dict)
        # Handle either dictionary or object response
        if isinstance(project, dict):
            project_id = project.get('_id', project.get('id', 'unknown'))
        else:
            project_id = getattr(project, 'id', 'unknown')
        print(f"Demo project created with ID: {project_id}")
        return project_id
    else:
        # Handle either dictionary or object response
        if isinstance(existing_project, dict):
            project_id = existing_project.get('_id', existing_project.get('id', 'unknown'))
        else:
            project_id = getattr(existing_project, 'id', 'unknown')
        print(f"Demo project already exists with ID: {project_id}")
        return project_id


async def ensure_services_exist(service_repo: ServiceRepository, project_id: str) -> List[str]:
    """Ensure demo services exist and return service IDs."""
    print("Checking for demo services...")
    
    # Get services collection
    services_collection = service_repo.collection
    
    # Find services for the project directly from MongoDB
    cursor = services_collection.find({"project_id": project_id})
    existing_services = []
    async for service in cursor:
        existing_services.append(service)
        
    service_ids = []
    
    # Check for existing services and create if needed
    for demo_service in DEMO_SERVICES:
        # Check if service exists by comparing name
        existing_service = next((s for s in existing_services if s.get('name') == demo_service["name"]), None)
        
        if not existing_service:
            print(f"Creating service: {demo_service['name']}...")
            # Prepare service data for direct insertion
            service_data = {
                "name": demo_service["name"],
                "description": demo_service["description"],
                "project_id": project_id,
                "url": demo_service["url"],
                "port": demo_service["port"],
                "status": demo_service["status"],
                "health": demo_service["health"],
                "version": demo_service["version"],
                "uptime": demo_service["uptime"],
                "last_deployment": demo_service["last_deployment"]
            }
            
            # Insert directly into MongoDB
            result = await services_collection.insert_one(service_data)
            service_id = str(result.inserted_id)
            print(f"Service {demo_service['name']} created with ID: {service_id}")
            service_ids.append(service_id)
        else:
            service_id = str(existing_service.get('_id'))
            print(f"Service {demo_service['name']} already exists with ID: {service_id}")
            service_ids.append(service_id)
    
    return service_ids


async def create_test_data(db, service_ids, project_id):
    """Create test data for the demo services."""
    print("\nCreating test data for services...")
    
    # Get the test collection
    test_collection = db["tests"]
    
    # Sample test data for each service
    for idx, service_id in enumerate(service_ids[-2:]):  # Only for the newly created x-service and y-service
        service_name = "x-service" if idx == 0 else "y-service"
        
        # Create 3 tests for each service
        for test_num in range(1, 4):
            test_data = {
                "name": f"Test {test_num} for {service_name}",
                "description": f"Automated test case #{test_num} for {service_name}",
                "service_id": service_id,
                "project_id": project_id,
                "status": "Passed" if test_num < 3 else "Failed",
                "last_run": datetime.datetime.now().isoformat(),
                "duration": f"{test_num * 0.5:.1f}s",
                "type": "Unit Test" if test_num == 1 else "Integration Test" if test_num == 2 else "E2E Test"
            }
            
            # Check if test already exists
            existing_test = await test_collection.find_one({
                "name": test_data["name"],
                "service_id": service_id
            })
            
            if not existing_test:
                result = await test_collection.insert_one(test_data)
                print(f"Created test '{test_data['name']}' with ID: {result.inserted_id}")
            else:
                print(f"Test '{test_data['name']}' already exists")
    
    print("Test data creation complete")


async def main():
    """Main function to set up all demo data."""
    print("=" * 50)
    print("POLY MICRO MANAGER - DEMO SETUP")
    print("=" * 50)
    print()
    
    # Initialize database connection
    print("\nConnecting to database...")
    db = get_database()
    
    # Initialize repositories
    user_repo = UserRepository(db)
    project_repo = ProjectRepository(db)
    service_repo = ServiceRepository(db)
    
    # Initialize services
    auth_service = AuthService(user_repo)
    project_service = ProjectService(project_repo)
    service_service = ServiceService(service_repo, project_repo)
    
    # Setup demo user
    user_id = await ensure_user_exists(user_repo)
    
    # Setup demo project
    project_id = await ensure_project_exists(project_service)
    
    # Setup demo services
    service_ids = await ensure_services_exist(service_repo, project_id)
    
    # Create test data for services
    await create_test_data(db, service_ids, project_id)
    
    print("\n" + "=" * 50)
    print("DEMO SETUP COMPLETE")
    print("=" * 50)
    print(f"\nDemo User: {DEMO_USER['email']} (Password: {DEMO_USER['password']})")
    print(f"Demo Project ID: {project_id}")
    print(f"Demo Service IDs: {', '.join(service_ids)}")
    print("\nYou can now showcase the application to your teacher!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
