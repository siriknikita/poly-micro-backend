from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class TestStatus(str, Enum):
    """Test execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class TestRunCreate(BaseModel):
    """Schema for creating a new test run"""
    project_id: str = Field(..., description="Project ID the test belongs to")
    service_id: str = Field(..., description="Service ID the test belongs to")
    test_path: str = Field(..., description="Path to the test file or test directory")
    test_id: Optional[str] = Field(None, description="Specific test ID if running a single test")
    environment: Optional[Dict[str, str]] = Field(None, description="Environment variables for the test")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional pytest options")


class TestRunResult(BaseModel):
    """Schema for test run results"""
    id: str = Field(..., description="Unique test run ID")
    project_id: str = Field(..., description="Project ID")
    service_id: str = Field(..., description="Service ID")
    test_path: str = Field(..., description="Test path that was executed")
    test_id: Optional[str] = Field(None, description="Specific test ID if a single test was run")
    status: TestStatus = Field(..., description="Overall test run status")
    start_time: datetime = Field(..., description="Test run start timestamp")
    end_time: Optional[datetime] = Field(None, description="Test run end timestamp")
    duration_seconds: Optional[float] = Field(None, description="Test run duration in seconds")
    total_tests: int = Field(0, description="Total number of tests")
    passed_tests: int = Field(0, description="Number of passed tests")
    failed_tests: int = Field(0, description="Number of failed tests")
    error_tests: int = Field(0, description="Number of tests with errors")
    skipped_tests: int = Field(0, description="Number of skipped tests")
    log_ids: List[str] = Field(default_factory=list, description="List of associated log entry IDs")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about the test run")


class TestRunUpdate(BaseModel):
    """Schema for updating a test run"""
    status: Optional[TestStatus] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    total_tests: Optional[int] = None
    passed_tests: Optional[int] = None
    failed_tests: Optional[int] = None
    error_tests: Optional[int] = None
    skipped_tests: Optional[int] = None
    log_ids: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class TestAnalysisRequest(BaseModel):
    """Schema for requesting analysis of test run results"""
    test_run_id: str = Field(..., description="ID of the test run to analyze")
    include_logs: bool = Field(True, description="Whether to include logs in the analysis")
    analysis_type: Optional[str] = Field("comprehensive", description="Type of analysis to perform")


class TestAnalysisResult(BaseModel):
    """Schema for test analysis results"""
    test_run_id: str = Field(..., description="ID of the analyzed test run")
    project_id: str = Field(..., description="Project ID")
    service_id: str = Field(..., description="Service ID")
    analysis: str = Field(..., description="AI-generated analysis of the test results")
    summary: str = Field(..., description="Short summary of the analysis")
    issues_detected: List[Dict[str, Any]] = Field(default_factory=list, description="List of detected issues")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    success: bool = Field(..., description="Whether the analysis was successful")
    created_at: datetime = Field(..., description="Timestamp when the analysis was created")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about the analysis")
