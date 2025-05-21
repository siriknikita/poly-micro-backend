from fastapi import APIRouter, Depends, Path, Query, HTTPException, status
from typing import List, Optional

from app.services.metrics_service import MetricsService
from app.api.dependencies import get_metrics_service
from app.schemas.metrics import CPUEntry, CPUEntryCreate, CPUEntryUpdate, CPUDataCreate

router = APIRouter()

@router.get("/cpu", response_model=List[CPUEntry])
async def get_all_cpu_data(
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get all CPU metrics data"""
    return await metrics_service.get_all_cpu_data()

@router.get("/cpu/project/{project_id}", response_model=List[CPUEntry])
async def get_cpu_data_by_project(
    project_id: str = Path(..., description="The project ID to get CPU data for"),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get CPU metrics data for a specific project"""
    return await metrics_service.get_cpu_data_by_project(project_id)

@router.get("/cpu/service/{service_name}", response_model=List[CPUEntry])
async def get_cpu_data_by_service(
    service_name: str = Path(..., description="The service name to get CPU data for"),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get CPU metrics data for a specific service"""
    return await metrics_service.get_cpu_data_by_service(service_name)

@router.get("/cpu/{cpu_entry_id}", response_model=CPUEntry)
async def get_cpu_entry(
    cpu_entry_id: str = Path(..., description="The ID of the CPU entry to get"),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get a specific CPU metrics entry by ID"""
    return await metrics_service.get_cpu_entry_by_id(cpu_entry_id)

@router.post("/cpu", response_model=CPUEntry, status_code=status.HTTP_201_CREATED)
async def create_cpu_entry(
    cpu_entry: CPUEntryCreate,
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Create a new CPU metrics entry"""
    return await metrics_service.create_cpu_entry(cpu_entry)

@router.put("/cpu/{cpu_entry_id}", response_model=CPUEntry)
async def update_cpu_entry(
    cpu_entry: CPUEntryUpdate,
    cpu_entry_id: str = Path(..., description="The ID of the CPU metrics entry to update"),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Update a CPU metrics entry"""
    return await metrics_service.update_cpu_entry(cpu_entry_id, cpu_entry)

@router.delete("/cpu/{cpu_entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cpu_entry(
    cpu_entry_id: str = Path(..., description="The ID of the CPU metrics entry to delete"),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Delete a CPU metrics entry"""
    await metrics_service.delete_cpu_entry(cpu_entry_id)
    return None

@router.post("/cpu/{cpu_entry_id}/data", response_model=CPUEntry)
async def add_cpu_data_point(
    cpu_data: CPUDataCreate,
    cpu_entry_id: str = Path(..., description="The ID of the CPU metrics entry to add data to"),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Add a new data point to an existing CPU metrics entry"""
    return await metrics_service.add_cpu_data_point(cpu_entry_id, cpu_data)
