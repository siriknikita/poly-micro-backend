#!/usr/bin/env python3
"""
Demo Setup Script for Poly Micro Manager

This script creates a demo project with sample services, users, and
test data in the database to showcase the functionality of the application.

Run this script with:
python setup_demo.py
"""

import asyncio
import json
import os
import sys
import datetime
import random
from pathlib import Path
from typing import Dict, List, Any, Optional
import time

# Add the current directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import necessary app modules
from app.core.config import settings
from app.db.database import get_database
from app.services.auth_service import AuthService
from app.services.project_service import ProjectService
from app.services.service_service import ServiceService
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.service_repository import ServiceRepository
from app.db.repositories.log_repository import LogRepository
from app.db.repositories.metrics_repository import MetricsRepository
from app.schemas.project import ProjectCreate
from app.schemas.service import ServiceCreate
from app.schemas.user import UserCreate
from app.schemas.log import LogCreate, Severity
from app.schemas.metrics import CPUEntryCreate, CPUDataCreate
from app.core.auth import get_password_hash

# Configure absolute path to the demo project
DEMO_PROJECT_PATH = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "demo-project"

# Demo data
DEMO_USER = {
    "email": "demo@example.com",
    "password": "demo123",
    "username": "demo_user",
    "full_name": "Demo User",
}

DEMO_PROJECT = {
    "name": "Demo Project",
    "description": "A demo project showcasing microservices and test discovery",
    "path": str(DEMO_PROJECT_PATH),
    "tests_dir_path": "tests"
}

DEMO_SERVICES = [
    {
        "name": "x-service",
        "description": "User authentication and management service",
        "url": "http://localhost:8001",
        "port": 8001,
        "status": "Running",
        "health": "Healthy",
        "version": "1.0.0",
        "uptime": "2h 15m",
        "last_deployment": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    },
    {
        "name": "y-service",
        "description": "Product catalog and management service",
        "url": "http://localhost:8002",
        "port": 8002,
        "status": "Running",
        "health": "Warning",
        "version": "1.0.0",
        "uptime": "2h 15m",
        "last_deployment": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }
]


async def ensure_user_exists(user_repo: UserRepository) -> str:
    """Ensure demo user exists and return user ID."""
    print(f"Looking for demo user: {DEMO_USER['email']}...")
    user = await user_repo.get_user_by_email(DEMO_USER["email"])
    
    if not user:
        print("Creating demo user...")
        user_create = UserCreate(
            email=DEMO_USER["email"],
            username=DEMO_USER["username"],
            password=DEMO_USER["password"],
            full_name=DEMO_USER["full_name"]
        )
        # Convert Pydantic model to dict before inserting
        user_dict = user_create.dict(exclude={"password"})
        # Add properly hashed password
        user_dict["hashed_password"] = get_password_hash(DEMO_USER["password"])
        user_dict["created_at"] = datetime.datetime.now().isoformat()
        user_dict["disabled"] = False
        user = await user_repo.create(user_dict)
        # Handle either dictionary or object response
        if isinstance(user, dict):
            user_id = user.get('_id', user.get('id', 'unknown'))
        else:
            user_id = getattr(user, 'id', 'unknown')
        print(f"Demo user created with ID: {user_id}")
    else:
        # Handle either dictionary or object response
        if isinstance(user, dict):
            user_id = user.get('_id', user.get('id', 'unknown'))
        else:
            user_id = getattr(user, 'id', 'unknown')
        print(f"Demo user already exists with ID: {user_id}")
    
    return user_id


