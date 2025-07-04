from typing import List, Dict, Any, Optional
from bson import ObjectId
from .base_repository import BaseRepository
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.core.cache import cached, invalidate_cache

class ServiceRepository(BaseRepository):
    """Repository for service-related database operations"""
    
    def __init__(self, db):
        super().__init__(db, "poly_micro_services")
    
    @cached(ttl=300, prefix="services:all")
    async def get_all_services(self) -> List[Dict[str, Any]]:
        """Get all services with caching"""
        services = await self.find_all()
        # Convert _id to id for response compatibility
        for service in services:
            if "_id" in service:
                service["id"] = str(service["_id"])
        return services
    
    @cached(ttl=300, prefix="services:by_project")
    async def get_services_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all services for a specific project with caching"""
        try:
            # Try to convert project_id to ObjectId
            print(f"Trying to query services with ObjectId for project: {project_id}")
            services = await self.find_all({"project_id": project_id})
            if services:
                print(f"Found {len(services)} services using ObjectId for project: {project_id}")
            else:
                # Fallback to string ID if no results with ObjectId
                print(f"No services found with ObjectId, trying string ID for project: {project_id}")
                services = await self.find_all({"project_id": project_id})
                print(f"Found {len(services)} services using string ID for project: {project_id}")
        except Exception as e:
            # If ObjectId conversion fails, use string ID
            print(f"Failed to convert to ObjectId: {str(e)}, using string ID for project: {project_id}")
            services = await self.find_all({"project_id": project_id})
            print(f"Found {len(services)} services using string ID for project: {project_id}")
            
        # Convert _id to id for response compatibility
        for service in services:
            if "_id" in service:
                service["id"] = str(service["_id"])
        return services
    
    @cached(ttl=300, prefix="services:by_id")
    async def get_service_by_id(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get a service by ID with caching"""
        service = await self.find_one(service_id)
        if service and "_id" in service:
            service["id"] = str(service["_id"])
        return service
    
    @invalidate_cache(prefix="services")
    async def create_service(self, service: ServiceCreate) -> Dict[str, Any]:
        """Create a new service and invalidate cache"""
        # Use dict() for Pydantic v1 compatibility
        service_data = service.dict() if hasattr(service, 'dict') else service
        result = await self.collection.insert_one(service_data)
        
        # Add ID to the response
        service_data["id"] = str(result.inserted_id)
        return service_data
    
    @invalidate_cache(prefix="services")
    async def update_service(self, service_id: str, service: ServiceUpdate) -> Optional[Dict[str, Any]]:
        """Update a service and invalidate cache"""
        # Only update provided fields - use dict() for Pydantic v1 compatibility
        update_data = {k: v for k, v in service.dict().items() if v is not None}
        if not update_data:
            return await self.get_service_by_id(service_id)  # Return current service if no updates
        
        try:
            await self.collection.update_one({"_id": ObjectId(service_id)}, {"$set": update_data})
            return await self.get_service_by_id(service_id)
        except:
            await self.collection.update_one({"id": service_id}, {"$set": update_data})
            return await self.get_service_by_id(service_id)
    
    @invalidate_cache(prefix="services")
    async def delete_service(self, service_id: str) -> bool:
        """Delete a service and invalidate cache"""
        return await self.delete(service_id)
    
    @cached(ttl=60, prefix="services:exists")
    async def check_service_exists(self, project_id: str, service_name: str) -> bool:
        """Check if a service exists for the given project with short-lived caching"""
        print("Checking service exists for project", project_id, "and service", service_name)
        print('All services', await self.get_services_by_project(project_id))
        
        try:
            # Try with ObjectId first
            service = await self.collection.find_one({"project_id": ObjectId(project_id), "name": service_name})
            if service:
                return True
        except:
            pass
            
        # Fallback to string ID
        service = await self.collection.find_one({"project_id": project_id, "name": service_name})
        return service is not None
