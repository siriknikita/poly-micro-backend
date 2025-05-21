from fastapi import APIRouter, Depends, Path, Query, HTTPException, status
from typing import List, Optional

from app.services.log_service import LogService
from app.api.dependencies import get_log_service
from app.schemas.log import Log, LogCreate, LogUpdate, Severity

router = APIRouter()

@router.get("/", response_model=List[Log])
async def get_all_logs(
    service: Optional[str] = Query(None, description="Filter logs by service name"),
    severity: Optional[Severity] = Query(None, description="Filter logs by severity"),
    log_service: LogService = Depends(get_log_service)
):
    """Get all logs with optional filtering"""
    return await log_service.get_all_logs(service, severity)

@router.get("/{log_id}", response_model=Log)
async def get_log(
    log_id: str = Path(..., description="The ID of the log to get"),
    log_service: LogService = Depends(get_log_service)
):
    """Get a specific log by ID"""
    return await log_service.get_log_by_id(log_id)

@router.post("/", response_model=Log, status_code=status.HTTP_201_CREATED)
async def create_log(
    log: LogCreate,
    log_service: LogService = Depends(get_log_service)
):
    """Create a new log entry"""
    return await log_service.create_log(log)

@router.put("/{log_id}", response_model=Log)
async def update_log(
    log: LogUpdate,
    log_id: str = Path(..., description="The ID of the log to update"),
    log_service: LogService = Depends(get_log_service)
):
    """Update a log entry"""
    return await log_service.update_log(log_id, log)

@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log(
    log_id: str = Path(..., description="The ID of the log to delete"),
    log_service: LogService = Depends(get_log_service)
):
    """Delete a log entry"""
    await log_service.delete_log(log_id)
    return None
