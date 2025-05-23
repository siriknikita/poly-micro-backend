"""
Service for managing logs in the poly_micro_logs collection.
This service handles the business logic for service logs.
"""

from typing import List, Optional, Union, Dict, Any
from fastapi import HTTPException
from bson import ObjectId
from app.db.repositories.logs_collection_repository import LogsCollectionRepository
from app.schemas.log import Log, LogCreate, LogUpdate, Severity
from app.models.log import LogEntry


class ServiceLogsService:
    """Service for service logs-related business logic"""
    
    def __init__(self, logs_repository: LogsCollectionRepository):
        self.logs_repository = logs_repository
    
    async def get_all_logs(
        self, 
        project_id: Optional[str] = None,
        service_id: Optional[str] = None,
        test_id: Optional[str] = None,
        func_id: Optional[str] = None,
        severity: Optional[Severity] = None,
        source: Optional[str] = None
    ) -> List[Log]:
        """Get all logs with optional filtering"""
        logs = await self.logs_repository.get_all_logs(
            project_id=project_id,
            service_id=service_id,
            test_id=test_id,
            func_id=func_id,
            severity=severity,
            source=source
        )
        return [Log(**log) for log in logs]
    
    async def get_log_by_id(self, log_id: str) -> Log:
        """Get a log by ID"""
        log = await self.logs_repository.get_log_by_id(log_id)
        if not log:
            raise HTTPException(status_code=404, detail="Log not found")
        return Log(**log)
    
    async def get_logs_by_project(self, project_id: str) -> List[Log]:
        """Get all logs for a specific project"""
        logs = await self.logs_repository.get_logs_by_project(project_id)
        return [Log(**log) for log in logs]
    
    async def get_logs_by_service(self, service_id: str) -> List[Log]:
        """Get all logs for a specific service"""
        logs = await self.logs_repository.get_logs_by_service(service_id)
        return [Log(**log) for log in logs]
    
    async def create_log(self, log: Union[LogCreate, LogEntry]) -> Log:
        """Create a new log entry"""
        log_data = await self.logs_repository.create_log(log)
        return Log(**log_data)
    
    async def create_log_entry(self, log_data: Dict[str, Any]) -> Log:
        """Create a log entry from raw data"""
        log_entry = LogEntry.from_dict(log_data)
        log_data = await self.logs_repository.create_log(log_entry)
        return Log(**log_data)
