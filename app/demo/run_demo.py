"""
Main demo script for Poly Micro Manager's logging system.

This script demonstrates how to:
1. Create and use logger instances
2. Run multiple microservices that log to the system
3. Query logs through the API
"""

import asyncio
import json
import time
from bson import ObjectId, json_util
from app.utils.logger import create_logger
from app.demo.sample_service import SampleService

# Service names (the IDs will be provided at runtime)
SERVICES = [
    {"id": "service_1", "name": "Auth Service"},
    {"id": "service_2", "name": "User Service"},
    {"id": "service_3", "name": "Order Service"}
]

def parse_json(data):
    """Parse MongoDB JSON data properly"""
    return json.loads(json_util.dumps(data))

async def create_direct_logs(project_id, service_ids):
    """Create logs directly using the logger utility"""
    print("\n=== Creating direct logs ===")
    
    # Create loggers for each service
    loggers = {}
    for service in SERVICES:
        # Use the actual service ID from the database
        actual_service_id = service_ids.get(service["id"])
        logger = create_logger(project_id, actual_service_id)
        loggers[service["id"]] = logger
        print(f"Created logger for {service['name']} with ID {actual_service_id}")
    
    # Log some messages directly
    await loggers["service_1"].ainfo("System initialization complete")
    await loggers["service_1"].ainfo("User authentication enabled", source="auth_module")
    await loggers["service_1"].awarning("High memory usage detected", source="system_monitor")
    
    await loggers["service_2"].ainfo("User profile service started")
    await loggers["service_2"].aerror("Failed to connect to database", source="db_connector")
    
    await loggers["service_3"].ainfo("Order processing ready")
    await loggers["service_3"].adebug("Processing order #12345", func_id="process_order")
    
    print("Created direct logs for all services")
    
async def run_sample_services(project_id, service_ids):
    """Run sample services that will generate logs"""
    print("\n=== Running sample services ===")
    
    # Create and run services
    services = []
    for service in SERVICES:
        # Use the actual service ID from the database
        actual_service_id = service_ids.get(service["id"])
        sample = SampleService(project_id, actual_service_id, service["name"])
        services.append(sample)
        print(f"Created {service['name']} (ID: {actual_service_id})")
    
    # Run all services concurrently
    tasks = []
    for i, service in enumerate(services):
        # Each service runs a different number of tasks
        num_tasks = i + 3  # 3, 4, 5 tasks
        task = asyncio.create_task(service.run_service(num_tasks))
        tasks.append(task)
    
    # Wait for all services to complete
    results = await asyncio.gather(*tasks)
    
    # Print summary
    total_tasks = sum(len(r) for r in results)
    print(f"All services completed with {total_tasks} total tasks")
    
async def run_demo(project_id, service_ids):
    """Main demo function with provided project and service IDs"""
    print("=== Poly Micro Manager Logging Demo ===")
    print(f"Project ID: {project_id}")
    print(f"Services: {', '.join(s['name'] for s in SERVICES)}")
    
    # Step 1: Create direct logs
    await create_direct_logs(project_id, service_ids)
    
    # Step 2: Run sample services that generate logs
    await run_sample_services(project_id, service_ids)
    
    print("\n=== Demo Complete ===")
    print("Check the Poly Micro Manager dashboard to see all logs.")
    print("You can also use the API endpoints to query logs:")
    print(f"- GET /service-logs?project_id={project_id}")
    print(f"- GET /service-logs/project/{project_id}")
    print("- GET /service-logs/service/{service_id}")

if __name__ == "__main__":
    # For standalone testing only
    # In practice, run the demo through run_logging_demo.py
    DEMO_PROJECT_ID = "demo_project_123"  # This won't work properly without setup
    DEMO_SERVICE_IDS = {s["id"]: s["id"] for s in SERVICES}
    asyncio.run(run_demo(DEMO_PROJECT_ID, DEMO_SERVICE_IDS))
