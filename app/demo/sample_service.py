"""
Sample microservice demonstrating the logging functionality.
This service simulates a real microservice that uses the logger.
"""

import asyncio
import random
import time
from bson import ObjectId
from app.utils.logger import create_logger

class SampleService:
    """
    Sample service that demonstrates how to use the logger in a real service.
    """
    
    def __init__(self, project_id, service_id, service_name="Sample Service"):
        """
        Initialize the sample service.
        
        Args:
            project_id: The project ID this service belongs to
            service_id: The service ID for this service
            service_name: The name of the service
        """
        self.project_id = project_id
        self.service_id = service_id
        self.service_name = service_name
        self.logger = create_logger(project_id, service_id)
        
    async def run_task(self, task_name, duration=5):
        """
        Run a simulated task and log its progress.
        
        Args:
            task_name: The name of the task
            duration: How long the task should run (in seconds)
        """
        # Log task start - use async logging methods since we're in an async context
        await self.logger.ainfo(f"Starting task: {task_name}")
        
        # Simulate work
        start_time = time.time()
        
        # Log some progress
        await asyncio.sleep(duration * 0.25)
        await self.logger.ainfo(f"Task {task_name} is 25% complete")
        
        # Randomly generate a warning
        if random.random() < 0.3:  # 30% chance
            await self.logger.awarning(f"Resource usage high for task {task_name}")
        
        # More progress
        await asyncio.sleep(duration * 0.25)
        await self.logger.ainfo(f"Task {task_name} is 50% complete")
        
        # Randomly generate an error
        if random.random() < 0.2:  # 20% chance
            try:
                # Simulate an error
                raise ValueError(f"Simulated error in task {task_name}")
            except Exception as e:
                await self.logger.aerror(f"Error in task {task_name}: {str(e)}")
        
        # More progress
        await asyncio.sleep(duration * 0.25)
        await self.logger.ainfo(f"Task {task_name} is 75% complete")
        
        # Final progress
        await asyncio.sleep(duration * 0.25)
        
        # Log completion
        elapsed = time.time() - start_time
        await self.logger.ainfo(f"Task {task_name} completed in {elapsed:.2f} seconds")
        
        return {"task": task_name, "elapsed": elapsed}
    
    async def run_service(self, num_tasks=5):
        """
        Run the service, executing multiple tasks.
        
        Args:
            num_tasks: Number of tasks to run
        """
        await self.logger.ainfo(f"Starting {self.service_name} with {num_tasks} tasks")
        
        # Run multiple tasks
        tasks = []
        for i in range(num_tasks):
            task_name = f"Task-{i+1}"
            duration = random.uniform(1, 3)  # Random duration between 1-3 seconds
            task = asyncio.create_task(self.run_task(task_name, duration))
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        
        # Log service completion
        await self.logger.ainfo(f"Service {self.service_name} completed all {num_tasks} tasks")
        
        return results
    
    def run(self, num_tasks=5):
        """
        Synchronous method to run the service.
        
        Args:
            num_tasks: Number of tasks to run
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.run_service(num_tasks))
