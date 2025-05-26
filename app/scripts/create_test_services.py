#!/usr/bin/env python3
"""
Script to create test microservices for existing projects
"""
import asyncio
import sys
import os
from bson.objectid import ObjectId

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.db.database import get_database
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.service_repository import ServiceRepository
from app.schemas.service import ServiceCreate

async def create_test_services():
    """Create test microservices for each existing project"""
    db = get_database()
    project_repository = ProjectRepository(db)
    service_repository = ServiceRepository(db)
    
    # Get all projects
    projects = await project_repository.get_all_projects()
    
    if not projects:
        print("No projects found. Please create some projects first.")
        return
    
    print(f"Found {len(projects)} projects")
    
    # For each project, create some test microservices
    for project in projects:
        project_id = project.get("id") or str(project.get("_id"))
        project_name = project.get("name")
        
        print(f"Creating services for project: {project_name} (ID: {project_id})")
        
        # Check if project already has services
        existing_services = await service_repository.get_services_by_project(project_id)
        if existing_services:
            print(f"  Project already has {len(existing_services)} services. Skipping.")
            continue
        
        # Create a few test microservices
        services = [
            {
                "name": "User Service",
                "project_id": project_id,
                "status": "online",
                "health": "Healthy",
                "port": 8080,
                "url": "http://user-service:8080",
                "version": "1.0.0",
                "uptime": "3d 4h",
                "last_deployment": "2025-05-20T12:00:00Z"
            },
            {
                "name": "Authentication Service",
                "project_id": project_id,
                "status": "online",
                "health": "Healthy",
                "port": 8081,
                "url": "http://auth-service:8081",
                "version": "1.1.2",
                "uptime": "2d 7h",
                "last_deployment": "2025-05-22T15:30:00Z"
            },
            {
                "name": "Order Service",
                "project_id": project_id,
                "status": "online",
                "health": "Warning",
                "port": 8082,
                "url": "http://order-service:8082",
                "version": "0.9.5",
                "uptime": "1d 2h",
                "last_deployment": "2025-05-24T10:15:00Z"
            }
        ]
        
        for service_data in services:
            try:
                service = ServiceCreate(**service_data)
                created_service = await service_repository.create_service(service)
                print(f"  Created service: {created_service['name']} (ID: {created_service.get('id') or created_service.get('_id')})")
            except Exception as e:
                print(f"  Error creating service {service_data['name']}: {str(e)}")
    
    print("Test services creation completed!")

if __name__ == "__main__":
    asyncio.run(create_test_services())
