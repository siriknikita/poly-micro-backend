"""Integration tests for the services API endpoints."""
import pytest
from bson import ObjectId
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_get_all_services(client: AsyncClient):
    """Test getting all services."""
    response = await client.get("/api/services/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    # Verify the structure of a service
    if data:
        service = data[0]
        assert "id" in service
        assert "name" in service
        assert "project_id" in service
        # These fields are optional but commonly present
        assert "status" in service or "status" is None
        assert "port" in service or "port" is None


@pytest.mark.asyncio
async def test_get_services_by_project(client: AsyncClient, test_db):
    """Test getting services by project ID."""
    # First, get all projects to find an ID
    response = await client.get("/api/projects/")
    assert response.status_code == status.HTTP_200_OK
    projects = response.json()
    
    if projects:
        project_id = projects[0]["id"]
        # Test getting services for the specific project
        response = await client.get(f"/api/services/project/{project_id}")
        assert response.status_code == status.HTTP_200_OK
        services = response.json()
        assert isinstance(services, list)
        # Verify that all services belong to the specified project
        for service in services:
            assert service["project_id"] == project_id


@pytest.mark.asyncio
async def test_get_service_by_id(client: AsyncClient):
    """Test getting a service by ID."""
    # First, get all services to find an ID
    response = await client.get("/api/services/")
    assert response.status_code == status.HTTP_200_OK
    services = response.json()
    
    if services:
        service_id = services[0]["id"]
        # Test getting the specific service
        response = await client.get(f"/api/services/{service_id}")
        assert response.status_code == status.HTTP_200_OK
        service = response.json()
        assert service["id"] == service_id
    
    # Test with invalid ID
    response = await client.get(f"/api/services/{str(ObjectId())}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_create_service(client: AsyncClient):
    """Test creating a new service."""
    # First, get a project to associate with the service
    response = await client.get("/api/projects/")
    assert response.status_code == status.HTTP_200_OK
    projects = response.json()
    
    if projects:
        project_id = projects[0]["id"]
        
        new_service = {
            "project_id": project_id,
            "name": "Test Service",
            "port": 3009,
            "url": "http://localhost:3009",
            "status": "Running",
            "health": "Healthy",
            "uptime": "1d 2h 30m",
            "version": "1.0.0",
            "last_deployment": "2024-05-22 10:00"
        }
        
        response = await client.post("/api/services/", json=new_service)
        assert response.status_code == status.HTTP_201_CREATED
        created_service = response.json()
        assert created_service["name"] == new_service["name"]
        assert created_service["project_id"] == project_id
        assert "id" in created_service
        
        # Verify the service was actually created
        response = await client.get(f"/api/services/{created_service['id']}")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_service(client: AsyncClient):
    """Test updating a service."""
    # First, get all services to find one to update
    response = await client.get("/api/services/")
    assert response.status_code == status.HTTP_200_OK
    services = response.json()
    
    if services:
        service_id = services[0]["id"]
        project_id = services[0]["project_id"]
        
        # Update the service
        updated_data = {
            "name": "Updated Service",
            "status": "Stopped",
            "health": "Warning",
            "version": "1.1.0",
            "port": 3010
        }
        
        response = await client.put(f"/api/services/{service_id}", json=updated_data)
        assert response.status_code == status.HTTP_200_OK
        updated_service = response.json()
        assert updated_service["name"] == updated_data["name"]
        assert updated_service["status"] == updated_data["status"]
        
        # Verify the update was persisted
        response = await client.get(f"/api/services/{service_id}")
        assert response.status_code == status.HTTP_200_OK
        service = response.json()
        assert service["name"] == updated_data["name"]
        assert service["status"] == updated_data["status"]


@pytest.mark.asyncio
async def test_delete_service(client: AsyncClient):
    """Test deleting a service."""
    # First, create a service to delete
    # Get a project ID to associate with the service
    response = await client.get("/api/projects/")
    projects = response.json()
    
    if projects:
        project_id = projects[0]["id"]
        
        new_service = {
            "project_id": project_id,
            "name": "Service to Delete",
            "port": 3011,
            "status": "Running"
        }
        
        response = await client.post("/api/services/", json=new_service)
        assert response.status_code == status.HTTP_201_CREATED
        service_id = response.json()["id"]
        
        # Delete the service
        response = await client.delete(f"/api/services/{service_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify the service was deleted
        response = await client.get(f"/api/services/{service_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_invalid_service_data(client: AsyncClient):
    """Test validation of service data."""
    # Missing required fields
    invalid_service = {
        "port": 3012,
        "status": "Running"
    }
    
    response = await client.post("/api/services/", json=invalid_service)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Invalid project ID
    invalid_service = {
        "name": "Invalid Service",
        "project_id": str(ObjectId()),  # Non-existent project ID
        "port": 3013
    }
    
    response = await client.post("/api/services/", json=invalid_service)
    assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]
