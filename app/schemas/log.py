from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum as PyEnum

class Severity(str, PyEnum):
    """Log severity enum"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"

class LogBase(BaseModel):
    """Base log schema with common attributes"""
    service: str
    severity: Severity
    message: str
    timestamp: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        arbitrary_types_allowed = True

class LogCreate(LogBase):
    """Schema for creating a new log entry"""
    pass

class LogUpdate(BaseModel):
    """Schema for updating an existing log entry"""
    service: Optional[str] = None
    severity: Optional[Severity] = None
    message: Optional[str] = None
    timestamp: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        arbitrary_types_allowed = True

class Log(LogBase):
    """Schema for log response"""
    id: str
    
    class Config:
        from_attributes = True  # pydantic v1 equivalent of populate_by_name
        arbitrary_types_allowed = True
