from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class TestItem(BaseModel):
    """Schema for a single test item discovered by pytest --collect-only"""
    id: str
    name: str
    path: str
    nodeid: str
    type: str  # 'class', 'function', etc.
    class_name: Optional[str] = None
    module_name: str


class ServiceTestsResponse(BaseModel):
    """Schema for response containing all tests for a microservice"""
    service_id: str
    service_name: str
    project_id: str
    discovery_time: datetime = Field(default_factory=datetime.now)
    tests: List[TestItem] = []
    metadata: Optional[Dict[str, Any]] = None
