from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from .base_repository import BaseRepository
from app.schemas.log import LogCreate, LogUpdate, Severity
from app.models.log import LogEntry
from app.core.cache import cached, invalidate_cache

class LogRepository(BaseRepository):
    """Repository for log-related database operations"""
    
    def __init__(self, db):
        super().__init__(db, "logs")
    
    # Cache is applied based on combined parameters so different filter combinations are cached separately
    @cached(ttl=300, prefix="logs:filtered")
    async def get_all_logs(self, project_id: Optional[str] = None, service_id: Optional[str] = None, severity: Optional[Severity] = None, test_id: Optional[str] = None, func_id: Optional[str] = None, source: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all logs with optional filtering and caching"""
        print("project_id:", project_id)
        print("service_id:", service_id)
        print("severity:", severity)
        print("test_id:", test_id)
        print("func_id:", func_id)
        print("source:", source)
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
            
        return await self.find_all(filter_query)
    
    @cached(ttl=300, prefix="logs:by_id")
    async def get_log_by_id(self, log_id: str) -> Optional[Dict[str, Any]]:
        """Get a log by ID with caching"""
        return await self.find_one(log_id)
    
    @invalidate_cache(prefix="logs")
    async def create_log(self, log: Union[LogCreate, LogEntry]) -> Dict[str, Any]:
        """Create a new log entry with auto-generated ID and timestamp and invalidate cache"""
        # Generate log data with timestamp if not provided
        if isinstance(log, LogEntry):
            log_dict = log.to_dict()
        else:
            log_dict = log.model_dump()
            
        if not log_dict.get("timestamp"):
            log_dict["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate a new ID
        all_logs = await self.find_all(limit=1000)
        max_id = 0
        for l in all_logs:
            try:
                l_id = int(l.get("id", 0))
                if l_id > max_id:
                    max_id = l_id
            except ValueError:
                continue
        
        # Create new log with incremented ID
        new_id = str(max_id + 1)
        log_dict["id"] = new_id
        
        return await self.create(log_dict)
    
    @invalidate_cache(prefix="logs")
    async def update_log(self, log_id: str, log: Union[LogUpdate, LogEntry]) -> Optional[Dict[str, Any]]:
        """Update a log entry and invalidate cache"""
        # Only update provided fields
        if isinstance(log, LogEntry):
            update_data = log.to_dict()
        else:
            update_data = {k: v for k, v in log.model_dump().items() if v is not None}
            
        if not update_data:
            return await self.find_one(log_id)  # Return current log if no updates
        
        return await self.update(log_id, update_data)
    
    @invalidate_cache(prefix="logs")
    async def delete_log(self, log_id: str) -> bool:
        """Delete a log entry and invalidate cache"""
        return await self.delete(log_id)
        
    @cached(ttl=300, prefix="logs:by_project")
    async def get_logs_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all logs for a specific project with caching"""
        return await self.find_all({"project_id": project_id})
        
    @cached(ttl=300, prefix="logs:by_service")
    async def get_logs_by_service(self, service_id: str) -> List[Dict[str, Any]]:
        """Get all logs for a specific service with caching"""
        return await self.find_all({"service_id": service_id})
