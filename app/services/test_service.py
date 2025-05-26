import os
import uuid
import json
import asyncio
import logging
import subprocess
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from app.schemas.test import TestRunCreate, TestRunResult, TestStatus, TestRunUpdate
from app.schemas.log import LogCreate, Severity
from app.services.log_service import LogService
from app.schemas.test_item import TestItem
from app.schemas.service_tests import ServiceTestsResponse
from app.utils.logger import create_logger
from app.db.database import get_database

logger = logging.getLogger(__name__)

class TestService:
    """Service for executing tests and managing test results"""
    
    def __init__(self, log_service: LogService):
        """Initialize test service with required dependencies"""
        self.log_service = log_service
        self.test_results_dir = os.path.join(os.getcwd(), "test_results")
        self.service_tests_dir = os.path.join(os.getcwd(), "service_tests")
        
        # Ensure test results directory exists
        os.makedirs(self.test_results_dir, exist_ok=True)
        os.makedirs(self.service_tests_dir, exist_ok=True)
        
        # Database connection
        self.db = get_database()
    
    async def create_test_run(self, test_run: TestRunCreate) -> TestRunResult:
        """Create a new test run and return its metadata"""
        run_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # Create test run result object
        test_result = TestRunResult(
            id=run_id,
            project_id=test_run.project_id,
            service_id=test_run.service_id,
            test_path=test_run.test_path,
            test_id=test_run.test_id,
            status=TestStatus.PENDING,
            start_time=start_time,
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            error_tests=0,
            skipped_tests=0,
            log_ids=[]
        )
        
        # Create directory for test results
        project_dir = os.path.join(self.test_results_dir, test_run.project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        test_run_dir = os.path.join(project_dir, run_id)
        os.makedirs(test_run_dir, exist_ok=True)
        os.makedirs(os.path.join(test_run_dir, "logs"), exist_ok=True)
        
        # Save initial test run metadata
        self._save_test_run_metadata(test_result)
        
        # Create a log entry for test start
        log_entry = await self.log_service.create_log(
            LogCreate(
                project_id=test_run.project_id,
                service_id=test_run.service_id,
                test_id=run_id,
                message=f"Test run started: {test_run.test_path}",
                severity=Severity.INFO,
                source="test_service",
                metadata={
                    "test_path": test_run.test_path,
                    "test_id": test_run.test_id
                }
            )
        )
        
        test_result.log_ids.append(log_entry.id)
        self._save_test_run_metadata(test_result)
        
        return test_result
    
    async def execute_test_run(self, test_run_id: str) -> TestRunResult:
        """Execute a test run in a Docker container"""
        # Load test run metadata
        test_run = await self.get_test_run(test_run_id)
        if not test_run:
            raise ValueError(f"Test run with ID {test_run_id} not found")
        
        # Update status to running
        test_run.status = TestStatus.RUNNING
        self._save_test_run_metadata(test_run)
        
        try:
            # Execute the test in Docker container
            await self._run_test_in_container(test_run)
            
            # Parse test results and update test run metadata
            updated_test_run = await self._process_test_results(test_run)
            
            return updated_test_run
            
        except Exception as e:
            logger.exception(f"Error executing test run {test_run_id}: {str(e)}")
            
            # Update test run with error status
            test_run.status = TestStatus.ERROR
            test_run.end_time = datetime.now()
            test_run.duration_seconds = (test_run.end_time - test_run.start_time).total_seconds()
            
            # Log the error
            log_entry = await self.log_service.create_log(
                LogCreate(
                    project_id=test_run.project_id,
                    service_id=test_run.service_id,
                    test_id=test_run_id,
                    message=f"Test execution error: {str(e)}",
                    severity=Severity.ERROR,
                    source="test_service",
                    metadata={
                        "error": str(e)
                    }
                )
            )
            
            test_run.log_ids.append(log_entry.id)
            self._save_test_run_metadata(test_run)
            
            return test_run
    
    async def _run_test_in_container(self, test_run: TestRunResult) -> None:
        """Run the test in a Docker container and collect output"""
        logger.info(f"Running test in container: {test_run.id}")
        
        test_path = test_run.test_path
        test_id = test_run.test_id
        
        # Build the pytest command
        pytest_cmd = ["pytest", test_path]
        
        # Add specific test ID if provided
        if test_id:
            pytest_cmd.append(f"::{test_id}")
        
        # Add options for JSON report
        report_file = f"/tmp/test-report-{test_run.id}.json"
        pytest_cmd.extend(["-v", f"--json-report --json-report-file={report_file}"])
        
        # Docker command to run the test
        docker_cmd = [
            "docker", "exec",
            test_run.service_id,
            "bash", "-c", " ".join(pytest_cmd)
        ]
        
        logger.info(f"Executing command: {' '.join(docker_cmd)}")
        
        # Execute the command and capture output
        process = await asyncio.create_subprocess_exec(
            *docker_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # Get the project and test run directories
        project_dir = os.path.join(self.test_results_dir, test_run.project_id)
        test_run_dir = os.path.join(project_dir, test_run.id)
        logs_dir = os.path.join(test_run_dir, "logs")
        
        # Save stdout and stderr
        with open(os.path.join(logs_dir, "stdout.log"), "wb") as f:
            f.write(stdout)
        
        with open(os.path.join(logs_dir, "stderr.log"), "wb") as f:
            f.write(stderr)
        
        # Copy the JSON report from the container
        copy_cmd = [
            "docker", "cp",
            f"{test_run.service_id}:{report_file}",
            os.path.join(test_run_dir, "report.json")
        ]
        
        try:
            copy_process = await asyncio.create_subprocess_exec(
                *copy_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await copy_process.communicate()
        except Exception as e:
            logger.error(f"Failed to copy test report: {str(e)}")
            
            # Create a log for the stdout
            stdout_log = await self.log_service.create_log(
                LogCreate(
                    project_id=test_run.project_id,
                    service_id=test_run.service_id,
                    test_id=test_run.id,
                    message="Test execution stdout",
                    severity=Severity.INFO,
                    source="test_execution",
                    metadata={
                        "content": stdout.decode('utf-8', errors='replace')
                    }
                )
            )
            
            # Create a log for the stderr
            stderr_log = await self.log_service.create_log(
                LogCreate(
                    project_id=test_run.project_id,
                    service_id=test_run.service_id,
                    test_id=test_run.id,
                    message="Test execution stderr",
                    severity=Severity.WARNING if stderr else Severity.INFO,
                    source="test_execution",
                    metadata={
                        "content": stderr.decode('utf-8', errors='replace')
                    }
                )
            )
            
            test_run.log_ids.extend([stdout_log.id, stderr_log.id])
    
    async def _process_test_results(self, test_run: TestRunResult) -> TestRunResult:
        """Process test results and update test run metadata"""
        project_dir = os.path.join(self.test_results_dir, test_run.project_id)
        test_run_dir = os.path.join(project_dir, test_run.id)
        report_path = os.path.join(test_run_dir, "report.json")
        
        # Check if report exists
        if os.path.exists(report_path):
            try:
                with open(report_path, 'r') as f:
                    report_data = json.load(f)
                
                # Extract test statistics
                summary = report_data.get('summary', {})
                
                # Update test run with results
                test_run.total_tests = summary.get('total', 0)
                test_run.passed_tests = summary.get('passed', 0)
                test_run.failed_tests = summary.get('failed', 0)
                test_run.error_tests = summary.get('error', 0)
                test_run.skipped_tests = summary.get('skipped', 0)
                
                # Determine overall status
                if test_run.failed_tests > 0 or test_run.error_tests > 0:
                    test_run.status = TestStatus.FAILED
                else:
                    test_run.status = TestStatus.PASSED
                
                # Create logs for test results
                test_cases = report_data.get('tests', [])
                for test_case in test_cases:
                    # Create a log entry for each test case
                    outcome = test_case.get('outcome', 'unknown')
                    test_name = test_case.get('nodeid', 'unknown')
                    
                    severity = Severity.INFO
                    if outcome == 'failed':
                        severity = Severity.ERROR
                    elif outcome == 'skipped':
                        severity = Severity.WARNING
                    
                    log_entry = await self.log_service.create_log(
                        LogCreate(
                            project_id=test_run.project_id,
                            service_id=test_run.service_id,
                            test_id=test_run.id,
                            message=f"Test case {test_name}: {outcome}",
                            severity=severity,
                            source="test_result",
                            metadata=test_case
                        )
                    )
                    
                    test_run.log_ids.append(log_entry.id)
                
            except Exception as e:
                logger.error(f"Error processing test results: {str(e)}")
                test_run.status = TestStatus.ERROR
                
                # Log the error
                log_entry = await self.log_service.create_log(
                    LogCreate(
                        project_id=test_run.project_id,
                        service_id=test_run.service_id,
                        test_id=test_run.id,
                        message=f"Error processing test results: {str(e)}",
                        severity=Severity.ERROR,
                        source="test_service",
                        metadata={
                            "error": str(e)
                        }
                    )
                )
                
                test_run.log_ids.append(log_entry.id)
        else:
            # No report file found
            logger.warning(f"No test report found for test run {test_run.id}")
            test_run.status = TestStatus.ERROR
            
            # Log the error
            log_entry = await self.log_service.create_log(
                LogCreate(
                    project_id=test_run.project_id,
                    service_id=test_run.service_id,
                    test_id=test_run.id,
                    message="No test report found",
                    severity=Severity.ERROR,
                    source="test_service"
                )
            )
            
            test_run.log_ids.append(log_entry.id)
        
        # Update end time and duration
        test_run.end_time = datetime.now()
        test_run.duration_seconds = (test_run.end_time - test_run.start_time).total_seconds()
        
        # Save updated test run metadata
        self._save_test_run_metadata(test_run)
        
        # Create a log entry for test completion
        log_entry = await self.log_service.create_log(
            LogCreate(
                project_id=test_run.project_id,
                service_id=test_run.service_id,
                test_id=test_run.id,
                message=f"Test run completed: {test_run.status.value}",
                severity=Severity.INFO if test_run.status == TestStatus.PASSED else Severity.WARNING,
                source="test_service",
                metadata={
                    "status": test_run.status.value,
                    "total_tests": test_run.total_tests,
                    "passed_tests": test_run.passed_tests,
                    "failed_tests": test_run.failed_tests,
                    "error_tests": test_run.error_tests,
                    "skipped_tests": test_run.skipped_tests,
                    "duration_seconds": test_run.duration_seconds
                }
            )
        )
        
        test_run.log_ids.append(log_entry.id)
        self._save_test_run_metadata(test_run)
        
        return test_run
    
    async def get_test_run(self, test_run_id: str) -> Optional[TestRunResult]:
        """Get a test run by its ID"""
        # Search for the test run in all project directories
        for project_id in os.listdir(self.test_results_dir):
            project_dir = os.path.join(self.test_results_dir, project_id)
            if not os.path.isdir(project_dir):
                continue
                
            test_run_dir = os.path.join(project_dir, test_run_id)
            if os.path.isdir(test_run_dir):
                metadata_path = os.path.join(test_run_dir, "metadata.json")
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                        return TestRunResult(**metadata)
        
        return None
    
    async def get_test_runs_by_project(self, project_id: str) -> List[TestRunResult]:
        """Get all test runs for a project"""
        project_dir = os.path.join(self.test_results_dir, project_id)
        if not os.path.exists(project_dir):
            return []
            
        test_runs = []
        for test_run_id in os.listdir(project_dir):
            test_run_dir = os.path.join(project_dir, test_run_id)
            if not os.path.isdir(test_run_dir):
                continue
                
            metadata_path = os.path.join(test_run_dir, "metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    test_runs.append(TestRunResult(**metadata))
        
        # Sort by start time (newest first)
        test_runs.sort(key=lambda x: x.start_time, reverse=True)
        return test_runs
    
    async def get_test_runs_by_service(self, service_id: str) -> List[TestRunResult]:
        """Get all test runs for a service"""
        test_runs = []
        
        # Search all project directories
        for project_id in os.listdir(self.test_results_dir):
            project_dir = os.path.join(self.test_results_dir, project_id)
            if not os.path.isdir(project_dir):
                continue
                
            # Search for test runs in this project
            for test_run_id in os.listdir(project_dir):
                test_run_dir = os.path.join(project_dir, test_run_id)
                if not os.path.isdir(test_run_dir):
                    continue
                    
                metadata_path = os.path.join(test_run_dir, "metadata.json")
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                        test_run = TestRunResult(**metadata)
                        if test_run.service_id == service_id:
                            test_runs.append(test_run)
        
        # Sort by start time (newest first)
        test_runs.sort(key=lambda x: x.start_time, reverse=True)
        return test_runs
    
    async def update_test_run(self, test_run_id: str, update_data: TestRunUpdate) -> Optional[TestRunResult]:
        """Update a test run"""
        test_run = await self.get_test_run(test_run_id)
        if not test_run:
            return None
            
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(test_run, field, value)
            
        # Save updated test run metadata
        self._save_test_run_metadata(test_run)
        
        return test_run
    
    def _save_test_run_metadata(self, test_run: TestRunResult) -> None:
        """Save test run metadata to disk"""
        project_dir = os.path.join(self.test_results_dir, test_run.project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        test_run_dir = os.path.join(project_dir, test_run.id)
        os.makedirs(test_run_dir, exist_ok=True)
        
        metadata_path = os.path.join(test_run_dir, "metadata.json")
        with open(metadata_path, 'w') as f:
            # Convert to dict and handle datetime serialization
            test_run_dict = test_run.dict()
            if test_run.start_time:
                test_run_dict["start_time"] = test_run.start_time.isoformat()
            if test_run.end_time:
                test_run_dict["end_time"] = test_run.end_time.isoformat()
                
            json.dump(test_run_dict, f, indent=2)

    async def collect_service_tests(self, project_id: str, service_id: str, service_name: str, project_path: str, tests_dir_path: str) -> ServiceTestsResponse:
        """Collect all available tests for a specific service using pytest --collect-only
        and also check the database for manually created tests
        
        Args:
            project_id: The ID of the project
            service_id: The ID of the service to collect tests for
            service_name: The name of the service
            project_path: The absolute path to the project root
            tests_dir_path: The relative path to the tests directory
        
        Returns:
            ServiceTestsResponse containing the collected tests
        """
        # Create a custom logger for this operation
        custom_logger = create_logger(project_id, service_id)
        await custom_logger.ainfo(f"Collecting tests for service {service_name}")
        
        # Form the full path to the tests directory
        service_tests_path = os.path.join(project_path, tests_dir_path, service_name)
        
        # Create the response object
        response = ServiceTestsResponse(
            service_id=service_id,
            service_name=service_name,
            project_id=project_id,
            tests=[],
            metadata={
                "tests_path": service_tests_path,
                "collection_command": f"pytest {service_tests_path} --collect-only -q"
            }
        )
        
        tests_found = False
        
        try:
            # First, try to collect tests from the filesystem using pytest
            if os.path.exists(service_tests_path):
                # Run pytest --collect-only to get all available tests
                await custom_logger.ainfo(f"Running pytest --collect-only on {service_tests_path}")
                process = await asyncio.create_subprocess_exec(
                    "pytest", 
                    service_tests_path, 
                    "--collect-only", 
                    "-q",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                # Parse the output to extract test information
                if process.returncode == 0:
                    # Extract tests from the output
                    test_nodeids = self._parse_pytest_collect_output(stdout.decode("utf-8"))
                    
                    # Create TestItem objects for each test
                    for i, nodeid in enumerate(test_nodeids):
                        test_item = self._create_test_item_from_nodeid(nodeid, i)
                        response.tests.append(test_item)
                        
                    await custom_logger.ainfo(f"Collected {len(response.tests)} tests from filesystem for {service_name}")
                    tests_found = len(response.tests) > 0
                else:
                    error_message = stderr.decode("utf-8")
                    await custom_logger.aerror(f"Error collecting tests from filesystem: {error_message}")
                    response.metadata["filesystem_error"] = error_message
            else:
                await custom_logger.awarning(f"Tests directory does not exist: {service_tests_path}")
                response.metadata["filesystem_error"] = f"Tests directory does not exist: {service_tests_path}"
            
            # Next, try to fetch tests from the database
            test_collection = self.db["tests"]
            await custom_logger.ainfo(f"Checking database for tests for service_id {service_id}")
            
            # Query for tests in the database for this service
            cursor = test_collection.find({"service_id": service_id})
            db_tests = await cursor.to_list(length=100)  # Limit to 100 tests
            
            if db_tests:
                await custom_logger.ainfo(f"Found {len(db_tests)} tests in database for service {service_name}")
                
                # Convert database tests to test objects that match the ServiceTestsResponse schema
                for i, test_data in enumerate(db_tests):
                    # Create a test object with all required fields
                    test_obj = {
                        "id": str(test_data.get("_id", f"db-test-{i}")),
                        "name": test_data.get("name", f"Test {i}"),
                        "type": test_data.get("type", "Unit Test"),
                        "status": test_data.get("status", "Unknown"),
                        "path": f"demo_tests/{service_name}/{test_data.get('name', f'test_{i}')}",  # Required field
                        "nodeid": f"{service_name}::test_{i}",  # Required field
                        "module_name": f"{service_name}_tests",  # Required field
                        "class_name": "TestClass",
                        "function_name": f"test_{i}",
                        "line_number": 100 + i,
                        "parameters": [],
                        "is_parameterized": False,
                        "duration": test_data.get("duration", "0.1s"),
                        "result": test_data.get("status", "Unknown").lower(),
                        "test_id": str(test_data.get("_id", f"db-test-{i}"))
                    }
                    # Append this test object to the response
                    response.tests.append(test_obj)
                    tests_found = True
            else:
                await custom_logger.awarning(f"No tests found in database for service {service_name}")
            
            # If we have tests from either source, consider it a success
            if tests_found:
                # Save the collected tests to a file for persistence
                self._save_service_tests(response)
                await custom_logger.ainfo(f"Total of {len(response.tests)} tests collected for {service_name}")
            else:
                await custom_logger.awarning(f"No tests found for service {service_name} in filesystem or database")
            
            return response
            
        except Exception as e:
            error_message = str(e)
            await custom_logger.aerror(f"Exception while collecting tests: {error_message}")
            response.metadata["error"] = error_message
            return response
    
    def _parse_pytest_collect_output(self, output: str) -> List[str]:
        """Parse the output of pytest --collect-only to extract test nodeids"""
        # The output format is typically lines of nodeids
        lines = output.strip().split('\n')
        return [line.strip() for line in lines if line.strip()]
    
    def _create_test_item_from_nodeid(self, nodeid: str, index: int) -> TestItem:
        """Create a TestItem from a pytest nodeid"""
        # Parse the nodeid which typically has format: path/to/test_file.py::TestClass::test_method
        parts = nodeid.split("::") 
        path = parts[0]
        
        # Extract module name from path
        module_name = os.path.basename(path)
        if module_name.endswith(".py"):
            module_name = module_name[:-3]  # Remove .py extension
        
        # Initialize with defaults
        test_name = nodeid
        test_type = "unknown"
        class_name = None
        
        # Try to determine the test type and name based on the nodeid structure
        if len(parts) == 3:  # path/to/file.py::TestClass::test_method
            class_name = parts[1]
            test_name = parts[2]
            test_type = "method"
        elif len(parts) == 2:  # path/to/file.py::test_function
            test_name = parts[1]
            if test_name.startswith("Test") and not test_name.startswith("test_"):
                test_type = "class"
            else:
                test_type = "function"
        
        return TestItem(
            id=f"test_{index}_{uuid.uuid4().hex[:8]}",
            name=test_name,
            path=path,
            nodeid=nodeid,
            type=test_type,
            class_name=class_name,
            module_name=module_name
        )
    
    def _save_service_tests(self, tests_response: ServiceTestsResponse) -> None:
        """Save the collected service tests to a file for persistence"""
        # Create directory for the project if it doesn't exist
        project_dir = os.path.join(self.service_tests_dir, tests_response.project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        # Create a filename using the service ID
        filename = f"{tests_response.service_name}.json"
        file_path = os.path.join(project_dir, filename)
        
        # Convert to dictionary and serialize datetime
        tests_dict = tests_response.dict()
        tests_dict["discovery_time"] = tests_response.discovery_time.isoformat()
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(tests_dict, f, indent=2)
    
    async def get_service_tests(self, project_id: str, service_name: str) -> Optional[ServiceTestsResponse]:
        """Retrieve previously collected tests for a service"""
        # Check if the tests file exists
        project_dir = os.path.join(self.service_tests_dir, project_id)
        file_path = os.path.join(project_dir, f"{service_name}.json")
        
        if not os.path.exists(file_path):
            return None
            
        try:
            # Load the tests data
            with open(file_path, 'r') as f:
                tests_data = json.load(f)
                
            # Convert the loaded data back to a ServiceTestsResponse object
            return ServiceTestsResponse(**tests_data)
        except Exception as e:
            logger.error(f"Error loading service tests: {str(e)}")
            return None
