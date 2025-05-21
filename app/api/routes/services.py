from fastapi import APIRouter, Depends, Path, Query, HTTPException, status
from typing import List

from app.services.service_service import ServiceService
from app.api.dependencies import get_service_service
from app.schemas.service import Service, ServiceCreate, ServiceUpdate

router = APIRouter()

@router.get("/", response_model=List[Service])
async def get_all_services(
    service_service: ServiceService = Depends(get_service_service)
):
    """Get all services across all projects"""
    return await service_service.get_all_services()

@router.get("/project/{project_id}", response_model=List[Service])
async def get_services_by_project(
    project_id: str = Path(..., description="The ID of the project to get services for"),
    service_service: ServiceService = Depends(get_service_service)
):
    """Get all services for a specific project"""
    return await service_service.get_services_by_project(project_id)

@router.get("/{service_id}", response_model=Service)
async def get_service(
    service_id: str = Path(..., description="The ID of the service to get"),
    service_service: ServiceService = Depends(get_service_service)
):
    """Get a specific service by ID"""
    return await service_service.get_service_by_id(service_id)

@router.post("/", response_model=Service, status_code=status.HTTP_201_CREATED)
async def create_service(
    service: ServiceCreate,
    service_service: ServiceService = Depends(get_service_service)
):
    """Create a new service"""
    return await service_service.create_service(service)

@router.put("/{service_id}", response_model=Service)
async def update_service(
    service: ServiceUpdate,
    service_id: str = Path(..., description="The ID of the service to update"),
    service_service: ServiceService = Depends(get_service_service)
):
    """Update a service"""
    return await service_service.update_service(service_id, service)

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: str = Path(..., description="The ID of the service to delete"),
    service_service: ServiceService = Depends(get_service_service)
):
    """Delete a service"""
    await service_service.delete_service(service_id)
    return None
