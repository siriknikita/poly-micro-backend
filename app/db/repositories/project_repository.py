from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository
from app.schemas.project import ProjectCreate, ProjectUpdate, Project
from app.core.cache import cached, invalidate_cache

class ProjectRepository(BaseRepository):
    """Repository for project-related database operations"""
    
    def __init__(self, db):
        super().__init__(db, "poly_micro_projects")
    
    @cached(ttl=300, prefix="projects:all")
    async def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all projects with caching"""
        projects = await self.find_all()
        
        # Transform MongoDB data to match Pydantic model requirements
        for project in projects:
            # Convert _id to id if it exists
            if '_id' in project and 'id' not in project:
                project['id'] = str(project['_id'])
            
            # Add path field if missing (using name as fallback)
            if 'path' not in project:
                project['path'] = project.get('name', '').lower().replace(' ', '_')
                
        return projects
    
    @cached(ttl=300, prefix="projects:by_id")
    async def get_project_by_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a project by ID with caching"""
        project = await self.find_one(project_id)
        
        if project:
            # Convert _id to id if it exists
            if '_id' in project and 'id' not in project:
                project['id'] = str(project['_id'])
            
            # Add path field if missing (using name as fallback)
            if 'path' not in project:
                project['path'] = project.get('name', '').lower().replace(' ', '_')
        
        return project
    
    @invalidate_cache(prefix="projects")
    async def create_project(self, project: ProjectCreate) -> Dict[str, Any]:
        """Create a new project with auto-generated ID and invalidate cache"""
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
        
        # Handle different types - if it's a Pydantic model use dict(), if already a dict use as is
        if hasattr(project, 'dict'):
            project_data = project.dict()
        else:
            project_data = project
            
        project_data["id"] = new_id
        
        return await self.create(project_data)
    
    @invalidate_cache(prefix="projects")
    async def update_project(self, project_id: str, project: ProjectUpdate) -> Optional[Dict[str, Any]]:
        """Update a project and invalidate cache"""
        # Only update provided fields
        # Handle different Pydantic versions by using dict() instead of model_dump()
        update_data = {k: v for k, v in project.dict().items() if v is not None}
        if not update_data:
            return await self.find_one(project_id)  # Return current project if no updates
        
        return await self.update(project_id, update_data)
    
    @invalidate_cache(prefix="projects")
    async def delete_project(self, project_id: str) -> bool:
        """Delete a project and invalidate cache"""
        return await self.delete(project_id)

    def __str__(self):
        return f"ProjectRepository({self.db})"
        