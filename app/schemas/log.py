from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.core.enum_compat import StrEnum

class Severity(StrEnum):
    """Log severity enum"""
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    CRITICAL = "critical"

class LogBase(BaseModel):
    """Base log schema with common attributes"""
    project_id: str
    service_id: str
    test_id: Optional[str] = None
    func_id: Optional[str] = None
    message: str
    severity: Severity
    timestamp: Optional[str] = None
    source: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True

class LogCreate(LogBase):
    """Schema for creating a new log entry"""
    pass

class LogUpdate(BaseModel):
    """Schema for updating an existing log entry"""
    project_id: Optional[str] = None
    service_id: Optional[str] = None
    test_id: Optional[str] = None
    func_id: Optional[str] = None
    message: Optional[str] = None
    severity: Optional[Severity] = None
    timestamp: Optional[str] = None
    source: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True

class Log(LogBase):
    """Schema for log response"""
    id: str
    
    class Config:
        from_attributes = True  # pydantic v1 equivalent of populate_by_name
        arbitrary_types_allowed = True
