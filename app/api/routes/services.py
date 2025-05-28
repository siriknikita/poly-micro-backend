from fastapi import APIRouter, Depends, Path, Query, HTTPException, status
from typing import List, Dict, Any
import subprocess
import asyncio
import os
import json
import tempfile
import time
from datetime import datetime
import docker
import tarfile
import shutil

from app.services.service_service import ServiceService
from app.services.test_service import TestService
from app.services.project_service import ProjectService
from app.api.dependencies import get_service_service, get_test_service, get_project_service
from app.schemas.service import Service, ServiceCreate, ServiceUpdate
from app.schemas.test_item import TestItem
from app.schemas.service_test_item import ServiceTestItem
from app.schemas.service_tests import ServiceTestsResponse
from app.schemas.test import TestRunResult, TestStatus

router = APIRouter()

@router.get("/", response_model=List[Service])
async def get_all_services(
    service_service: ServiceService = Depends(get_service_service)
):
    """Get all services across all projects"""
    return await service_service.get_all_services()

@router.get("/project/{project_id}", response_model=List[ServiceTestItem])
async def get_services_by_project(
    project_id: str = Path(..., description="The ID of the project to get services for"),
    service_service: ServiceService = Depends(get_service_service)
):
    """Get all services for a specific project as TestItems"""
    items = await service_service.get_services_by_project(project_id)
    print(f"API Route: Retrieved {len(items)} TestItems")
    
    # Convert TestItem to ServiceTestItem for API response
    result = []
    for item in items:
        service_item = ServiceTestItem(
            id=item.id,
            name=item.name,
            type=item.type,
            project_id=item.projectId,  # Convert camelCase to snake_case
            children=item.children,
            status=item.status,
            version=item.version,
            last_deployment=item.lastDeployed,  # Convert camelCase to snake_case
            port=item.port,
            url=item.url,
            health=item.health,
            uptime=item.uptime,
            container_name=getattr(item, 'containerName', None)  # Include container name if it exists
        )
        result.append(service_item)
    
    print(f"API Route: Converted to {len(result)} ServiceTestItems")
    return result

@router.get("/{service_id}", response_model=Service)
async def get_service(
    service_id: str = Path(..., description="The ID of the service to get"),
    service_service: ServiceService = Depends(get_service_service)
):
    """Get a specific service by ID"""
    return await service_service.get_service_by_id(service_id)

@router.post("/", response_model=Service, status_code=status.HTTP_201_CREATED)
async def create_service(
    service: ServiceCreate,
    service_service: ServiceService = Depends(get_service_service)
):
    """Create a new service"""
    return await service_service.create_service(service)

@router.put("/{service_id}", response_model=Service)
async def update_service(
    service: ServiceUpdate,
    service_id: str = Path(..., description="The ID of the service to update"),
    service_service: ServiceService = Depends(get_service_service)
):
    """Update a service"""
    return await service_service.update_service(service_id, service)

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: str = Path(..., description="The ID of the service to delete"),
    service_service: ServiceService = Depends(get_service_service)
):
    """Delete a service"""
    await service_service.delete_service(service_id)
    return None

