from pydantic import BaseModel, Field
from typing import Optional

class ServiceBase(BaseModel):
    """Base service schema with common attributes"""
    project_id: str
    name: str
    port: Optional[int] = None
    url: Optional[str] = None
    status: Optional[str] = None  # e.g., 'Running', 'Stopped'
    health: Optional[str] = None  # e.g., 'Healthy', 'Warning'
    uptime: Optional[str] = None
    version: Optional[str] = None
    last_deployment: Optional[str] = None

class ServiceCreate(ServiceBase):
    """Schema for creating a new service"""
    pass

class ServiceUpdate(BaseModel):
    """Schema for updating an existing service"""
    project_id: Optional[str] = None
    name: Optional[str] = None
    port: Optional[int] = None
    url: Optional[str] = None
    status: Optional[str] = None
    health: Optional[str] = None
    uptime: Optional[str] = None
    version: Optional[str] = None
    last_deployment: Optional[str] = None

class Service(ServiceBase):
    """Schema for service response"""
    id: str
    
    class Config:
        orm_mode = True  # pydantic v1 equivalent of populate_by_name
