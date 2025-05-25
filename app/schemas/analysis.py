from pydantic import BaseModel, Field
from typing import Optional


class LogAnalysisRequest(BaseModel):
    """Request model for log analysis"""
    project_id: str = Field(..., description="ID of the project to analyze logs for")
    

class LogAnalysisResponse(BaseModel):
    """Response model for log analysis results"""
    project_id: str = Field(..., description="ID of the project that was analyzed")
    analysis: str = Field(..., description="Analysis results from the AI model")
    log_count: int = Field(..., description="Number of logs that were analyzed")
    success: bool = Field(..., description="Whether the analysis was successful")
    error: Optional[str] = Field(None, description="Error message if analysis failed")
