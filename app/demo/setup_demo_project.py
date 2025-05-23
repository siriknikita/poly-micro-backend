"""
Setup script for creating a demo project and services in the Poly Micro Manager system.
This script will create the necessary database entries to make logs visible in the dashboard.
"""

import asyncio
from bson import ObjectId
from app.db.database import get_database
from app.services.project_service import ProjectService
from app.services.service_service import ServiceService
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.service_repository import ServiceRepository

async def create_demo_project(name="Demo Project", description="Project for logging demo"):
    """Create a demo project and return its ID"""
    # Set up repositories
    db = get_database()
    project_repo = ProjectRepository(db)
    
    # Set up service
    project_service = ProjectService(project_repo)
    
    # Check if project with this name already exists
    existing_projects = await project_repo.find_all({"name": name})
    if existing_projects:
        print(f"Project '{name}' already exists, using existing project")
        project = existing_projects[0]
        # Ensure we have a proper ID, prefer the MongoDB _id converted to string
        if '_id' in project:
            return str(project['_id'])
        elif 'id' in project:
            return project['id']
        else:
            print("WARNING: Project has no ID, creating a new project instead")
            # Will proceed to create a new project
    
    # Create project
    project_data = {
        "name": name,
        "description": description,
        "status": "active"
    }
    
    created_project = await project_repo.create(project_data)
    
    # Ensure we have a proper ID, prefer the MongoDB _id converted to string
    if '_id' in created_project:
        project_id = str(created_project['_id'])
    else:
        project_id = created_project.get("id")
        
    print(f"Created project '{name}' with ID: {project_id}")
    
    return project_id

async def create_demo_services(project_id, services):
    """Create demo services for the project"""
    # Set up repositories
    db = get_database()
    service_repo = ServiceRepository(db)
    project_repo = ProjectRepository(db)
    
    # Set up service
    service_service = ServiceService(service_repo, project_repo)
    
    service_ids = {}
    
    for service in services:
        # Check if service already exists
        existing_services = await service_repo.find_all({
            "name": service["name"],
            "project_id": project_id
        })
        
        if existing_services:
            print(f"Service '{service['name']}' already exists, using existing service")
            service_ids[service["id"]] = existing_services[0].get("id")
            continue
        
        # Create service
        service_data = {
            "name": service["name"],
            "description": f"Demo service: {service['name']}",
            "project_id": project_id,
            "status": "active",
            "url": service.get("url", "http://localhost:8000")
        }
        
        created_service = await service_repo.create(service_data)
        service_id = created_service.get("id")
        service_ids[service["id"]] = service_id
        
        print(f"Created service '{service['name']}' with ID: {service_id}")
    
    return service_ids

async def setup_demo():
    """Set up all demo data"""
    # Define services
    services = [
        {"id": "service_1", "name": "Auth Service", "url": "http://localhost:8001"},
        {"id": "service_2", "name": "User Service", "url": "http://localhost:8002"},
        {"id": "service_3", "name": "Order Service", "url": "http://localhost:8003"}
    ]
    
    # Create project
    project_id = await create_demo_project()
    
    # Create services
    service_ids = await create_demo_services(project_id, services)
    
    return {
        "project_id": project_id,
        "service_ids": service_ids
    }

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    demo_data = loop.run_until_complete(setup_demo())
    
    print("\nDemo Setup Complete!")
    print(f"Project ID: {demo_data['project_id']}")
    print("Service IDs:")
    for demo_id, actual_id in demo_data['service_ids'].items():
        print(f"  {demo_id} -> {actual_id}")
    
    print("\nYou can now run the logging demo with these IDs.")
