from typing import List, Optional
from fastapi import HTTPException
from app.db.repositories.service_repository import ServiceRepository
from app.db.repositories.project_repository import ProjectRepository
from app.schemas.service import Service, ServiceCreate, ServiceUpdate
from app.schemas.test_item import TestItem

class ServiceService:
    """Service for microservice-related business logic"""
    
    def __init__(self, service_repository: ServiceRepository, project_repository: ProjectRepository):
        print(f"Initializing ServiceService with: {service_repository}, {project_repository}")
        self.service_repository = service_repository
        self.project_repository = project_repository
        # Validate the repositories
        print(f"ServiceRepository type: {type(service_repository)}")
        print(f"ProjectRepository type: {type(project_repository)}")
    
    async def get_all_services(self) -> List[Service]:
        """Get all services across all projects"""
        services = await self.service_repository.get_all_services()
        return [Service(**service) for service in services]
    
    async def get_services_by_project(self, project_id: str) -> List[TestItem]:
        """Get all services for a specific project and convert them to TestItems"""
        print(f"ServiceService: Getting services for project {project_id}")
        
        try:
            # Validate project repository is accessible
            print(f"Project repository: {self.project_repository}, type: {type(self.project_repository)}")
            
            try:
                # Check if project exists - but don't fail if we can't verify
                if hasattr(self.project_repository, 'get_project_by_id'):
                    project = await self.project_repository.get_project_by_id(project_id)
                    if project:
                        print(f"ServiceService: Project found: {project}")
                    else:
                        print(f"ServiceService: Project not found: {project_id}")
            except Exception as e:
                print(f"Error checking project existence: {e}, but will continue")
            
            # Get services regardless of whether we could verify the project
            services = await self.service_repository.get_services_by_project(project_id)
            print(f"ServiceService: Raw services data: {services}")
            
            # If no services are found, just return an empty list
            if not services:
                print(f"No services found for project {project_id}")
                return []
                
            # Convert the real services to TestItems for the frontend
            result = []
            for service in services:
                try:
                    # Create a Service object first
                    service_obj = Service(**service)
                    print(f"ServiceService: Converted service: {service_obj}")
                    
                    # Create a TestItem from the service data
                    test_item_data = {
                        "id": service_obj.id,
                        "name": service_obj.name,
                        "type": "microservice",
                        "children": [],  # Empty children array
                        "projectId": project_id,
                        "status": service_obj.status or "offline",
                        "version": service_obj.version or "1.0.0",
                        "lastDeployed": service_obj.last_deployment
                    }
                    
                    # Create the TestItem object
                    test_item = TestItem(**test_item_data)
                    print(f"ServiceService: Created test item for service: {test_item}")
                    result.append(test_item)
                except Exception as e:
                    print(f"ServiceService: Error converting service: {service} - {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            print(f"ServiceService: Returning {len(result)} test items")
            return result
            
        except Exception as e:
            print(f"Unexpected error in get_services_by_project: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return an empty list to avoid breaking the API
            return []
    
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
