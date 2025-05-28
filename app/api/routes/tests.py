from fastapi import APIRouter, Depends, Path, Query, HTTPException, status
from typing import List, Optional, Dict, Any
import logging

from app.services.test_service import TestService
from app.services.test_analyzer_service import TestAnalyzerService
from app.services.log_service import LogService
from app.api.dependencies import get_log_service
from app.schemas.test import TestRunCreate, TestRunResult, TestAnalysisRequest, TestAnalysisResult
from app.services.service_manager import ServiceManager
from app.api.dependencies import get_service_manager

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Define dependencies
def get_test_service(log_service: LogService = Depends(get_log_service)):
    """Dependency for injecting TestService"""
    return TestService(log_service)

def get_test_analyzer_service(
    log_service: LogService = Depends(get_log_service),
    test_service: TestService = Depends(get_test_service)
):
    """Dependency for injecting TestAnalyzerService"""
    return TestAnalyzerService(log_service, test_service)

def get_service_manager_with_deps(
    log_service: LogService = Depends(get_log_service)
):
    """Dependency for injecting ServiceManager with dependencies"""
    return ServiceManager(log_service)


@router.post("/run", response_model=TestRunResult, status_code=status.HTTP_202_ACCEPTED)
async def run_test(
    test_run: TestRunCreate,
    test_service: TestService = Depends(get_test_service)
):
    """
    Execute a test in a Docker container and collect results.
    
    This endpoint:
    1. Creates a new test run record
    2. Executes the test in the appropriate Docker container
    3. Collects and processes test results
    4. Stores logs with test metadata
    
    Returns the test run result with execution details.
    """
    try:
        logger.info(f"Creating test run for {test_run.project_id}/{test_run.service_id}")
        
        # Create test run record
        test_result = await test_service.create_test_run(test_run)
        
        # Execute test run asynchronously
        # We'll return the initial test run metadata immediately and let the execution happen in the background
        # The client can poll for updates or use websockets for real-time status
        import asyncio
        asyncio.create_task(test_service.execute_test_run(test_result.id))
        
        return test_result
    
    except Exception as e:
        logger.exception(f"Error running test: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run test: {str(e)}"
        )


@router.get("/run/{test_run_id}", response_model=TestRunResult)
async def get_test_run(
    test_run_id: str = Path(..., description="The ID of the test run to retrieve"),
    test_service: TestService = Depends(get_test_service)
):
    """
    Get the details of a specific test run.
    
    This endpoint retrieves the metadata and results of a previously executed test run.
    """
    try:
        test_run = await test_service.get_test_run(test_run_id)
        if not test_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test run with ID {test_run_id} not found"
            )
        
        return test_run
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving test run: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve test run: {str(e)}"
        )


@router.get("/project/{project_id}", response_model=List[TestRunResult])
async def get_project_test_runs(
    project_id: str = Path(..., description="The project ID to get test runs for"),
    test_service: TestService = Depends(get_test_service)
):
    """
    Get all test runs for a specific project.
    
    This endpoint returns a list of all test runs associated with the given project.
    """
    try:
        test_runs = await test_service.get_test_runs_by_project(project_id)
        return test_runs
    
    except Exception as e:
        logger.exception(f"Error retrieving project test runs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve project test runs: {str(e)}"
        )


@router.get("/service/{service_id}", response_model=List[TestRunResult])
async def get_service_test_runs(
    service_id: str = Path(..., description="The service ID to get test runs for"),
    test_service: TestService = Depends(get_test_service)
):
    """
    Get all test runs for a specific service.
    
    This endpoint returns a list of all test runs associated with the given service.
    """
    try:
        test_runs = await test_service.get_test_runs_by_service(service_id)
        return test_runs
    
    except Exception as e:
        logger.exception(f"Error retrieving service test runs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve service test runs: {str(e)}"
        )


@router.post("/analyze", response_model=TestAnalysisResult)
async def analyze_test_run(
    analysis_request: TestAnalysisRequest,
    test_analyzer_service: TestAnalyzerService = Depends(get_test_analyzer_service)
):
    """
    Analyze a test run using AI to extract insights.
    
    This endpoint:
    1. Retrieves the test run data and associated logs
    2. Uses Gemini AI to analyze the test results
    3. Returns structured analysis with insights and suggestions
    
    The analysis includes:
    - Overall assessment of the test run
    - Identification of key issues or failures
    - Potential root causes for failures
    - Suggestions for improvement
    """
    try:
        logger.info(f"Analyzing test run: {analysis_request.test_run_id}")
        
        # Check if analysis already exists
        existing_analysis = await test_analyzer_service.get_analysis(analysis_request.test_run_id)
        if existing_analysis:
            logger.info(f"Returning existing analysis for test run {analysis_request.test_run_id}")
            return existing_analysis
        
        # Generate new analysis
        analysis_result = await test_analyzer_service.analyze_test_run(
            analysis_request.test_run_id,
            include_logs=analysis_request.include_logs
        )
        
        return analysis_result
    
    except ValueError as e:
        # Handle case where test run doesn't exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Error analyzing test run: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze test run: {str(e)}"
        )


@router.get("/analyze/{test_run_id}", response_model=TestAnalysisResult)
async def get_test_analysis(
    test_run_id: str = Path(..., description="The ID of the test run to get analysis for"),
    test_analyzer_service: TestAnalyzerService = Depends(get_test_analyzer_service)
):
    """
    Get the AI analysis for a test run if it exists.
    
    This endpoint retrieves a previously generated analysis for a test run.
    If no analysis exists, it returns a 404 error.
    """
    try:
        analysis = await test_analyzer_service.get_analysis(test_run_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No analysis found for test run {test_run_id}"
            )
        
        return analysis
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving test analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve test analysis: {str(e)}"
        )


@router.post("/service/{service_id}/run-all", response_model=TestRunResult, status_code=status.HTTP_202_ACCEPTED)
async def run_service_tests(
    service_id: str = Path(..., description="The ID of the service to run tests for"),
    project_id: str = Query(..., description="The project ID that the service belongs to"),
    test_service: TestService = Depends(get_test_service),
    service_manager: ServiceManager = Depends(get_service_manager_with_deps)
):
    """
    Run all tests for a specific microservice in its Docker container.
    
    This endpoint:
    1. Gets the Docker container name from the service
    2. Creates a new test run for the service
    3. Executes all tests in the container using pytest with JSON reporting
    4. Processes the results and generates logs for each test
    5. Returns the test run result with execution details
    
    The test results are also available through the logs with pass/fail status indicators.
    """
    try:
        logger.info(f"Running all tests for service {service_id} in project {project_id}")
        
        # Get the service details to get the container name
        service = await service_manager.get_service(project_id, service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service with ID {service_id} not found in project {project_id}"
            )
        
        # Get the container name from the service
        container_name = service.container_name
        if not container_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Service {service_id} does not have a valid container name"
            )
        
        # Run all tests for the service
        test_result = await test_service.run_service_tests(
            project_id=project_id,
            service_id=service_id,
            service_name=service.name,
            container_name=container_name
        )
        
        return test_result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error running service tests: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run service tests: {str(e)}"
        )