@router.get("/tests/{service_id}", response_model=ServiceTestsResponse)
async def get_service_tests(
    service_id: str = Path(..., description="The ID of the service to get tests for"),
    service_service: ServiceService = Depends(get_service_service),
    test_service: TestService = Depends(get_test_service),
    project_service: ProjectService = Depends(get_project_service)
):
    """Get all available tests for a specific service"""
    # Get the service details
    service = await service_service.get_service_by_id(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Get the project details to get the project path and tests directory path
    project = await project_service.get_project_by_id(service.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Collect the tests for the service
    test_results = await test_service.collect_service_tests(
        project_id=project.id,
        service_id=service.id,
        service_name=service.name,
        project_path=project.path,
        tests_dir_path=project.tests_dir_path
    )
    
    return test_results

@router.post("/run-tests/{service_id}", response_model=Dict[str, Any])
async def run_service_tests(
    service_id: str = Path(..., description="The ID of the service to run tests for"),
    service_service: ServiceService = Depends(get_service_service),
    project_service: ProjectService = Depends(get_project_service)
):
    """Run tests for a specific service using direct Docker command execution"""
    # Get the service details
    service = await service_service.get_service_by_id(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Get the project details
    project = await project_service.get_project_by_id(service.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # For now, we'll use a fixed command as specified
    container_name = f"demo-{service.name}"
    
    # Create timestamp for report saving
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = os.path.join(os.getcwd(), "tests-results")
    os.makedirs(report_dir, exist_ok=True)
    
    local_report_path = os.path.join(report_dir, f"report-{service.name}-{timestamp}.json")
    
    try:
        # Initialize Docker client using Docker socket
        # This requires the Docker socket to be mounted into the container
        try:
            docker_client = docker.from_env()
            # Check if Docker is available by listing containers
            docker_client.ping()
        except Exception as e:
            return {
                "success": False,
                "service_id": service_id,
                "service_name": service.name,
                "test_run_id": "error",
                "status": "ERROR",
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "duration_seconds": 0,
                "error": f"Docker is not accessible. Make sure the backend container has access to the Docker socket. Error: {str(e)}"
            }

        # Check if the target container exists
        try:
            target_container = docker_client.containers.get(container_name)
        except docker.errors.NotFound:
            return {
                "success": False,
                "service_id": service_id,
                "service_name": service.name,
                "test_run_id": "error",
                "status": "ERROR",
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "duration_seconds": 0,
                "error": f"Container '{container_name}' not found. Make sure the service container is running."
            }

        start_time = datetime.now()
        
        # Execute pytest in the container using Docker Python SDK
        exec_command = ["pytest", f"/tests/{service.name}", "--json-report", "--json-report-file=/tmp/report.json"]
        exec_result = target_container.exec_run(exec_command)
        
        stdout = exec_result.output
        stderr = b"" if exec_result.exit_code == 0 else stdout  # In Docker SDK, stderr is often included in stdout
        exit_code = exec_result.exit_code
        
        end_time = datetime.now()
        duration_seconds = (end_time - start_time).total_seconds()
        
        # Copy the report from the container to host using Docker SDK
        # First, create a temporary file to store the report
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Use Docker SDK's get_archive to copy the file from container
        try:
            # Get the archive stream from the container
            bits, stat = target_container.get_archive('/tmp/report.json')
            
            # First, write the tar stream to a temporary file
            with open(temp_path, 'wb') as f:
                for chunk in bits:
                    f.write(chunk)
            
            # Then extract the contents using tarfile module
            # Create the directory for the report if it doesn't exist
            os.makedirs(os.path.dirname(local_report_path), exist_ok=True)
            
            with tarfile.open(temp_path) as tar:
                # Find the report.json file in the archive
                report_file = None
                for member in tar.getmembers():
                    if member.name == 'report.json' or member.name.endswith('/report.json'):
                        report_file = member
                        break
                
                if report_file:
                    # Extract the report file to the desired location
                    with tar.extractfile(report_file) as f_in:
                        with open(local_report_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    copy_success = True
                else:
                    print("Report file not found in the archive")
                    copy_success = False
            
            # Clean up the temporary file
            os.unlink(temp_path)
        except Exception as e:
            print(f"Error copying report file: {str(e)}")
            copy_success = False
        
        success = exit_code == 0 and copy_success
        
        # Parse the JSON report if available
        json_report = None
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        # Add a retry mechanism for reading the JSON report
        max_retries = 3
        retry_delay = 0.5  # seconds
        
        for attempt in range(max_retries):
            try:
                if os.path.exists(local_report_path):
                    # Check if file has content
                    if os.path.getsize(local_report_path) > 0:
                        with open(local_report_path, 'r') as f:
                            json_report = json.load(f)
                        
                        if json_report and 'summary' in json_report:
                            total_tests = json_report['summary'].get('total', 0)
                            passed_tests = json_report['summary'].get('passed', 0)
                            failed_tests = json_report['summary'].get('failed', 0)
                            break  # Successfully parsed, exit the retry loop
                    else:
                        print(f"Report file is empty, retrying ({attempt+1}/{max_retries})")
                else:
                    print(f"Report file doesn't exist yet, retrying ({attempt+1}/{max_retries})")
                
                # Wait before the next retry
                if attempt < max_retries - 1:  # Don't sleep on the last attempt
                    time.sleep(retry_delay)
            except Exception as e:
                print(f"Error parsing JSON report (attempt {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:  # Don't sleep on the last attempt
                    time.sleep(retry_delay)
        
        # Return results with enhanced information
        return {
            "success": success,
            "service_id": service_id,
            "service_name": service.name,
            "test_run_id": timestamp,  # Use timestamp as a run ID
            "status": "PASSED" if success and failed_tests == 0 else "FAILED",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "duration_seconds": duration_seconds,
            "stdout": stdout.decode("utf-8", errors="replace") if stdout else "",
            "stderr": stderr.decode("utf-8", errors="replace") if stderr else "",
            "report_path": local_report_path,
            "timestamp": timestamp,
            "json_report": json_report
        }
    
    except Exception as e:
        error_message = str(e)
        # Return a structured error response rather than raising an exception
        # This makes it easier for the frontend to display helpful error messages
        return {
            "success": False,
            "service_id": service_id,
            "service_name": service.name,
            "test_run_id": "error",
            "status": "ERROR",
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "duration_seconds": 0,
            "error": f"Error running tests: {error_message}"
        }
