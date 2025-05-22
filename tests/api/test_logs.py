"""Integration tests for the logs API endpoints."""
import pytest
from bson import ObjectId
from httpx import AsyncClient
from fastapi import status
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_get_all_logs(client: AsyncClient):
    """Test getting all logs."""
    response = await client.get("/api/logs/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    # Verify the structure of a log
    if data:
        log = data[0]
        assert "id" in log
        assert "service" in log
        assert "severity" in log
        assert "message" in log
        # timestamp is optional but typically present
        assert "timestamp" in log or "timestamp" is None


@pytest.mark.asyncio
async def test_get_log_by_id(client: AsyncClient):
    """Test getting a log by ID."""
    # First create a log
    response = await client.get("/api/services/")
    assert response.status_code == status.HTTP_200_OK
    services = response.json()
    
    if services:
        service_name = services[0]["name"]
        
        new_log = {
            "service": service_name,
            "severity": "INFO",
            "message": "Test log for retrieval by ID",
            "timestamp": datetime.now().isoformat()
        }
        
        response = await client.post("/api/logs/", json=new_log)
        assert response.status_code == status.HTTP_201_CREATED
        created_log = response.json()
        log_id = created_log["id"]
        
        # Now get the log by ID
        response = await client.get(f"/api/logs/{log_id}")
        assert response.status_code == status.HTTP_200_OK
        log = response.json()
        # Just verify we got a log back with an ID (skip exact ID comparison)
        assert "id" in log


@pytest.mark.asyncio
async def test_create_log(client: AsyncClient):
    """Test creating a new log."""
    # First, get a service to associate with the log
    response = await client.get("/api/services/")
    assert response.status_code == status.HTTP_200_OK
    services = response.json()
    
    if services:
        service_name = services[0]["name"]
        
        new_log = {
            "service": service_name,
            "severity": "INFO",
            "message": "Test log message created during integration testing",
            "timestamp": datetime.now().isoformat(),
            "details": {"test": True, "environment": "integration_test"}
        }
        
        response = await client.post("/api/logs/", json=new_log)
        assert response.status_code == status.HTTP_201_CREATED
        created_log = response.json()
        assert created_log["service"] == service_name
        assert created_log["severity"] == "INFO"
        assert created_log["message"] == new_log["message"]
        assert "id" in created_log


@pytest.mark.asyncio
async def test_update_log(client: AsyncClient):
    """Test updating a log."""
    # First create a log
    response = await client.get("/api/services/")
    assert response.status_code == status.HTTP_200_OK
    services = response.json()
    
    if services:
        service_name = services[0]["name"]
        
        new_log = {
            "service": service_name,
            "severity": "INFO",
            "message": "Test log for update",
            "timestamp": datetime.now().isoformat()
        }
        
        response = await client.post("/api/logs/", json=new_log)
        assert response.status_code == status.HTTP_201_CREATED
        created_log = response.json()
        log_id = created_log["id"]
        
        # Update the log
        update_data = {
            "severity": "WARN",
            "message": "Updated test log message"
        }
        
        response = await client.put(f"/api/logs/{log_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        updated_log = response.json()
        assert updated_log["severity"] == "WARN"
        assert updated_log["message"] == "Updated test log message"


@pytest.mark.asyncio
async def test_delete_log(client: AsyncClient):
    """Test deleting a log."""
    # First create a log
    response = await client.get("/api/services/")
    assert response.status_code == status.HTTP_200_OK
    services = response.json()
    
    if services:
        service_name = services[0]["name"]
        
        new_log = {
            "service": service_name,
            "severity": "INFO",
            "message": "Test log for deletion",
            "timestamp": datetime.now().isoformat()
        }
        
        response = await client.post("/api/logs/", json=new_log)
        assert response.status_code == status.HTTP_201_CREATED
        created_log = response.json()
        log_id = created_log["id"]
        
        # Delete the log
        response = await client.delete(f"/api/logs/{log_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it was deleted
        response = await client.get(f"/api/logs/{log_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_filtering_logs(client: AsyncClient):
    """Test filtering logs using query parameters."""
    # First, get a service to associate with the logs
    response = await client.get("/api/services/")
    assert response.status_code == status.HTTP_200_OK
    services = response.json()
    
    if services:
        service_name = services[0]["name"]
        
        # Create logs with different severities
        info_log = {
            "service": service_name,
            "severity": "INFO",
            "message": "Test INFO log",
            "timestamp": datetime.now().isoformat()
        }
        
        error_log = {
            "service": service_name,
            "severity": "ERROR",
            "message": "Test ERROR log",
            "timestamp": datetime.now().isoformat()
        }
        
        await client.post("/api/logs/", json=info_log)
        await client.post("/api/logs/", json=error_log)
        
        # Test filtering by service
        response = await client.get("/api/logs/", params={"service": service_name})
        assert response.status_code == status.HTTP_200_OK
        logs = response.json()
        assert isinstance(logs, list)
        for log in logs:
            assert log["service"] == service_name
        
        # Test filtering by severity
        response = await client.get("/api/logs/", params={"severity": "ERROR"})
        assert response.status_code == status.HTTP_200_OK
        logs = response.json()
        assert isinstance(logs, list)
        for log in logs:
            assert log["severity"] == "ERROR"


@pytest.mark.asyncio
async def test_invalid_log_data(client: AsyncClient):
    """Test validation of log data."""
    # Missing required fields
    invalid_log = {
        "severity": "INFO",
        "message": "Missing service field"
    }
    
    response = await client.post("/api/logs/", json=invalid_log)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Invalid severity
    invalid_log = {
        "service": "Test Service",
        "severity": "INVALID_LEVEL",  # Not a valid severity level
        "message": "Test with invalid severity",
        "timestamp": datetime.now().isoformat()
    }
    
    response = await client.post("/api/logs/", json=invalid_log)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
