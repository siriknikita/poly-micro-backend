from typing import List, Optional
from fastapi import HTTPException
from app.db.repositories.project_repository import ProjectRepository
from app.schemas.project import Project, ProjectCreate, ProjectUpdate

class ProjectService:
    """Service for project-related business logic"""
    
    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository
    
    async def get_all_projects(self) -> List[Project]:
        """Get all projects"""
        projects = await self.project_repository.get_all_projects()
        return [Project(**project) for project in projects]
    
    async def get_project_by_id(self, project_id: str) -> Project:
        """Get a project by ID"""
        project = await self.project_repository.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return Project(**project)
    
    async def create_project(self, project: ProjectCreate) -> Project:
        """Create a new project"""
        project_data = await self.project_repository.create_project(project)
        return Project(**project_data)
    
    async def update_project(self, project_id: str, project: ProjectUpdate) -> Project:
        """Update a project"""
        # Check if project exists
        existing_project = await self.project_repository.get_project_by_id(project_id)
        if not existing_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Update project
        updated_project = await self.project_repository.update_project(project_id, project)
        if not updated_project:
            raise HTTPException(status_code=404, detail="Failed to update project")
        
        return Project(**updated_project)
    
    async def delete_project(self, project_id: str) -> None:
        """Delete a project"""
        # Check if project exists
        existing_project = await self.project_repository.get_project_by_id(project_id)
        if not existing_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Delete project
        deleted = await self.project_repository.delete_project(project_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Failed to delete project")
