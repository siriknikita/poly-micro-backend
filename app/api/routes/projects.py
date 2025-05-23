from fastapi import APIRouter, Depends, Path, HTTPException, status
from typing import List

from app.services.project_service import ProjectService
from app.api.dependencies import get_project_service
from app.schemas.project import Project, ProjectCreate, ProjectUpdate

router = APIRouter()

@router.get("/", response_model=List[Project])
async def get_all_projects(
    project_service: ProjectService = Depends(get_project_service)
):
    """Get all projects"""
    print("DEBUG: Getting all projects...")
    print("DEBUG: Project service: ", project_service)
    return await project_service.get_all_projects()

@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str = Path(..., description="The ID of the project to get"),
    project_service: ProjectService = Depends(get_project_service)
):
    """Get a specific project by ID"""
    return await project_service.get_project_by_id(project_id)

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    project_service: ProjectService = Depends(get_project_service)
):
    """Create a new project"""
    return await project_service.create_project(project)

@router.put("/{project_id}", response_model=Project)
async def update_project(
    project: ProjectUpdate,
    project_id: str = Path(..., description="The ID of the project to update"),
    project_service: ProjectService = Depends(get_project_service)
):
    """Update a project"""
    return await project_service.update_project(project_id, project)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str = Path(..., description="The ID of the project to delete"),
    project_service: ProjectService = Depends(get_project_service)
):
    """Delete a project"""
    await project_service.delete_project(project_id)
    return None
