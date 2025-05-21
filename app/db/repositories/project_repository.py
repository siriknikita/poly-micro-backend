from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository
from app.schemas.project import ProjectCreate, ProjectUpdate, Project

class ProjectRepository(BaseRepository):
    """Repository for project-related database operations"""
    
    def __init__(self, db):
        super().__init__(db, "projects")
    
    async def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all projects"""
        return await self.find_all()
    
    async def get_project_by_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a project by ID"""
        return await self.find_one(project_id)
    
    async def create_project(self, project: ProjectCreate) -> Dict[str, Any]:
        """Create a new project with auto-generated ID"""
        # Generate a new ID
        all_projects = await self.find_all(limit=1000)
        max_id = 0
        for p in all_projects:
            try:
                p_id = int(p.get("id", 0))
                if p_id > max_id:
                    max_id = p_id
            except ValueError:
                continue
        
        # Create new project with incremented ID
        new_id = str(max_id + 1)
        project_data = project.dict()
        project_data["id"] = new_id
        
        return await self.create(project_data)
    
    async def update_project(self, project_id: str, project: ProjectUpdate) -> Optional[Dict[str, Any]]:
        """Update a project"""
        # Only update provided fields
        update_data = {k: v for k, v in project.dict().items() if v is not None}
        if not update_data:
            return await self.find_one(project_id)  # Return current project if no updates
        
        return await self.update(project_id, update_data)
    
    async def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        return await self.delete(project_id)
