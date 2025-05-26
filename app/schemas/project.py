from pydantic import BaseModel, Field
from typing import Optional, List

# Import TestItem schema for microservices
from app.schemas.test_item import TestItem

class ProjectBase(BaseModel):
    """Base project schema with common attributes"""
    name: str
    path: str
    tests_dir_path: Optional[str] = "tests"  # Default tests directory path

class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    pass

class ProjectUpdate(ProjectBase):
    """Schema for updating an existing project"""
    name: Optional[str] = None
    path: Optional[str] = None
    tests_dir_path: Optional[str] = None

class Project(ProjectBase):
    """Schema for project response"""
    id: str
    microservices: Optional[List[TestItem]] = None
    
    class Config:
        from_attributes = True  # pydantic v1 equivalent of populate_by_name
        populate_by_name = True