async def ensure_project_exists(project_service: ProjectService) -> str:
    """Ensure demo project exists and return project ID."""
    print(f"Looking for demo project: {DEMO_PROJECT['name']}...")
    projects = await project_service.get_all_projects()
    
    # Check if project exists by comparing name
    existing_project = next((p for p in projects if (isinstance(p, dict) and p.get('name') == DEMO_PROJECT["name"]) or 
                              (hasattr(p, 'name') and p.name == DEMO_PROJECT["name"])), None)
    
    if not existing_project:
        print("Creating demo project...")
        project_create = ProjectCreate(
            name=DEMO_PROJECT["name"],
            description=DEMO_PROJECT["description"],
            path=DEMO_PROJECT["path"],
            tests_dir_path=DEMO_PROJECT["tests_dir_path"]
        )
        # Convert Pydantic model to dict for older Pydantic version
        project_dict = project_create.dict()
        # Use the dict for creation
        project = await project_service.create_project(project_dict)
        # Handle either dictionary or object response
        if isinstance(project, dict):
            project_id = project.get('_id', project.get('id', 'unknown'))
        else:
            project_id = getattr(project, 'id', 'unknown')
        print(f"Demo project created with ID: {project_id}")
        return project_id
    else:
        # Handle either dictionary or object response
        if isinstance(existing_project, dict):
            project_id = existing_project.get('_id', existing_project.get('id', 'unknown'))
        else:
            project_id = getattr(existing_project, 'id', 'unknown')
        print(f"Demo project already exists with ID: {project_id}")
        return project_id


async def ensure_services_exist(service_repo: ServiceRepository, project_id: str) -> List[str]:
    """Ensure demo services exist and return service IDs."""
    print("Checking for demo services...")
    
    # Get services collection
    services_collection = service_repo.collection
    
    # Find services for the project directly from MongoDB
    cursor = services_collection.find({"project_id": project_id})
    existing_services = []
    async for service in cursor:
        existing_services.append(service)
        
    service_ids = []
    
    # Check for existing services and create if needed
    for demo_service in DEMO_SERVICES:
        # Check if service exists by comparing name
        existing_service = next((s for s in existing_services if s.get('name') == demo_service["name"]), None)
        
        if not existing_service:
            print(f"Creating service: {demo_service['name']}...")
            # Prepare service data for direct insertion
            service_data = {
                "name": demo_service["name"],
                "description": demo_service["description"],
                "project_id": project_id,
                "url": demo_service["url"],
                "port": demo_service["port"],
                "status": demo_service["status"],
                "health": demo_service["health"],
                "version": demo_service["version"],
                "uptime": demo_service["uptime"],
                "last_deployment": demo_service["last_deployment"]
            }
            
            # Insert directly into MongoDB
            result = await services_collection.insert_one(service_data)
            service_id = str(result.inserted_id)
            print(f"Service {demo_service['name']} created with ID: {service_id}")
            service_ids.append(service_id)
        else:
            service_id = str(existing_service.get('_id'))
            print(f"Service {demo_service['name']} already exists with ID: {service_id}")
            service_ids.append(service_id)
    
    return service_ids


async def create_test_data(db, service_ids, project_id, log_repo):
    """Create test data for the demo services and their logs."""
    print("\nCreating test data for services...")
    
    # Get the test collection
    test_collection = db["poly_micro_tests"]
    
    test_ids = []
    
    # Sample test data for each service
    for idx, service_id in enumerate(service_ids[-2:]):  # Only for the newly created x-service and y-service
        service_name = "x-service" if idx == 0 else "y-service"
        
        # Create 3 tests for each service
        for test_num in range(1, 4):
            test_status = "Passed" if test_num < 3 else "Failed"
            test_data = {
                "name": f"Test {test_num} for {service_name}",
                "description": f"Automated test case #{test_num} for {service_name}",
                "service_id": service_id,
                "project_id": project_id,
                "status": test_status,
                "last_run": datetime.datetime.now().isoformat(),
                "duration": f"{test_num * 0.5:.1f}s",
                "type": "Unit Test" if test_num == 1 else "Integration Test" if test_num == 2 else "E2E Test"
            }
            
            # Check if test already exists
            existing_test = await test_collection.find_one({
                "name": test_data["name"],
                "service_id": service_id
            })
            
            test_id = None
            
            if not existing_test:
                result = await test_collection.insert_one(test_data)
                test_id = str(result.inserted_id)
                print(f"Created test '{test_data['name']}' with ID: {test_id}")
            else:
                test_id = str(existing_test.get('_id'))
                print(f"Test '{test_data['name']}' already exists with ID: {test_id}")
                
            test_ids.append((test_id, test_data, service_id))
    
    # Create logs for tests
    await create_test_logs(log_repo, test_ids, project_id)
    
    print("Test data creation complete")
    
    return test_ids


