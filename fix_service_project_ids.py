#!/usr/bin/env python
"""
Fix Service Project IDs

This script updates any service in the database that has a null project_id.
It associates these services with the correct project.
"""

import asyncio
import os
from dotenv import load_dotenv
from bson import ObjectId
from app.db.database import get_database
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.service_repository import ServiceRepository

# Load environment variables
load_dotenv()

async def fix_service_project_ids():
    """Find and fix services with null project_id"""
    # Set up database connection
    db = get_database()
    
    # Create repositories
    project_repo = ProjectRepository(db)
    service_repo = ServiceRepository(db)
    
    # Get the Demo Project (should exist)
    demo_projects = await project_repo.find_all({"name": "Demo Project"})
    if not demo_projects:
        print("Error: Demo Project not found. Please run setup_demo first.")
        return
    
    project = demo_projects[0]
    # Ensure we have a proper ID
    project_id = str(project.get("_id", project.get("id")))
    
    print(f"Found Demo Project with ID: {project_id}")
    
    # Find services with null project_id
    null_services = await service_repo.find_all({"project_id": None})
    print(f"Found {len(null_services)} services with null project_id")
    
    # Update each service
    for service in null_services:
        service_id = str(service.get("_id", service.get("id")))
        service_name = service.get("name", "Unknown Service")
        
        print(f"Fixing service '{service_name}' (ID: {service_id})")
        
        # Update the service
        update_result = await service_repo.update(service_id, {"project_id": project_id})
        if update_result:
            print(f"  ✓ Updated successfully")
        else:
            print(f"  ✗ Update failed")
    
    print("\nFixed project_id for all affected services.")

if __name__ == "__main__":
    print("Starting project_id fix...")
    asyncio.run(fix_service_project_ids())
    print("Done.")
