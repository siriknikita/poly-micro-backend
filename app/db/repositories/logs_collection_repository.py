"""
Repository for interacting with the poly_micro_logs collection in MongoDB.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from bson import ObjectId
from .base_repository import BaseRepository
from app.schemas.log import LogCreate, LogUpdate, Severity
from app.models.log import LogEntry


class LogsCollectionRepository(BaseRepository):
    """Repository for log-related database operations on the poly_micro_logs collection"""
    
    def __init__(self, db):
        super().__init__(db, "poly_micro_logs")
    
    async def get_all_logs(self, project_id: Optional[str] = None, service_id: Optional[str] = None, 
                          severity: Optional[Severity] = None, test_id: Optional[str] = None, 
                          func_id: Optional[str] = None, source: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all logs with optional filtering"""
        filter_query = {}
        if project_id:
            filter_query["project_id"] = project_id
        if service_id:
            filter_query["service_id"] = service_id
        if severity:
            filter_query["severity"] = severity
        if test_id:
            filter_query["test_id"] = test_id
        if func_id:
            filter_query["func_id"] = func_id
        if source:
            filter_query["source"] = source
            
        # Get logs sorted by timestamp descending (newest first)
        logs = await self.find_all(filter_query, sort=[("timestamp", -1)])
        
        # Convert ObjectId to string for each log
        for log in logs:
            if "_id" in log:
                log["id"] = str(log["_id"])
                del log["_id"]
        
        return logs
    
    async def get_log_by_id(self, log_id: str) -> Optional[Dict[str, Any]]:
        """Get a log by ID"""
        try:
            # Try to convert string to ObjectId
            object_id = ObjectId(log_id)
            log = await self.collection.find_one({"_id": object_id})
            if log:
                log["id"] = str(log["_id"])
                del log["_id"]
            return log
        except:
            # If not a valid ObjectId, try to find by string id
            return await self.find_one(log_id)
    
    async def create_log(self, log: Union[LogCreate, LogEntry]) -> Dict[str, Any]:
        """Create a new log entry"""
        # Generate log data
        if isinstance(log, LogEntry):
            log_dict = log.to_dict()
        else:
            log_dict = log.model_dump()
            
        # Set timestamp if not provided
        if not log_dict.get("timestamp"):
            log_dict["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insert into collection
        result = await self.collection.insert_one(log_dict)
        
        # Get the inserted document
        created_log = await self.collection.find_one({"_id": result.inserted_id})
        if created_log:
            created_log["id"] = str(created_log["_id"])
            del created_log["_id"]
        
        return created_log
    
    async def update_log(self, log_id: str, log: Union[LogUpdate, LogEntry]) -> Optional[Dict[str, Any]]:
        """Update a log entry"""
        # Only update provided fields
        if isinstance(log, LogEntry):
            update_data = log.to_dict()
        else:
            update_data = {k: v for k, v in log.model_dump().items() if v is not None}
            
        if not update_data:
            return await self.get_log_by_id(log_id)  # Return current log if no updates
        
        try:
            # Try to convert string to ObjectId
            object_id = ObjectId(log_id)
            result = await self.collection.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            if result.modified_count > 0:
                return await self.get_log_by_id(log_id)
            return None
        except:
            # If not a valid ObjectId, try to update by string id
            return await self.update(log_id, update_data)
    
    async def delete_log(self, log_id: str) -> bool:
        """Delete a log entry"""
        try:
            # Try to convert string to ObjectId
            object_id = ObjectId(log_id)
            result = await self.collection.delete_one({"_id": object_id})
            return result.deleted_count > 0
        except:
            # If not a valid ObjectId, try to delete by string id
            return await self.delete(log_id)
        
    async def get_logs_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all logs for a specific project"""
        return await self.get_all_logs(project_id=project_id)
        
    async def get_logs_by_service(self, service_id: str) -> List[Dict[str, Any]]:
        """Get all logs for a specific service"""
        return await self.get_all_logs(service_id=service_id)