async def create_test_logs(log_repo, test_ids, project_id):
    """Create logs for test executions."""
    print("\nCreating test logs...")
    
    # Define possible log messages for each test status
    passed_messages = [
        "Test executed successfully",
        "All assertions passed",
        "Test completed without errors",
        "Verified expected behavior",
        "All endpoints responded correctly"
    ]
    
    failed_messages = [
        "Test failed: Expected response code 200, got 500",
        "Assertion error: Expected '{}' but got '{}'",
        "Service connection timed out during test",
        "Failed to validate response data structure",
        "Error in test setup: database connection failed"
    ]
    
    # Create 3-5 logs for each test with appropriate severity based on status
    for test_id, test_data, service_id in test_ids:
        # Determine number of logs for this test
        num_logs = random.randint(3, 5)
        
        # Create logs with timestamps spaced throughout the test execution
        test_start_time = datetime.datetime.fromisoformat(test_data["last_run"])
        test_duration_seconds = float(test_data["duration"].replace('s', ''))
        
        for i in range(num_logs):
            # Calculate a timestamp within the test duration
            log_time_offset = (i / num_logs) * test_duration_seconds
            log_timestamp = test_start_time + datetime.timedelta(seconds=log_time_offset)
            
            # Determine severity and message based on test status
            if test_data["status"] == "Passed":
                # For passed tests: mostly INFO with occasional DEBUG
                if i == 0:
                    severity = Severity.INFO
                    message = f"Started test: {test_data['name']}"
                elif i == num_logs - 1:
                    severity = Severity.INFO
                    message = f"Test completed successfully in {test_data['duration']}"
                else:
                    severity = random.choice([Severity.DEBUG, Severity.INFO])
                    message = random.choice(passed_messages)
            else:
                # For failed tests: DEBUG at start, ERROR at end, mix in between
                if i == 0:
                    severity = Severity.INFO
                    message = f"Started test: {test_data['name']}"
                elif i == num_logs - 1:
                    severity = Severity.ERROR
                    message = random.choice(failed_messages).format("expected_value", "actual_value")
                else:
                    severity = random.choice([Severity.DEBUG, Severity.INFO, Severity.WARN])
                    message = f"Executing test step {i}"
            
            # Create the log entry
            log_data = LogCreate(
                project_id=project_id,
                service_id=service_id,
                test_id=test_id,
                message=message,
                severity=severity,
                timestamp=log_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                source=test_data["type"]
            )
            
            # Pass the LogCreate object directly
            await log_repo.create_log(log_data)
            
    print(f"Created {len(test_ids) * random.randint(3, 5)} test logs")


