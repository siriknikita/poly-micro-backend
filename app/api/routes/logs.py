from fastapi import APIRouter, Depends, Path, Query, HTTPException, status
from typing import List, Optional, Dict, Any
import os

from app.services.log_service import LogService
from app.api.dependencies import get_log_service
from app.schemas.log import Log, LogCreate, LogUpdate, Severity
from app.schemas.analysis import LogAnalysisResponse, LogAnalysisRequest

# For Gemini log analysis
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()

@router.get("/", response_model=List[Log])
async def get_all_logs(
    project_id: Optional[str] = Query(None, description="Filter logs by project ID"),
    service_id: Optional[str] = Query(None, description="Filter logs by service ID"),
    test_id: Optional[str] = Query(None, description="Filter logs by test ID"),
    func_id: Optional[str] = Query(None, description="Filter logs by function ID"),
    severity: Optional[Severity] = Query(None, description="Filter logs by severity"),
    source: Optional[str] = Query(None, description="Filter logs by source"),
    log_service: LogService = Depends(get_log_service)
):
    """Get all logs with optional filtering"""
    return await log_service.get_all_logs(
        project_id=project_id,
        service_id=service_id,
        test_id=test_id,
        func_id=func_id,
        severity=severity,
        source=source
    )

@router.get("/project/{project_id}", response_model=List[Log])
async def get_logs_by_project(
    project_id: str = Path(..., description="The project ID to filter logs by"),
    log_service: LogService = Depends(get_log_service)
):
    """Get all logs for a specific project"""
    return await log_service.get_logs_by_project(project_id)

@router.get("/service/{service_id}", response_model=List[Log])
async def get_logs_by_service(
    service_id: str = Path(..., description="The service ID to filter logs by"),
    log_service: LogService = Depends(get_log_service)
):
    """Get all logs for a specific service"""
    return await log_service.get_logs_by_service(service_id)

@router.get("/{log_id}", response_model=Log)
async def get_log(
    log_id: str = Path(..., description="The ID of the log to get"),
    log_service: LogService = Depends(get_log_service)
):
    """Get a specific log by ID"""
    return await log_service.get_log_by_id(log_id)

@router.post("/", response_model=Log, status_code=status.HTTP_201_CREATED)
async def create_log(
    log: LogCreate,
    log_service: LogService = Depends(get_log_service)
):
    """Create a new log entry"""
    return await log_service.create_log(log)

@router.post("/raw", response_model=Log, status_code=status.HTTP_201_CREATED)
async def create_log_from_dict(
    log_data: Dict[str, Any],
    log_service: LogService = Depends(get_log_service)
):
    """Create a new log entry from raw dictionary data"""
    return await log_service.create_log_entry(log_data)

@router.put("/{log_id}", response_model=Log)
async def update_log(
    log: LogUpdate,
    log_id: str = Path(..., description="The ID of the log to update"),
    log_service: LogService = Depends(get_log_service)
):
    """Update a log entry"""
    return await log_service.update_log(log_id, log)

@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log(
    log_id: str = Path(..., description="The ID of the log to delete"),
    log_service: LogService = Depends(get_log_service)
):
    """Delete a log entry"""
    await log_service.delete_log(log_id)
    return None


# Configure Gemini for log analysis
def get_gemini_model():
    import traceback
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("ERROR: GEMINI_API_KEY environment variable not found")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GEMINI_API_KEY not found in environment variables"
        )
    
    # Mask most of the API key when printing for security
    masked_key = gemini_api_key[:4] + "*" * (len(gemini_api_key) - 8) + gemini_api_key[-4:] if len(gemini_api_key) > 8 else "*****"
    print(f"GEMINI_API_KEY present (masked): {masked_key}")
    
    try:
        print("Configuring Gemini API...")
        genai.configure(api_key=gemini_api_key)
        print("Gemini API configured successfully")
        
        print("Creating Gemini model instance...")
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        print(f"Gemini model created: {type(model).__name__}")
        
        # Test with a simple prompt to verify API is working
        try:
            print("Testing Gemini API with simple prompt...")
            test_response = model.generate_content("Respond with only the word 'OK' if you can read this.")
            print(f"Gemini API test response: {test_response.text}")
        except Exception as test_error:
            print(f"WARNING: Gemini API test failed: {str(test_error)}")
            print(f"Traceback: {traceback.format_exc()}")
            # Continue anyway since we got a model object
        
        return model
    except Exception as e:
        print(f"ERROR configuring Gemini model: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error configuring Gemini model: {str(e)}"
        )


