from typing import List, Optional
from fastapi import HTTPException
from app.db.repositories.metrics_repository import MetricsRepository
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.service_repository import ServiceRepository
from app.schemas.metrics import CPUEntry, CPUEntryCreate, CPUEntryUpdate, CPUDataCreate

class MetricsService:
    """Service for metrics-related business logic"""
    
    def __init__(
        self, 
        metrics_repository: MetricsRepository,
        project_repository: ProjectRepository,
        service_repository: ServiceRepository
    ):
        self.metrics_repository = metrics_repository
        self.project_repository = project_repository
        self.service_repository = service_repository
    
    async def get_all_cpu_data(self) -> List[CPUEntry]:
        """Get all CPU metrics data"""
        cpu_data = await self.metrics_repository.get_all_cpu_data()
        return [CPUEntry(**entry) for entry in cpu_data]
    
    async def get_cpu_data_by_project(self, project_id: str) -> List[CPUEntry]:
        """Get CPU metrics data for a specific project"""
        # Check if project exists
        project = await self.project_repository.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        cpu_data = await self.metrics_repository.get_cpu_data_by_project(project_id)
        return [CPUEntry(**entry) for entry in cpu_data]
    
    async def get_cpu_data_by_service(self, service_name: str) -> List[CPUEntry]:
        """Get CPU metrics data for a specific service"""
        cpu_data = await self.metrics_repository.get_cpu_data_by_service(service_name)
        return [CPUEntry(**entry) for entry in cpu_data]
    
    async def get_cpu_entry_by_id(self, cpu_entry_id: str) -> CPUEntry:
        """Get a specific CPU metrics entry by ID"""
        cpu_entry = await self.metrics_repository.get_cpu_entry_by_id(cpu_entry_id)
        if not cpu_entry:
            raise HTTPException(status_code=404, detail="CPU metrics entry not found")
        return CPUEntry(**cpu_entry)
    
    async def create_cpu_entry(self, cpu_entry: CPUEntryCreate) -> CPUEntry:
        """Create a new CPU metrics entry"""
        # Check if project exists
        project = await self.project_repository.get_project_by_id(cpu_entry.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if service exists for the project
        service_exists = await self.service_repository.check_service_exists(
            cpu_entry.project_id, cpu_entry.service_name
        )
        if not service_exists:
            raise HTTPException(status_code=404, detail="Service not found for the given project")
        
        # Create CPU metrics entry
        cpu_entry_data = await self.metrics_repository.create_cpu_entry(cpu_entry)
        if not cpu_entry_data:
            raise HTTPException(status_code=404, detail="Failed to create CPU metrics entry")

        return CPUEntry(**cpu_entry_data)
    
    async def update_cpu_entry(self, cpu_entry_id: str, cpu_entry: CPUEntryUpdate) -> CPUEntry:
        """Update a CPU metrics entry"""
        # Check if CPU entry exists
        existing_entry = await self.metrics_repository.get_cpu_entry_by_id(cpu_entry_id)
        if not existing_entry:
            raise HTTPException(status_code=404, detail="CPU metrics entry not found")
        
        # Update CPU entry
        updated_entry = await self.metrics_repository.update_cpu_entry(cpu_entry_id, cpu_entry)
        if not updated_entry:
            raise HTTPException(status_code=404, detail="Failed to update CPU metrics entry")
        
        return CPUEntry(**updated_entry)
    
    async def delete_cpu_entry(self, cpu_entry_id: str) -> None:
        """Delete a CPU metrics entry"""
        # Check if CPU entry exists
        existing_entry = await self.metrics_repository.get_cpu_entry_by_id(cpu_entry_id)
        if not existing_entry:
            raise HTTPException(status_code=404, detail="CPU metrics entry not found")
        
        # Delete CPU entry
        deleted = await self.metrics_repository.delete_cpu_entry(cpu_entry_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Failed to delete CPU metrics entry")
    
    async def add_cpu_data_point(self, cpu_entry_id: str, cpu_data: CPUDataCreate) -> CPUEntry:
        """Add a new data point to an existing CPU metrics entry"""
        # Check if CPU entry exists
        existing_entry = await self.metrics_repository.get_cpu_entry_by_id(cpu_entry_id)
        if not existing_entry:
            raise HTTPException(status_code=404, detail="CPU metrics entry not found")
        
        # Add data point to CPU entry
        updated_entry = await self.metrics_repository.add_cpu_data_point(cpu_entry_id, cpu_data)
        if not updated_entry:
            raise HTTPException(status_code=404, detail="Failed to add data point to CPU metrics entry")
        
        return CPUEntry(**updated_entry)