async def create_system_metrics(metrics_repo, project_id, service_ids):
    """Create system metrics data for the demo services."""
    print("\nCreating system metrics data...")
    
    # Generate metrics for each service
    for service_id in service_ids:
        # Determine service name based on index in service_ids list
        # This assumes service_ids order matches DEMO_SERVICES order
        idx = service_ids.index(service_id)
        service_name = DEMO_SERVICES[idx]["name"]
        
        # Create metrics data covering the last 24 hours with 15-minute intervals
        now = datetime.datetime.now()
        
        # Calculate a baseline for this service
        cpu_baseline = random.uniform(10, 30)  # Base CPU load varies between services
        memory_baseline = random.uniform(5, 100)  # Base memory usage in MB
        threads_baseline = random.randint(4, 12)  # Base thread count
        
        # Create the metrics entry directly as a dictionary
        cpu_entry_dict = {
            "project_id": project_id,
            "service_name": service_name,
            "data": []
        }
        
        # Generate data points for the past 24 hours (96 points at 15-minute intervals)
        for i in range(96):
            # Calculate time for this data point (96 intervals of 15 minutes = 24 hours)
            time_offset = 96 - i
            point_time = now - datetime.timedelta(minutes=15 * time_offset)
            
            # Add daily pattern - higher usage during work hours (9am-5pm)
            hour = point_time.hour
            day_factor = 1.5 if 9 <= hour <= 17 else 0.8
            
            # Add some randomness with occasional spikes
            random_factor = random.uniform(0.85, 1.15)
            spike = random.random() > 0.95  # 5% chance of a spike
            spike_factor = random.uniform(1.5, 2.0) if spike else 1.0
            
            # Calculate metrics with patterns
            cpu_load = min(99, cpu_baseline * day_factor * random_factor * spike_factor)
            memory_usage = min(1024, memory_baseline * day_factor * random_factor * spike_factor)
            threads = max(1, round(threads_baseline * day_factor * random_factor))
            
            # Create data point directly as a dictionary
            data_point = {
                "time": point_time.strftime("%Y-%m-%d %H:%M:%S"),
                "load": round(cpu_load, 2),
                "memory": round(memory_usage, 2),
                "threads": threads
            }
            
            # Add data point to the entry
            cpu_entry_dict["data"].append(data_point)
        
        # Now directly insert the dict into MongoDB
        result = await metrics_repo.collection.insert_one(cpu_entry_dict)
        print(f"Created metrics data for {service_name} with {len(cpu_entry_dict['data'])} data points")
    
    print(f"System metrics creation complete for {len(service_ids)} services")