def analyze_logs_with_gemini(logs: list[Log]) -> str:
    """Analyze logs using Gemini AI and return insights"""
    import traceback
    
    if not logs:
        return "No logs provided for analysis."

    try:
        print("Getting Gemini model...")
        try:
            gemini_model = get_gemini_model()
            print(f"Gemini model object type: {type(gemini_model).__name__}")
            if not gemini_model:
                error_msg = "Failed to configure Gemini model - returned None"
                print(f"ERROR: {error_msg}")
                return f"Error: {error_msg}"
        except Exception as model_error:
            error_msg = f"Failed to get Gemini model: {str(model_error)}"
            print(f"ERROR: {error_msg}")
            print(f"Traceback: {traceback.format_exc()}")
            return f"Error: {error_msg}"

        print(f"Formatting {len(logs)} log entries...")
        log_entries_str = ""
        for i, log_item in enumerate(logs):
            # Safely get severity - handle all possible cases
            try:
                if hasattr(log_item.severity, 'value'):
                    severity = log_item.severity.value
                elif log_item.severity is not None:
                    severity = str(log_item.severity)
                else:
                    severity = 'N/A'
            except Exception as sev_error:
                print(f"Error getting severity for log {i}: {str(sev_error)}")
                severity = 'N/A'
            
            # Safely format each log entry
            try:
                timestamp = log_item.timestamp if log_item.timestamp else 'N/A'
                service = log_item.service_id if log_item.service_id else 'N/A'
                message = log_item.message if log_item.message else 'N/A'
                source = log_item.source if log_item.source else 'N/A'
                
                log_entries_str += (
                    f"- Timestamp: {timestamp}, "
                    f"Severity: {severity}, "
                    f"Service: {service}, "
                    f"Message: {message}, "
                    f"Source: {source}\n"
                )
            except Exception as log_format_error:
                print(f"Error formatting log {i}: {str(log_format_error)}")
                print(f"Traceback: {traceback.format_exc()}")
                # Continue with other logs even if one fails
                continue

        if not log_entries_str:
            return "Could not format any logs for analysis."

        print(f"Generated log string with {len(log_entries_str)} characters")
        prompt = (
            "You are an expert log analyst. Please analyze the following logs and provide concise insights. "
            "Focus on identifying critical errors, recurring warnings, unusual patterns, or any anomalies that might require immediate attention. "
            "Summarize the overall health of the system based on these logs.\n\n"
            "Logs:\n"
            f"{log_entries_str}\n\n"
            "Insights:"
        )

        print(f"Generated prompt with {len(prompt)} characters")
        
        try:
            print("Calling Gemini API to analyze logs...")
            response = gemini_model.generate_content(prompt)
            print(f"Gemini response received: {type(response).__name__}")
            if hasattr(response, 'text'):
                print(f"Response has text of length: {len(response.text)}")
                return response.text
            else:
                print(f"Response object: {response}")
                return "Received response from Gemini but it did not contain expected text content."
        except Exception as gemini_error:
            error_msg = f"Gemini API error: {str(gemini_error)}"
            print(f"ERROR: {error_msg}")
            print(f"Traceback: {traceback.format_exc()}")
            return f"Error calling Gemini API. Please try again later. Details: {str(gemini_error)}"
    except Exception as e:
        print(f"Unexpected error in analyze_logs_with_gemini: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        # Return error message instead of raising exception to avoid 500 errors
        return f"Error analyzing logs: {str(e)}"


@router.post("/analyze", response_model=LogAnalysisResponse)
async def analyze_project_logs(
    request: LogAnalysisRequest,
    log_service: LogService = Depends(get_log_service)
):
    """Analyze logs for a specific project using AI"""
    try:
        # Validate project ID
        if not request.project_id:
            return LogAnalysisResponse(
                project_id="",
                analysis="Error: Project ID is required for log analysis.",
                log_count=0,
                success=False
            )
        
        print(f"project_id: {request.project_id}")
        
        # Get logs for the specified project
        try:
            logs = await log_service.get_logs_by_project(request.project_id)
            print(f"LOGS {logs}")
        except Exception as logs_error:
            print(f"Error fetching logs: {str(logs_error)}")
            return LogAnalysisResponse(
                project_id=request.project_id,
                analysis=f"Error fetching logs: {str(logs_error)}",
                log_count=0,
                success=False
            )
        
        if not logs:
            return LogAnalysisResponse(
                project_id=request.project_id,
                analysis="No logs found for this project.",
                log_count=0,
                success=True
            )
        
        # Analyze logs using Gemini
        try:
            analysis = analyze_logs_with_gemini(logs)
            print(f"Log analysis completed: {analysis}")
        except Exception as analysis_error:
            print(f"Error during log analysis: {str(analysis_error)}")
            return LogAnalysisResponse(
                project_id=request.project_id,
                analysis=f"Error analyzing logs: {str(analysis_error)}",
                log_count=len(logs),
                success=False
            )
        
        return LogAnalysisResponse(
            project_id=request.project_id,
            analysis=analysis,
            log_count=len(logs),
            success=True
        )
    except Exception as e:
        print(f"Unexpected error in analyze_project_logs: {str(e)}")
        # Return a response instead of raising an exception to avoid 500 errors
        return LogAnalysisResponse(
            project_id=request.project_id if hasattr(request, 'project_id') else "unknown",
            analysis=f"An unexpected error occurred: {str(e)}",
            log_count=0,
            success=False
        )
