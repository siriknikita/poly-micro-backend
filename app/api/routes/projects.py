from fastapi import APIRouter, Depends, Path, HTTPException, status, Request
from typing import List

from app.services.project_service import ProjectService
from app.api.dependencies import get_project_service
from app.schemas.project import Project, ProjectCreate, ProjectUpdate

router = APIRouter()

@router.get("/", response_model=List[Project])
async def get_all_projects(
    project_service: ProjectService = Depends(get_project_service),
    request: Request = None
):
    """Get all projects"""
    print("DEBUG: Getting all projects...")
    print("DEBUG: Project service: ", project_service)
    
    # Pass the request to the service method to enable dependency resolution
    projects = await project_service.get_all_projects(request)
    print(f"DEBUG: Projects to return: {projects}")
    for project in projects:
        print(f"DEBUG: Project {project.id} has {len(project.microservices or [])} microservices")
    
    return projects

@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str = Path(..., description="The ID of the project to get"),
    project_service: ProjectService = Depends(get_project_service),
    request: Request = None
):
    """Get a specific project by ID"""
    print(f"DEBUG: Getting project with ID: {project_id}")
    
    # Pass the request to the service method to enable dependency resolution
    project = await project_service.get_project_by_id(project_id, request)
    
    print(f"DEBUG: Project to return: {project}")
    print(f"DEBUG: Project {project.id} has {len(project.microservices or [])} microservices")
    
    return project

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
