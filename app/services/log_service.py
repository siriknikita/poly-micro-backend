from typing import List, Optional, Union, Dict, Any
from fastapi import HTTPException
from app.db.repositories.log_repository import LogRepository
from app.schemas.log import Log, LogCreate, LogUpdate, Severity
from app.models.log import LogEntry

class LogService:
    """Service for log-related business logic"""
    
    def __init__(self, log_repository: LogRepository):
        self.log_repository = log_repository
    
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
        logs = await self.log_repository.get_all_logs(
            project_id=project_id,
            service_id=service_id,
            test_id=test_id,
            func_id=func_id,
            severity=severity,
            source=source
        )
        print('ALL LOGS', logs)
        # Ensure each log has an ID field for proper validation
        result = []
        for log in logs:
            if 'id' not in log and '_id' in log:
                # Use MongoDB's _id if no id is present
                log['id'] = str(log['_id'])
            elif 'id' not in log:
                # Assign a fallback ID if neither id nor _id is present
                log['id'] = 'unknown'
            result.append(Log(**log))
        return result
    
    async def get_log_by_id(self, log_id: str) -> Log:
        """Get a log by ID"""
        log = await self.log_repository.get_log_by_id(log_id)
        if not log:
            raise HTTPException(status_code=404, detail="Log not found")
        return Log(**log)
    
    async def get_logs_by_project(self, project_id: str) -> List[Log]:
        """Get all logs for a specific project"""
        print('PROJECT ID', project_id)
        logs = await self.log_repository.get_logs_by_project(project_id)
        all_logs = await self.log_repository.get_all_logs()
        print('LOGS', logs)
        print('ALL LOGS', all_logs)
        # Ensure each log has an ID field for proper validation
        result = []
        for log in logs:
            if 'id' not in log and '_id' in log:
                # Use MongoDB's _id if no id is present
                log['id'] = str(log['_id'])
            elif 'id' not in log:
                # Assign a fallback ID if neither id nor _id is present
                log['id'] = 'unknown'
            result.append(Log(**log))
        return result
    
    async def get_logs_by_service(self, service_id: str) -> List[Log]:
        """Get all logs for a specific service"""
        logs = await self.log_repository.get_logs_by_service(service_id)
        # Ensure each log has an ID field for proper validation
        result = []
        for log in logs:
            if 'id' not in log and '_id' in log:
                # Use MongoDB's _id if no id is present
                log['id'] = str(log['_id'])
            elif 'id' not in log:
                # Assign a fallback ID if neither id nor _id is present
                log['id'] = 'unknown'
            result.append(Log(**log))
        return result
    
    async def create_log(self, log: Union[LogCreate, LogEntry]) -> Log:
        """Create a new log entry"""
        log_data = await self.log_repository.create_log(log)
        return Log(**log_data)
    
    async def create_log_entry(self, log_data: Dict[str, Any]) -> Log:
        """Create a log entry from raw data"""
        log_entry = LogEntry.from_dict(log_data)
        log_data = await self.log_repository.create_log(log_entry)
        return Log(**log_data)
    
    async def update_log(self, log_id: str, log: Union[LogUpdate, LogEntry]) -> Log:
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