async def create_project_event_logs(log_repo, project_id, service_ids):
    """Create logs for regular project events."""
    print("\nCreating project event logs...")
    
    # Define events for the project
    events = [
        # Project lifecycle events
        {"message": "Project initialization started", "severity": Severity.INFO, "source": "Project Setup"},
        {"message": "Project configuration loaded", "severity": Severity.INFO, "source": "Project Setup"},
        {"message": "Project dependencies installed", "severity": Severity.INFO, "source": "Project Setup"},
        {"message": "Local development environment started", "severity": Severity.INFO, "source": "Development"},
        
        # Build/deployment events
        {"message": "Project build started", "severity": Severity.INFO, "source": "CI/CD"},
        {"message": "Project build completed successfully", "severity": Severity.INFO, "source": "CI/CD"},
        {"message": "Deployment to staging started", "severity": Severity.INFO, "source": "Deployment"},
        {"message": "Deployment to staging completed", "severity": Severity.INFO, "source": "Deployment"},
        
        # Warning events
        {"message": "High CPU usage detected in development environment", "severity": Severity.WARN, "source": "Monitoring"},
        {"message": "Slow database response time detected", "severity": Severity.WARN, "source": "Performance"},
        {"message": "Memory usage approaching threshold", "severity": Severity.WARN, "source": "Monitoring"},
        
        # Error events
        {"message": "Failed to connect to external API", "severity": Severity.ERROR, "source": "Integration"},
        {"message": "Database migration script failed", "severity": Severity.ERROR, "source": "Database"}
    ]
    
    # Service-specific events for each service
    service_events = [
        {"message": "Service started successfully", "severity": Severity.INFO, "source": "Service Lifecycle"},
        {"message": "Service configuration loaded", "severity": Severity.INFO, "source": "Service Lifecycle"},
        {"message": "Health check passed", "severity": Severity.INFO, "source": "Monitoring"},
        {"message": "API endpoint response time improved by 15%", "severity": Severity.INFO, "source": "Performance"},
        {"message": "Service restarted due to configuration change", "severity": Severity.INFO, "source": "Service Lifecycle"},
        {"message": "High latency detected on API endpoint", "severity": Severity.WARN, "source": "Performance"},
        {"message": "Service approaching memory limit", "severity": Severity.WARN, "source": "Resource Usage"},
        {"message": "Service crashed unexpectedly", "severity": Severity.ERROR, "source": "Service Lifecycle"},
        {"message": "Failed to process incoming message", "severity": Severity.ERROR, "source": "Message Queue"}
    ]
    
    # Create project-level logs
    now = datetime.datetime.now()
    for i, event in enumerate(events):
        # Create timestamps spread over the last 7 days
        log_time = now - datetime.timedelta(days=random.randint(0, 7), 
                                          hours=random.randint(0, 23), 
                                          minutes=random.randint(0, 59))
        
        log_data = LogCreate(
            project_id=project_id,
            service_id=random.choice(service_ids) if random.random() > 0.3 else service_ids[0],  # Some logs associated with services
            message=event["message"],
            severity=event["severity"],
            timestamp=log_time.strftime("%Y-%m-%d %H:%M:%S"),
            source=event["source"]
        )
        
        # Pass the LogCreate object directly
        await log_repo.create_log(log_data)
    
    # Create service-specific logs for each service
    for service_id in service_ids:
        for i, event in enumerate(random.sample(service_events, k=min(5, len(service_events)))):
            # Create timestamps spread over the last 3 days
            log_time = now - datetime.timedelta(days=random.randint(0, 3), 
                                              hours=random.randint(0, 23), 
                                              minutes=random.randint(0, 59))
            
            log_data = LogCreate(
                project_id=project_id,
                service_id=service_id,
                message=event["message"],
                severity=event["severity"],
                timestamp=log_time.strftime("%Y-%m-%d %H:%M:%S"),
                source=event["source"]
            )
            
            # Pass the LogCreate object directly
            await log_repo.create_log(log_data)
    
    print(f"Created {len(events) + len(service_ids) * 5} project and service event logs")


async def main():
    """Main function to set up all demo data."""
    print("=" * 50)
    print("POLY MICRO MANAGER - DEMO SETUP")
    print("=" * 50)
    print()
    
    # Initialize database connection
    print("\nConnecting to database...")
    db = get_database()
    
    # Initialize repositories
    user_repo = UserRepository(db)
    project_repo = ProjectRepository(db)
    service_repo = ServiceRepository(db)
    log_repo = LogRepository(db)
    metrics_repo = MetricsRepository(db)
    
    # Initialize services
    auth_service = AuthService(user_repo)
    project_service = ProjectService(project_repo)
    service_service = ServiceService(service_repo, project_repo)
    
    # Setup demo user
    user_id = await ensure_user_exists(user_repo)
    
    # Setup demo project
    project_id = await ensure_project_exists(project_service)
    
    # Setup demo services
    service_ids = await ensure_services_exist(service_repo, project_id)
    
    # Create test data for services
    test_ids = await create_test_data(db, service_ids, project_id, log_repo)
    
    # Create project and service event logs
    await create_project_event_logs(log_repo, project_id, service_ids)
    
    # Create system metrics data for services
    await create_system_metrics(metrics_repo, project_id, service_ids)
    
    print("\n" + "=" * 50)
    print("DEMO SETUP COMPLETE")
    print("=" * 50)
    print(f"\nDemo User: {DEMO_USER['username']} (Password: {DEMO_USER['password']})")
    print(f"Demo Project ID: {project_id}")
    print(f"Demo Service IDs: {', '.join(service_ids)}")
    print(f"Demo Test Data and Logs: Created")
    print(f"Demo System Metrics: Created")
    print("\nYou can now showcase the application to your teacher!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
