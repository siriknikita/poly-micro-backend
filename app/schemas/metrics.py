from pydantic import BaseModel, Field
from typing import List, Optional

class CPUData(BaseModel):
    """CPU data point schema"""
    time: str
    load: float
    memory: float
    threads: int

class CPUDataCreate(BaseModel):
    """Schema for creating a new CPU data point"""
    time: str
    load: float
    memory: float
    threads: int

class CPUEntryBase(BaseModel):
    """Base CPU entry schema with common attributes"""
    project_id: str
    service_name: str
    data: List[CPUData]

class CPUEntryCreate(BaseModel):
    """Schema for creating a new CPU entry"""
    project_id: str
    service_name: str
    data: List[CPUDataCreate]

class CPUEntryUpdate(BaseModel):
    """Schema for updating an existing CPU entry"""
    data: Optional[List[CPUDataCreate]] = None

class CPUEntry(CPUEntryBase):
    """Schema for CPU entry response"""
    id: Optional[str] = None
    
    class Config:
        orm_mode = True  # pydantic v1 equivalent of populate_by_name
