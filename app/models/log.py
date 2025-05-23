"""Log model for the application."""
from datetime import datetime
from typing import Optional
from app.schemas.log import Severity


class LogEntry:
    """
    Log entry class for logging functionality.
    Contains getters and setters for all log fields.
    """

    def __init__(
        self,
        project_id: str,
        service_id: str,
        message: str,
        severity: Severity = Severity.INFO.value,
        test_id: Optional[str] = None,
        func_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        source: Optional[str] = None,
        id: Optional[str] = None,
    ):
        self._id = id
        self._project_id = project_id
        self._service_id = service_id
        self._test_id = test_id
        self._func_id = func_id
        self._message = message
        self._severity = severity
        self._timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._source = source

    # ID property
    @property
    def id(self) -> Optional[str]:
        """Get log entry ID."""
        return self._id

    @id.setter
    def id(self, value: str):
        """Set log entry ID."""
        self._id = value

    # Project ID property
    @property
    def project_id(self) -> str:
        """Get project ID."""
        return self._project_id

    @project_id.setter
    def project_id(self, value: str):
        """Set project ID."""
        if not value:
            raise ValueError("Project ID cannot be empty")
        self._project_id = value

    # Service ID property
    @property
    def service_id(self) -> str:
        """Get service ID."""
        return self._service_id

    @service_id.setter
    def service_id(self, value: str):
        """Set service ID."""
        if not value:
            raise ValueError("Service ID cannot be empty")
        self._service_id = value

    # Test ID property
    @property
    def test_id(self) -> Optional[str]:
        """Get test ID."""
        return self._test_id

    @test_id.setter
    def test_id(self, value: Optional[str]):
        """Set test ID."""
        self._test_id = value

    # Function ID property
    @property
    def func_id(self) -> Optional[str]:
        """Get function ID."""
        return self._func_id

    @func_id.setter
    def func_id(self, value: Optional[str]):
        """Set function ID."""
        self._func_id = value

    # Message property
    @property
    def message(self) -> str:
        """Get message."""
        return self._message

    @message.setter
    def message(self, value: str):
        """Set message."""
        if not value:
            raise ValueError("Message cannot be empty")
        self._message = value

    # Severity property
    @property
    def severity(self) -> Severity:
        """Get severity."""
        return self._severity

    @severity.setter
    def severity(self, value: str):
        """Set severity."""
        if not isinstance(value, str):
            raise TypeError("Severity must be a string")
        self._severity = value

    # Timestamp property
    @property
    def timestamp(self) -> str:
        """Get timestamp."""
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: str):
        """Set timestamp."""
        self._timestamp = value

    # Source property
    @property
    def source(self) -> Optional[str]:
        """Get source."""
        return self._source

    @source.setter
    def source(self, value: Optional[str]):
        """Set source."""
        self._source = value

    def to_dict(self) -> dict:
        """Convert log entry to dictionary."""
        return {
            "id": self._id,
            "project_id": self._project_id,
            "service_id": self._service_id,
            "test_id": self._test_id,
            "func_id": self._func_id,
            "message": self._message,
            "severity": self._severity,
            "timestamp": self._timestamp,
            "source": self._source,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'LogEntry':
        """Create log entry from dictionary."""
        severity_value = data.get("severity")
        severity = next(
            (s for s in Severity if s.value == severity_value), 
            Severity.INFO.value
        )
        
        return cls(
            id=data.get("id"),
            project_id=data.get("project_id"),
            service_id=data.get("service_id"),
            test_id=data.get("test_id"),
            func_id=data.get("func_id"),
            message=data.get("message"),
            severity=severity,
            timestamp=data.get("timestamp"),
            source=data.get("source"),
        )
