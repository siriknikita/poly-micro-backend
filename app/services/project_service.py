from typing import List, Optional
from fastapi import HTTPException, Depends, Request
from app.db.repositories.project_repository import ProjectRepository
from app.schemas.project import Project, ProjectCreate, ProjectUpdate
from app.services.service_service import ServiceService

class ProjectService:
    """Service for project-related business logic"""
    
    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository
        self.service_service = None
    
    def get_service_service(self, request: Request = None) -> ServiceService:
        """Get the service service from the request"""
        print("Getting service service")
        if self.service_service is None:
            # Create ServiceService directly with repositories to avoid circular dependencies
            from app.db.database import get_database
            from app.db.repositories.service_repository import ServiceRepository
            
            print("Creating repositories directly")
            # Create repositories directly
            service_repository = ServiceRepository(get_database())
            
            print("Initializing service service directly")
            from app.services.service_service import ServiceService
            self.service_service = ServiceService(service_repository, self.project_repository)
            print(f"Service service initialized directly: {self.service_service}")
        return self.service_service
    
    async def get_all_projects(self, request: Request = None) -> List[Project]:
        """Get all projects with their microservices"""
        projects = await self.project_repository.get_all_projects()
        
        # Add microservices to each project
        result = []
        for project_data in projects:
            project_id = project_data["id"]
            # Get microservices for this project
            try:
                service_service = self.get_service_service(request)
                microservices = await service_service.get_services_by_project(project_id)
                # Create project with microservices
                project = Project(**project_data, microservices=microservices)
                result.append(project)
            except Exception as e:
                # If there's an error getting microservices, still return the project but without microservices
                print(f"Error fetching microservices for project {project_id}: {str(e)}")
                project = Project(**project_data)
                result.append(project)
                
        return result
    
    async def get_project_by_id(self, project_id: str, request: Request = None) -> Project:
        """Get a project by ID with its microservices"""
        print(f"Getting project by ID: {project_id}")
        project = await self.project_repository.get_project_by_id(project_id)
        if not project:
            print(f"Project not found: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")
        
        print(f"Project found: {project}")
            
        # Get microservices for this project
        try:
            print(f"Getting service_service for project {project_id}")
            service_service = self.get_service_service(request)
            print(f"Service service obtained: {service_service}")
            
            print(f"Fetching microservices for project {project_id}")
            microservices = await service_service.get_services_by_project(project_id)
            print(f"Microservices found: {len(microservices) if microservices else 'None'}, {microservices}")
            
            # Return project with microservices
            project_with_ms = Project(**project, microservices=microservices)
            print(f"Returning project with microservices: {project_with_ms}")
            return project_with_ms
        except Exception as e:
            # If there's an error getting microservices, still return the project but without microservices
            print(f"Error fetching microservices for project {project_id}: {str(e)}")
            print(f"Exception type: {type(e).__name__}")
            print(f"Exception traceback: {e.__traceback__}")
            return Project(**project)
    
    async def create_project(self, project: ProjectCreate, request: Request = None) -> Project:
        """Create a new project"""
        project_data = await self.project_repository.create_project(project)
        if not project_data:
            raise HTTPException(status_code=404, detail="Failed to create project")
        
        # A newly created project won't have microservices yet, but we use the same pattern
        # for consistency and to handle future cases where we might pre-populate microservices
        project_id = project_data["id"]
        try:
            service_service = self.get_service_service(request)
            microservices = await service_service.get_services_by_project(project_id)
            return Project(**project_data, microservices=microservices)
        except Exception as e:
            print(f"Error fetching microservices for new project {project_id}: {str(e)}")
            return Project(**project_data)
    
    async def update_project(self, project_id: str, project: ProjectUpdate, request: Request = None) -> Project:
        """Update a project"""
        # Check if project exists
        existing_project = await self.project_repository.get_project_by_id(project_id)
        if not existing_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Update project
        updated_project = await self.project_repository.update_project(project_id, project)
        if not updated_project:
            raise HTTPException(status_code=404, detail="Failed to update project")
        
        # Get microservices for the updated project
        try:
            service_service = self.get_service_service(request)
            microservices = await service_service.get_services_by_project(project_id)
            return Project(**updated_project, microservices=microservices)
        except Exception as e:
            print(f"Error fetching microservices for updated project {project_id}: {str(e)}")
            return Project(**updated_project)
    
    async def delete_project(self, project_id: str) -> None:
        """Delete a project"""
        # Check if project exists
        existing_project = await self.project_repository.get_project_by_id(project_id)
        if not existing_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Delete project
        deleted = await self.project_repository.delete_project(project_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Failed to delete project")
