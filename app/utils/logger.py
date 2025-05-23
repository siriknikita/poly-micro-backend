"""
Service Logger Utility for Poly Micro Manager

This module provides a simple logging interface for services to log messages
that will be stored in the MongoDB database and displayed in the Poly Micro Manager dashboard.
"""

import asyncio
from typing import Optional, Union
from bson import ObjectId
from app.models.log import LogEntry
from app.schemas.log import Severity
from app.db.database import get_database


class ServiceLogger:
    """
    Service Logger class for easy logging from services.
    Provides methods to log messages with different severity levels.
    """

    def __init__(self, project_id: Union[str, ObjectId], service_id: Union[str, ObjectId]):
        """
        Initialize a logger instance for a specific project and service.
        
        Args:
            project_id: The project identifier (str or ObjectId)
            service_id: The service identifier (str or ObjectId)
        """
        # Convert ObjectId to string if necessary
        self.project_id = str(project_id)
        self.service_id = str(service_id)
        self.collection_name = "poly_micro_logs"
        
    async def _log(self, message: str, severity: Severity, 
                 test_id: Optional[str] = None, 
                 func_id: Optional[str] = None, 
                 source: Optional[str] = None) -> LogEntry:
        """
        Internal method to log a message to the database.
        
        Args:
            message: The log message
            severity: Log severity level
            test_id: Optional test identifier
            func_id: Optional function identifier
            source: Optional source identifier
            
        Returns:
            The created LogEntry object
        """
        # Create log entry
        log_entry = LogEntry(
            project_id=self.project_id,
            service_id=self.service_id,
            message=message,
            severity=severity.value,
            test_id=test_id,
            func_id=func_id,
            source=source
        )
        
        # Store in database
        db = get_database()  # This is not async but returns AsyncIOMotorDatabase
        log_dict = log_entry.to_dict()
        
        # Remove id if None to let MongoDB generate one
        if log_dict.get("id") is None:
            log_dict.pop("id", None)
            
        # Insert into database
        result = await db[self.collection_name].insert_one(log_dict)
        
        # Update log entry with generated ID
        log_entry.id = str(result.inserted_id)
        return log_entry
    
    def _ensure_async(self, func):
        """Ensure a function runs in an async context, even if called synchronously."""
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
            
        def sync_wrapper(*args, **kwargs):
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're in an async context, create a task instead of a new loop
                    # This avoids the "Cannot run the event loop while another loop is running" error
                    future = asyncio.ensure_future(func(*args, **kwargs))
                    # We need to return the result, but we can't await here directly
                    # For simplicity in this implementation, we'll return the future
                    # The caller should be aware they need to await the result
                    return future
                else:
                    # If no loop is running, we can run until complete
                    return loop.run_until_complete(func(*args, **kwargs))
            except RuntimeError:
                # Fallback for when we can't get a loop or there are other issues
                # Just return the coroutine - caller must await it
                return func(*args, **kwargs)
                
        return sync_wrapper
    
    # Synchronous methods that work in both sync and async contexts
    def debug(self, message: str, test_id: Optional[str] = None, 
            func_id: Optional[str] = None, source: Optional[str] = None) -> LogEntry:
        """Log a debug message."""
        return self._ensure_async(self._log)(
            message, Severity.DEBUG, test_id, func_id, source
        )
        
    def info(self, message: str, test_id: Optional[str] = None, 
           func_id: Optional[str] = None, source: Optional[str] = None) -> LogEntry:
        """Log an info message."""
        return self._ensure_async(self._log)(
            message, Severity.INFO, test_id, func_id, source
        )
        
    def warning(self, message: str, test_id: Optional[str] = None, 
              func_id: Optional[str] = None, source: Optional[str] = None) -> LogEntry:
        """Log a warning message."""
        return self._ensure_async(self._log)(
            message, Severity.WARN, test_id, func_id, source
        )
        
    def error(self, message: str, test_id: Optional[str] = None, 
            func_id: Optional[str] = None, source: Optional[str] = None) -> LogEntry:
        """Log an error message."""
        return self._ensure_async(self._log)(
            message, Severity.ERROR, test_id, func_id, source
        )
        
    def critical(self, message: str, test_id: Optional[str] = None, 
               func_id: Optional[str] = None, source: Optional[str] = None) -> LogEntry:
        """Log a critical message."""
        return self._ensure_async(self._log)(
            message, Severity.CRITICAL, test_id, func_id, source
        )
    
    # Async versions of the logging methods
    async def adebug(self, message: str, test_id: Optional[str] = None, 
                  func_id: Optional[str] = None, source: Optional[str] = None) -> LogEntry:
        """Log a debug message asynchronously."""
        return await self._log(message, Severity.DEBUG, test_id, func_id, source)
    
    async def ainfo(self, message: str, test_id: Optional[str] = None, 
                 func_id: Optional[str] = None, source: Optional[str] = None) -> LogEntry:
        """Log an info message asynchronously."""
        return await self._log(message, Severity.INFO, test_id, func_id, source)
    
    async def awarning(self, message: str, test_id: Optional[str] = None, 
                    func_id: Optional[str] = None, source: Optional[str] = None) -> LogEntry:
        """Log a warning message asynchronously."""
        return await self._log(message, Severity.WARN, test_id, func_id, source)
    
    async def aerror(self, message: str, test_id: Optional[str] = None, 
                  func_id: Optional[str] = None, source: Optional[str] = None) -> LogEntry:
        """Log an error message asynchronously."""
        return await self._log(message, Severity.ERROR, test_id, func_id, source)
    
    async def acritical(self, message: str, test_id: Optional[str] = None, 
                     func_id: Optional[str] = None, source: Optional[str] = None) -> LogEntry:
        """Log a critical message asynchronously."""
        return await self._log(message, Severity.CRITICAL, test_id, func_id, source)


def create_logger(project_id: Union[str, ObjectId], service_id: Union[str, ObjectId]) -> ServiceLogger:
    """
    Create a new logger instance for a specific project and service.
    
    This is the main function that should be used to create logger instances.
    
    Args:
        project_id: The project identifier (str or ObjectId)
        service_id: The service identifier (str or ObjectId)
        
    Returns:
        A ServiceLogger instance tied to the specified project and service
    """
    return ServiceLogger(project_id, service_id)
