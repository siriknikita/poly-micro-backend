from typing import List, Optional
from fastapi import HTTPException
from app.db.repositories.log_repository import LogRepository
from app.schemas.log import Log, LogCreate, LogUpdate, Severity

class LogService:
    """Service for log-related business logic"""
    
    def __init__(self, log_repository: LogRepository):
        self.log_repository = log_repository
    
    async def get_all_logs(self, service: Optional[str] = None, severity: Optional[Severity] = None) -> List[Log]:
        """Get all logs with optional filtering"""
        logs = await self.log_repository.get_all_logs(service, severity)
        return [Log(**log) for log in logs]
    
    async def get_log_by_id(self, log_id: str) -> Log:
        """Get a log by ID"""
        log = await self.log_repository.get_log_by_id(log_id)
        if not log:
            raise HTTPException(status_code=404, detail="Log not found")
        return Log(**log)
    
    async def create_log(self, log: LogCreate) -> Log:
        """Create a new log entry"""
        log_data = await self.log_repository.create_log(log)
        return Log(**log_data)
    
    async def update_log(self, log_id: str, log: LogUpdate) -> Log:
        """Update a log entry"""
        # Check if log exists
        existing_log = await self.log_repository.get_log_by_id(log_id)
        if not existing_log:
            raise HTTPException(status_code=404, detail="Log not found")
        
        # Update log
        updated_log = await self.log_repository.update_log(log_id, log)
        if not updated_log:
            raise HTTPException(status_code=404, detail="Failed to update log")
        
        return Log(**updated_log)
    
    async def delete_log(self, log_id: str) -> None:
        """Delete a log entry"""
        # Check if log exists
        existing_log = await self.log_repository.get_log_by_id(log_id)
        if not existing_log:
            raise HTTPException(status_code=404, detail="Log not found")
        
        # Delete log
        deleted = await self.log_repository.delete_log(log_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Failed to delete log")
