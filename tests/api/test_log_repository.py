"""Integration tests for the LogRepository with the new LogEntry model."""
import pytest
from app.db.repositories.log_repository import LogRepository
from app.db.database import get_database
from app.models.log import LogEntry
from app.schemas.log import Severity


@pytest.fixture
def log_repository():
    """Create a log repository for testing."""
    db = get_database()
    return LogRepository(db)


@pytest.mark.asyncio
async def test_create_log_with_model(log_repository):
    """Test creating a log entry using the LogEntry model."""
    # Repository is already available
    repo = log_repository
    
    # Create a log entry using the model
    log_entry = LogEntry(
        project_id="test_project",
        service_id="test_service",
        message="Test message from model",
        severity=Severity.INFO.value,
        test_id="test1",
        func_id="func1",
        source="integration_test"
    )
    
    # Save to database
    created_log = await repo.create_log(log_entry)
    
    # Verify the log was created correctly
    assert created_log is not None
    assert created_log["project_id"] == "test_project"
    assert created_log["service_id"] == "test_service"
    assert created_log["message"] == "Test message from model"
    assert created_log["severity"] == Severity.INFO.value
    assert created_log["test_id"] == "test1"
    assert created_log["func_id"] == "func1"
    assert created_log["source"] == "integration_test"
    assert "id" in created_log
    assert "timestamp" in created_log
    
    # Clean up - delete the created log
    await repo.delete_log(created_log["id"])


@pytest.mark.asyncio
async def test_get_logs_by_project(log_repository):
    """Test getting logs by project ID."""
    # Repository is already available
    repo = log_repository
    
    # Create multiple logs for different projects
    project1_log = LogEntry(
        project_id="project1",
        service_id="service1",
        message="Project 1 log",
        severity=Severity.INFO.value
    )
    
    project2_log = LogEntry(
        project_id="project2",
        service_id="service1",
        message="Project 2 log",
        severity=Severity.INFO.value
    )
    
    # Save logs to database
    created_log1 = await repo.create_log(project1_log)
    created_log2 = await repo.create_log(project2_log)
    
    # Get logs by project
    project1_logs = await repo.get_logs_by_project("project1")
    
    # Verify we get only project1 logs
    assert len(project1_logs) >= 1
    for log in project1_logs:
        assert log["project_id"] == "project1"
    
    # Clean up
    await repo.delete_log(created_log1["id"])
    await repo.delete_log(created_log2["id"])


@pytest.mark.asyncio
async def test_get_logs_by_service(log_repository):
    """Test getting logs by service ID."""
    # Repository is already available
    repo = log_repository
    
    # Create multiple logs for different services
    service1_log = LogEntry(
        project_id="project1",
        service_id="service1",
        message="Service 1 log",
        severity=Severity.INFO.value
    )
    
    service2_log = LogEntry(
        project_id="project1",
        service_id="service2",
        message="Service 2 log",
        severity=Severity.INFO.value
    )
    
    # Save logs to database
    created_log1 = await repo.create_log(service1_log)
    created_log2 = await repo.create_log(service2_log)
    
    # Get logs by service
    service1_logs = await repo.get_logs_by_service("service1")
    
    # Verify we get only service1 logs
    assert len(service1_logs) >= 1
    for log in service1_logs:
        assert log["service_id"] == "service1"
    
    # Clean up
    await repo.delete_log(created_log1["id"])
    await repo.delete_log(created_log2["id"])


@pytest.mark.asyncio
async def test_update_log_with_model(log_repository):
    """Test updating a log entry using the LogEntry model."""
    # Repository is already available
    repo = log_repository
    
    # Create a log entry
    log_entry = LogEntry(
        project_id="test_project",
        service_id="test_service",
        message="Original message",
        severity=Severity.INFO.value
    )
    
    # Save to database
    created_log = await repo.create_log(log_entry)
    log_id = created_log["id"]
    
    # Update the log entry using the model
    updated_entry = LogEntry(
        id=log_id,
        project_id="test_project",
        service_id="test_service",
        message="Updated message",
        severity=Severity.WARN.value,
        source="updated_test"
    )
    
    # Update in database
    updated_log = await repo.update_log(log_id, updated_entry)
    
    # Verify the update
    assert updated_log["message"] == "Updated message"
    assert updated_log["severity"] == "warn"
    assert updated_log["source"] == "updated_test"
    
    # Clean up
    await repo.delete_log(log_id)


@pytest.mark.asyncio
async def test_filtering_logs(log_repository):
    """Test filtering logs with various parameters."""
    # Repository is already available
    repo = log_repository
    
    # Create logs with different attributes
    log1 = LogEntry(
        project_id="project1",
        service_id="service1",
        test_id="test1",
        func_id="func1",
        message="Log 1",
        severity=Severity.INFO.value,
        source="source1"
    )
    
    log2 = LogEntry(
        project_id="project1",
        service_id="service2",
        test_id="test2",
        func_id="func2",
        message="Log 2",
        severity=Severity.ERROR.value,
        source="source2"
    )
    
    log3 = LogEntry(
        project_id="project2",
        service_id="service1",
        test_id="test1",
        func_id="func3",
        message="Log 3",
        severity=Severity.WARN.value,
        source="source1"
    )
    
    # Save logs to database
    created_log1 = await repo.create_log(log1)
    created_log2 = await repo.create_log(log2)
    created_log3 = await repo.create_log(log3)
    
    # Test different filters
    
    # By project_id
    project1_logs = await repo.get_all_logs(project_id="project1")
    assert len(project1_logs) >= 2
    for log in project1_logs:
        assert log["project_id"] == "project1"
    
    # By service_id
    service1_logs = await repo.get_all_logs(service_id="service1")
    assert len(service1_logs) >= 2
    for log in service1_logs:
        assert log["service_id"] == "service1"
    
    # By test_id
    test1_logs = await repo.get_all_logs(test_id="test1")
    assert len(test1_logs) >= 2
    for log in test1_logs:
        assert log["test_id"] == "test1"
    
    # By func_id
    func1_logs = await repo.get_all_logs(func_id="func1")
    assert len(func1_logs) >= 1
    for log in func1_logs:
        assert log["func_id"] == "func1"
    
    # By severity
    error_logs = await repo.get_all_logs(severity=Severity.ERROR.value)
    assert len(error_logs) >= 1
    for log in error_logs:
        assert log["severity"] == "error"
    
    # By source
    source1_logs = await repo.get_all_logs(source="source1")
    assert len(source1_logs) >= 2
    for log in source1_logs:
        assert log["source"] == "source1"
    
    # Multiple filters
    filtered_logs = await repo.get_all_logs(
        project_id="project1",
        service_id="service1",
        test_id="test1"
    )
    assert len(filtered_logs) >= 1
    for log in filtered_logs:
        assert log["project_id"] == "project1"
        assert log["service_id"] == "service1"
        assert log["test_id"] == "test1"
    
    # Clean up
    await repo.delete_log(created_log1["id"])
    await repo.delete_log(created_log2["id"])
    await repo.delete_log(created_log3["id"])