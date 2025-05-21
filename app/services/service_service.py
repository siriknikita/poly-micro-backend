from typing import List, Optional
from fastapi import HTTPException
from app.db.repositories.service_repository import ServiceRepository
from app.db.repositories.project_repository import ProjectRepository
from app.schemas.service import Service, ServiceCreate, ServiceUpdate

class ServiceService:
    """Service for microservice-related business logic"""
    
    def __init__(self, service_repository: ServiceRepository, project_repository: ProjectRepository):
        self.service_repository = service_repository
        self.project_repository = project_repository
    
    async def get_all_services(self) -> List[Service]:
        """Get all services across all projects"""
        services = await self.service_repository.get_all_services()
        return [Service(**service) for service in services]
    
    async def get_services_by_project(self, project_id: str) -> List[Service]:
        """Get all services for a specific project"""
        # Check if project exists
        project = await self.project_repository.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        services = await self.service_repository.get_services_by_project(project_id)
        return [Service(**service) for service in services]
    
    async def get_service_by_id(self, service_id: str) -> Service:
        """Get a service by ID"""
        service = await self.service_repository.get_service_by_id(service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        return Service(**service)
    
    async def create_service(self, service: ServiceCreate) -> Service:
        """Create a new service"""
        # Check if referenced project exists
        project = await self.project_repository.get_project_by_id(service.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Create service
        service_data = await self.service_repository.create_service(service)
        return Service(**service_data)
    
    async def update_service(self, service_id: str, service: ServiceUpdate) -> Service:
        """Update a service"""
        # Check if service exists
        existing_service = await self.service_repository.get_service_by_id(service_id)
        if not existing_service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # If project_id is being updated, check if the referenced project exists
        if service.project_id and service.project_id != existing_service.get("project_id"):
            project = await self.project_repository.get_project_by_id(service.project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
        
        # Update service
        updated_service = await self.service_repository.update_service(service_id, service)
        if not updated_service:
            raise HTTPException(status_code=404, detail="Failed to update service")
        
        return Service(**updated_service)
    
    async def delete_service(self, service_id: str) -> None:
        """Delete a service"""
        # Check if service exists
        existing_service = await self.service_repository.get_service_by_id(service_id)
        if not existing_service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Delete service
        deleted = await self.service_repository.delete_service(service_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Failed to delete service")
