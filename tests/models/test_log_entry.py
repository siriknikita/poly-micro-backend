"""Unit tests for the LogEntry model."""
import pytest
from datetime import datetime
from app.models.log import LogEntry
from app.schemas.log import Severity


class TestLogEntry:
    """Test cases for the LogEntry model."""

    def test_init_with_required_fields(self):
        """Test initialization with only required fields."""
        log = LogEntry(
            project_id="project1",
            service_id="service1",
            message="Test message",
        )
        
        assert log.project_id == "project1"
        assert log.service_id == "service1"
        assert log.message == "Test message"
        assert log.severity == Severity.INFO.value
        assert log.test_id is None
        assert log.func_id is None
        assert log.source is None
        assert log.timestamp is not None  # Should be auto-generated

    def test_init_with_all_fields(self):
        """Test initialization with all fields."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log = LogEntry(
            id="1",
            project_id="project1",
            service_id="service1",
            message="Test message",
            severity=Severity.ERROR.value,
            test_id="test1",
            func_id="func1",
            timestamp=timestamp,
            source="unit_test",
        )
        
        assert log.id == "1"
        assert log.project_id == "project1"
        assert log.service_id == "service1"
        assert log.message == "Test message"
        assert log.severity == Severity.ERROR.value
        assert log.test_id == "test1"
        assert log.func_id == "func1"
        assert log.timestamp == timestamp
        assert log.source == "unit_test"

    def test_project_id_setter(self):
        """Test project_id setter validation."""
        log = LogEntry(
            project_id="project1",
            service_id="service1",
            message="Test message",
        )
        
        log.project_id = "project2"
        assert log.project_id == "project2"
        
        with pytest.raises(ValueError, match="Project ID cannot be empty"):
            log.project_id = ""
            
        with pytest.raises(ValueError, match="Project ID cannot be empty"):
            log.project_id = None

    def test_service_id_setter(self):
        """Test service_id setter validation."""
        log = LogEntry(
            project_id="project1",
            service_id="service1",
            message="Test message",
        )
        
        log.service_id = "service2"
        assert log.service_id == "service2"
        
        with pytest.raises(ValueError, match="Service ID cannot be empty"):
            log.service_id = ""
            
        with pytest.raises(ValueError, match="Service ID cannot be empty"):
            log.service_id = None

    def test_message_setter(self):
        """Test message setter validation."""
        log = LogEntry(
            project_id="project1",
            service_id="service1",
            message="Test message",
        )
        
        log.message = "New message"
        assert log.message == "New message"
        
        with pytest.raises(ValueError, match="Message cannot be empty"):
            log.message = ""
            
        with pytest.raises(ValueError, match="Message cannot be empty"):
            log.message = None

    def test_severity_setter(self):
        """Test severity setter validation."""
        log = LogEntry(
            project_id="project1",
            service_id="service1",
            message="Test message",
        )
        
        log.severity = Severity.ERROR.value
        assert log.severity == Severity.ERROR.value

    def test_optional_fields_setters(self):
        """Test setters for optional fields."""
        log = LogEntry(
            project_id="project1",
            service_id="service1",
            message="Test message",
        )
        
        log.test_id = "test1"
        assert log.test_id == "test1"
        
        log.func_id = "func1"
        assert log.func_id == "func1"
        
        log.source = "unit_test"
        assert log.source == "unit_test"
        
        # Test setting to None (should be allowed for optional fields)
        log.test_id = None
        assert log.test_id is None
        
        log.func_id = None
        assert log.func_id is None
        
        log.source = None
        assert log.source is None

    def test_to_dict(self):
        """Test conversion to dictionary."""
        log = LogEntry(
            id="1",
            project_id="project1",
            service_id="service1",
            message="Test message",
            severity=Severity.WARN.value,
            test_id="test1",
            func_id="func1",
            timestamp="2023-01-01 12:00:00",
            source="unit_test",
        )
        
        log_dict = log.to_dict()
        
        assert log_dict["id"] == "1"
        assert log_dict["project_id"] == "project1"
        assert log_dict["service_id"] == "service1"
        assert log_dict["message"] == "Test message"
        assert log_dict["severity"] == "warn"
        assert log_dict["test_id"] == "test1"
        assert log_dict["func_id"] == "func1"
        assert log_dict["timestamp"] == "2023-01-01 12:00:00"
        assert log_dict["source"] == "unit_test"

    def test_from_dict(self):
        """Test creation from dictionary."""
        log_dict = {
            "id": "1",
            "project_id": "project1",
            "service_id": "service1",
            "message": "Test message",
            "severity": "error",
            "test_id": "test1",
            "func_id": "func1",
            "timestamp": "2023-01-01 12:00:00",
            "source": "unit_test",
        }
        
        log = LogEntry.from_dict(log_dict)
        
        assert log.id == "1"
        assert log.project_id == "project1"
        assert log.service_id == "service1"
        assert log.message == "Test message"
        assert log.severity == Severity.ERROR.value
        assert log.test_id == "test1"
        assert log.func_id == "func1"
        assert log.timestamp == "2023-01-01 12:00:00"
        assert log.source == "unit_test"

    def test_from_dict_with_invalid_severity(self):
        """Test creation from dictionary with invalid severity defaults to INFO."""
        log_dict = {
            "project_id": "project1",
            "service_id": "service1",
            "message": "Test message",
            "severity": "invalid_severity",
        }
        
        log = LogEntry.from_dict(log_dict)
        
        assert log.severity == Severity.INFO.value
