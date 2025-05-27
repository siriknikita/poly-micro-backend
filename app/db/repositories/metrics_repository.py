from typing import List, Dict, Any, Optional
from bson import ObjectId
from .base_repository import BaseRepository
from app.schemas.metrics import CPUEntryCreate, CPUEntryUpdate, CPUDataCreate
from app.core.cache import cached, invalidate_cache

class MetricsRepository(BaseRepository):
    """Repository for metrics-related database operations"""
    
    def __init__(self, db):
        super().__init__(db, "poly_micro_metrics")
    
    @cached(ttl=300, prefix="metrics:all")
    async def get_all_cpu_data(self) -> List[Dict[str, Any]]:
        """Get all CPU metrics data with caching"""
        cpu_data = await self.find_all()
        # Convert _id to id for response compatibility
        for entry in cpu_data:
            if "_id" in entry:
                entry["id"] = str(entry["_id"])
        return cpu_data
    
    @cached(ttl=300, prefix="metrics:by_project")
    async def get_cpu_data_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        """Get CPU metrics data for a specific project with caching"""
        cpu_data = await self.find_all({"project_id": project_id})
        # Convert _id to id for response compatibility
        for entry in cpu_data:
            if "_id" in entry:
                entry["id"] = str(entry["_id"])
        return cpu_data
    
    @cached(ttl=300, prefix="metrics:by_service")
    async def get_cpu_data_by_service(self, service_name: str) -> List[Dict[str, Any]]:
        """Get CPU metrics data for a specific service with caching"""
        cpu_data = await self.find_all({"service_name": service_name})
        # Convert _id to id for response compatibility
        for entry in cpu_data:
            if "_id" in entry:
                entry["id"] = str(entry["_id"])
        return cpu_data
    
    @cached(ttl=300, prefix="metrics:entry_by_id")
    async def get_cpu_entry_by_id(self, cpu_entry_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific CPU metrics entry by ID with caching"""
        cpu_entry = await self.find_one(cpu_entry_id)
        if cpu_entry and "_id" in cpu_entry:
            cpu_entry["id"] = str(cpu_entry["_id"])
        return cpu_entry
    
    async def create_cpu_entry(self, cpu_entry: CPUEntryCreate) -> Dict[str, Any]:
        """Create a new CPU metrics entry"""
        cpu_entry_dict = cpu_entry.model_dump()
        result = await self.collection.insert_one(cpu_entry_dict)
        
        # Add ID to the response
        cpu_entry_dict["id"] = str(result.inserted_id)
        return cpu_entry_dict
    
    async def update_cpu_entry(self, cpu_entry_id: str, cpu_entry: CPUEntryUpdate) -> Optional[Dict[str, Any]]:
        """Update a CPU metrics entry"""
        # Only update provided fields
        update_data = {k: v for k, v in cpu_entry.model_dump().items() if v is not None}
        if not update_data:
            return await self.get_cpu_entry_by_id(cpu_entry_id)  # Return current entry if no updates
        
        try:
            await self.collection.update_one({"_id": ObjectId(cpu_entry_id)}, {"$set": update_data})
            return await self.get_cpu_entry_by_id(cpu_entry_id)
        except:
            await self.collection.update_one({"id": cpu_entry_id}, {"$set": update_data})
            return await self.get_cpu_entry_by_id(cpu_entry_id)
    
    async def delete_cpu_entry(self, cpu_entry_id: str) -> bool:
        """Delete a CPU metrics entry"""
        return await self.delete(cpu_entry_id)
    
    async def add_cpu_data_point(self, cpu_entry_id: str, cpu_data: CPUDataCreate) -> Optional[Dict[str, Any]]:
        """Add a new data point to an existing CPU metrics entry"""
        # Add the new data point
        new_data_point = cpu_data.model_dump()
        
        try:
            await self.collection.update_one(
                {"_id": ObjectId(cpu_entry_id)},
                {"$push": {"data": new_data_point}}
            )
            return await self.get_cpu_entry_by_id(cpu_entry_id)
        except:
            await self.collection.update_one(
                {"id": cpu_entry_id},
                {"$push": {"data": new_data_point}}
            )
            return await self.get_cpu_entry_by_id(cpu_entry_id)
