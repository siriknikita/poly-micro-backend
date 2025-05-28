import logging
from typing import Optional, Dict, Any, List
import subprocess
import json
import asyncio
from app.services.log_service import LogService
from app.db.repositories.service_repository import ServiceRepository
from app.schemas.service import Service, ServiceCreate, ServiceUpdate

# Configure logging
logger = logging.getLogger(__name__)

class ServiceManager:
    """
    Service Manager handles operations related to managing services and their Docker containers.
    It provides functionality to:
    - Get service details
    - Execute commands in service containers
    - Manage container lifecycle
    """
    
    def __init__(self, log_service: LogService):
        """
        Initialize the ServiceManager with required dependencies
        
        Args:
            log_service: For logging operations and storing output
        """
        self.log_service = log_service
        
    async def get_service(self, project_id: str, service_id: str) -> Optional[Service]:
        """
        Retrieve service details by ID and project ID
        
        Args:
            project_id: The project the service belongs to
            service_id: The ID of the service to retrieve
            
        Returns:
            Service object if found, None otherwise
        """
        try:
            # Since we don't have direct access to the service repository here,
            # we'll query the database directly through the models
            from app.db.database import get_database
            db = get_database()
            
            # Get service from database
            service_data = await db.services.find_one({"_id": service_id, "project_id": project_id})
            
            if not service_data:
                logger.warning(f"Service {service_id} not found in project {project_id}")
                return None
                
            # Convert to Service model
            return Service(**service_data)
        
        except Exception as e:
            logger.exception(f"Error retrieving service: {str(e)}")
            return None
            
    async def execute_in_container(self, container_name: str, command: List[str]) -> Dict[str, Any]:
        """
        Execute a command in a Docker container
        
        Args:
            container_name: The name of the Docker container
            command: The command to execute as a list of strings
            
        Returns:
            Dictionary containing execution results:
            {
                'success': bool,
                'stdout': str,
                'stderr': str,
                'exit_code': int
            }
        """
        try:
            # Prepare docker exec command
            docker_cmd = ["docker", "exec", container_name] + command
            
            logger.info(f"Executing in container {container_name}: {' '.join(command)}")
            
            # Run the command
            process = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for the command to complete
            stdout, stderr = await process.communicate()
            
            # Process results
            result = {
                'success': process.returncode == 0,
                'stdout': stdout.decode('utf-8'),
                'stderr': stderr.decode('utf-8'),
                'exit_code': process.returncode
            }
            
            if not result['success']:
                logger.error(f"Command failed in container {container_name}: {result['stderr']}")
            
            return result
            
        except Exception as e:
            logger.exception(f"Error executing command in container {container_name}: {str(e)}")
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'exit_code': -1
            }
    
    async def is_container_running(self, container_name: str) -> bool:
        """
        Check if a Docker container is running
        
        Args:
            container_name: The name of the Docker container
            
        Returns:
            True if the container is running, False otherwise
        """
        try:
            # Use docker inspect to check container status
            cmd = ["docker", "inspect", "--format", "{{.State.Running}}", container_name]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Process result
            if process.returncode != 0:
                logger.warning(f"Container {container_name} not found or other error: {stderr.decode('utf-8')}")
                return False
                
            running = stdout.decode('utf-8').strip() == "true"
            return running
            
        except Exception as e:
            logger.exception(f"Error checking container status: {str(e)}")
            return False
