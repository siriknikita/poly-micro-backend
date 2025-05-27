from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ServiceTestItem(BaseModel):
    """Schema for service test items returned by the API"""
    id: str
    name: str
    type: str  # 'microservice'
    project_id: str  # Using snake_case for API compatibility
    children: List[Dict[str, Any]] = []
    
    # Additional properties for microservices
    status: Optional[str] = None
    version: Optional[str] = None
    last_deployment: Optional[str] = None
    port: Optional[int] = None
    url: Optional[str] = None
    health: Optional[str] = None
    uptime: Optional[str] = None
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }
