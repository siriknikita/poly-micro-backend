from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class TestItem(BaseModel):
    """Schema for test items (microservices, functions, test cases)"""
    id: str
    name: str
    type: str  # 'microservice', 'function', or 'test-case'
    # Use List[Any] to avoid circular reference issues
    children: Optional[List[Dict[str, Any]]] = []
    
    # Additional properties for microservices
    projectId: Optional[str] = None
    status: Optional[str] = None
    version: Optional[str] = None
    lastDeployed: Optional[str] = None
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }
