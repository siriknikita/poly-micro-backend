from fastapi import APIRouter, Depends, Path, Query, HTTPException, status
from typing import List

from app.services.service_service import ServiceService
from app.services.test_service import TestService
from app.services.project_service import ProjectService
from app.api.dependencies import get_service_service, get_test_service, get_project_service
from app.schemas.service import Service, ServiceCreate, ServiceUpdate
from app.schemas.test_item import TestItem
from app.schemas.service_test_item import ServiceTestItem
from app.schemas.service_tests import ServiceTestsResponse

router = APIRouter()

@router.get("/", response_model=List[Service])
async def get_all_services(
    service_service: ServiceService = Depends(get_service_service)
):
    """Get all services across all projects"""
    return await service_service.get_all_services()

@router.get("/project/{project_id}", response_model=List[ServiceTestItem])
async def get_services_by_project(
    project_id: str = Path(..., description="The ID of the project to get services for"),
    service_service: ServiceService = Depends(get_service_service)
):
    """Get all services for a specific project as TestItems"""
    items = await service_service.get_services_by_project(project_id)
    print(f"API Route: Retrieved {len(items)} TestItems")
    
    # Convert TestItem to ServiceTestItem for API response
    result = []
    for item in items:
        service_item = ServiceTestItem(
            id=item.id,
            name=item.name,
            type=item.type,
            project_id=item.projectId,  # Convert camelCase to snake_case
            children=item.children,
            status=item.status,
            version=item.version,
            last_deployment=item.lastDeployed,  # Convert camelCase to snake_case
            port=item.port,
            url=item.url,
            health=item.health,
            uptime=item.uptime
        )
        result.append(service_item)
    
    print(f"API Route: Converted to {len(result)} ServiceTestItems")
    return result

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

@router.get("/tests/{service_id}", response_model=ServiceTestsResponse)
async def get_service_tests(
    service_id: str = Path(..., description="The ID of the service to get tests for"),
    service_service: ServiceService = Depends(get_service_service),
    test_service: TestService = Depends(get_test_service),
    project_service: ProjectService = Depends(get_project_service)
):
    """Get all available tests for a specific service"""
    # Get the service details
    service = await service_service.get_service_by_id(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Get the project details to get the project path and tests directory path
    project = await project_service.get_project_by_id(service.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Collect the tests for the service
    test_results = await test_service.collect_service_tests(
        project_id=project.id,
        service_id=service.id,
        service_name=service.name,
        project_path=project.path,
        tests_dir_path=project.tests_dir_path
    )
    
    return test_results
