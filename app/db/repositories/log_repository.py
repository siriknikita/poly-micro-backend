from typing import List, Dict, Any, Optional
from datetime import datetime
from .base_repository import BaseRepository
from app.schemas.log import LogCreate, LogUpdate, Severity

class LogRepository(BaseRepository):
    """Repository for log-related database operations"""
    
    def __init__(self, db):
        super().__init__(db, "logs")
    
    async def get_all_logs(self, service: Optional[str] = None, severity: Optional[Severity] = None) -> List[Dict[str, Any]]:
        """Get all logs with optional filtering"""
        filter_query = {}
        if service:
            filter_query["service"] = service
        if severity:
            filter_query["severity"] = severity.value
            
        return await self.find_all(filter_query)
    
    async def get_log_by_id(self, log_id: str) -> Optional[Dict[str, Any]]:
        """Get a log by ID"""
        return await self.find_one(log_id)
    
    async def create_log(self, log: LogCreate) -> Dict[str, Any]:
        """Create a new log entry with auto-generated ID and timestamp"""
        # Generate log data with timestamp if not provided
        log_dict = log.dict()
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
    
    async def update_log(self, log_id: str, log: LogUpdate) -> Optional[Dict[str, Any]]:
        """Update a log entry"""
        # Only update provided fields
        update_data = {k: v for k, v in log.dict().items() if v is not None}
        if not update_data:
            return await self.find_one(log_id)  # Return current log if no updates
        
        return await self.update(log_id, update_data)
    
    async def delete_log(self, log_id: str) -> bool:
        """Delete a log entry"""
        return await self.delete(log_id)
