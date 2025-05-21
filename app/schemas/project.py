from pydantic import BaseModel, Field
from typing import Optional

class ProjectBase(BaseModel):
    """Base project schema with common attributes"""
    name: str
    path: str

class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    pass

class ProjectUpdate(ProjectBase):
    """Schema for updating an existing project"""
    name: Optional[str] = None
    path: Optional[str] = None

class Project(ProjectBase):
    """Schema for project response"""
    id: str
    
    class Config:
        orm_mode = True  # pydantic v1 equivalent of populate_by_name
