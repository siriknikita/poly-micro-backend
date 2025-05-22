"""Integration tests for the metrics API endpoints."""
import pytest
from bson import ObjectId
from httpx import AsyncClient
from fastapi import status
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_get_all_cpu_entries(client: AsyncClient):
    """Test getting all CPU entries."""
    response = await client.get("/api/metrics/cpu")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    # Verify the structure of a CPU entry
    if data:
        cpu_entry = data[0]
        assert "id" in cpu_entry
        assert "project_id" in cpu_entry
        assert "service_name" in cpu_entry
        assert "data" in cpu_entry
        assert isinstance(cpu_entry["data"], list)
        if cpu_entry["data"]:
            cpu_data = cpu_entry["data"][0]
            assert "time" in cpu_data
            assert "load" in cpu_data
            assert "memory" in cpu_data
            assert "threads" in cpu_data


@pytest.mark.asyncio
async def test_get_cpu_entry_by_id(client: AsyncClient):
    """Test getting a CPU entry by ID."""
    # First, get all CPU entries to find an ID
    response = await client.get("/api/metrics/cpu")
    assert response.status_code == status.HTTP_200_OK
    entries = response.json()
    
    if entries:
        entry_id = entries[0]["id"]
        # Test getting the specific CPU entry
        response = await client.get(f"/api/metrics/cpu/{entry_id}")
        assert response.status_code == status.HTTP_200_OK
        entry = response.json()
        assert entry["id"] == entry_id
        assert "project_id" in entry
        assert "service_name" in entry
        assert "data" in entry


@pytest.mark.asyncio
async def test_get_metrics_by_project(client: AsyncClient):
    """Test getting metrics by project ID."""
    # First, get all projects to find an ID
    response = await client.get("/api/projects/")
    assert response.status_code == status.HTTP_200_OK
    projects = response.json()
    
    if projects:
        project_id = projects[0]["id"]
        # Test getting metrics for the specific project
        response = await client.get(f"/api/metrics/cpu/project/{project_id}")
        assert response.status_code == status.HTTP_200_OK
        cpu_entries = response.json()
        assert isinstance(cpu_entries, list)
        # Verify that all entries belong to the specified project
        for entry in cpu_entries:
            assert entry["project_id"] == project_id


@pytest.mark.asyncio
async def test_get_metrics_by_service(client: AsyncClient):
    """Test getting metrics by service name."""
    # First, get all services to find a name
    response = await client.get("/api/services/")
    assert response.status_code == status.HTTP_200_OK
    services = response.json()
    
    if services:
        service_name = services[0]["name"]
        # Test getting metrics for the specific service
        response = await client.get(f"/api/metrics/cpu/service/{service_name}")
        assert response.status_code == status.HTTP_200_OK
        cpu_entries = response.json()
        assert isinstance(cpu_entries, list)
        # Verify that all entries are for the specified service
        for entry in cpu_entries:
            assert entry["service_name"] == service_name


@pytest.mark.asyncio
async def test_create_cpu_entry(client: AsyncClient):
    """Test creating a new CPU entry."""
    # First, get a project and service to associate with the entry
    response = await client.get("/api/projects/")
    assert response.status_code == status.HTTP_200_OK
    projects = response.json()
    
    if projects:
        project_id = projects[0]["id"]
        
        # Get services for this specific project
        response = await client.get(f"/api/services/project/{project_id}")
        assert response.status_code == status.HTTP_200_OK, f"Failed to get services: {response.text}"

        services = response.json()
        assert services, f"No services available for project {project_id}"
        
        service_name = services[0]["name"]
        print(f"Using project_id: {project_id} and service_name: {service_name}")
        
        # Create a CPU entry with data points
        new_cpu_entry = {
            "project_id": project_id,
            "service_name": service_name,
            "data": [
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "load": 45.2,
                    "memory": 256.7,
                    "threads": 12
                },
                {
                    "time": (datetime.now() - timedelta(minutes=5)).strftime("%H:%M:%S"),
                    "load": 42.8,
                    "memory": 248.3,
                    "threads": 10
                }
            ]
        }
        
        response = await client.post("/api/metrics/cpu", json=new_cpu_entry)
        if response.status_code != status.HTTP_201_CREATED:
            print('response', response.text)
        assert response.status_code == status.HTTP_201_CREATED
        created_entry = response.json()
        assert created_entry["project_id"] == project_id
        assert created_entry["service_name"] == service_name
        assert "id" in created_entry
        assert len(created_entry["data"]) == 2


@pytest.mark.asyncio
async def test_update_cpu_entry(client: AsyncClient):
    """Test updating a CPU entry with new data points."""
    # First create a CPU entry
    response = await client.get("/api/projects/")
    assert response.status_code == status.HTTP_200_OK
    projects = response.json()
    
    if projects:
        project_id = projects[0]["id"]
        
        # Get services for this specific project
        response = await client.get(f"/api/services/project/{project_id}")
        assert response.status_code == status.HTTP_200_OK, f"Failed to get services: {response.text}"

        services = response.json()
        assert services, f"No services available for project {project_id}"
        
        service_name = services[0]["name"]
        print(f"Using project_id: {project_id} and service_name: {service_name}")
        
        # Create a CPU entry with data points
        new_cpu_entry = {
            "project_id": project_id,
            "service_name": service_name,
            "data": [
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "load": 45.2,
                    "memory": 256.7,
                    "threads": 12
                }
            ]
        }
        
        response = await client.post("/api/metrics/cpu", json=new_cpu_entry)
        assert response.status_code == status.HTTP_201_CREATED
        created_entry = response.json()
        entry_id = created_entry["id"]
        
        # Add new data points to the entry
        updated_data = {
            "data": [
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "load": 50.1,
                    "memory": 280.3,
                    "threads": 15
                }
            ]
        }
        
        response = await client.put(f"/api/metrics/cpu/{entry_id}", json=updated_data)
        assert response.status_code == status.HTTP_200_OK
        updated_entry = response.json()
        # Verify the data was updated
        assert len(updated_entry["data"]) > 0


@pytest.mark.asyncio
async def test_delete_cpu_entry(client: AsyncClient):
    """Test deleting a CPU entry."""
    # First create a CPU entry
    response = await client.get("/api/projects/")
    assert response.status_code == status.HTTP_200_OK
    projects = response.json()
    
    if projects:
        project_id = projects[0]["id"]
        
        # Get services for this specific project
        response = await client.get(f"/api/services/project/{project_id}")
        assert response.status_code == status.HTTP_200_OK, f"Failed to get services: {response.text}"

        services = response.json()
        assert services, f"No services available for project {project_id}"
        
        service_name = services[0]["name"]
        print(f"Using project_id: {project_id} and service_name: {service_name}")
        
        # Create a CPU entry to delete
        new_cpu_entry = {
            "project_id": project_id,
            "service_name": service_name,
            "data": [
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "load": 45.2,
                    "memory": 256.7,
                    "threads": 12
                }
            ]
        }
        
        response = await client.post("/api/metrics/cpu", json=new_cpu_entry)
        assert response.status_code == status.HTTP_201_CREATED
        created_entry = response.json()
        entry_id = created_entry["id"]
        
        # Delete the CPU entry
        response = await client.delete(f"/api/metrics/cpu/{entry_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it was deleted
        response = await client.get(f"/api/metrics/cpu/{entry_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_add_cpu_data_point(client: AsyncClient):
    """Test adding a new data point to an existing CPU entry."""
    # First create a CPU entry
    response = await client.get("/api/projects/")
    assert response.status_code == status.HTTP_200_OK
    projects = response.json()
    
    if projects:
        project_id = projects[0]["id"]
        
        # Get services for this specific project
        response = await client.get(f"/api/services/project/{project_id}")
        assert response.status_code == status.HTTP_200_OK, f"Failed to get services: {response.text}"

        services = response.json()
        assert services, f"No services available for project {project_id}"
        
        service_name = services[0]["name"]
        print(f"Using project_id: {project_id} and service_name: {service_name}")
        
        # Create a CPU entry
        new_cpu_entry = {
            "project_id": project_id,
            "service_name": service_name,
            "data": [
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "load": 45.2,
                    "memory": 256.7,
                    "threads": 12
                }
            ]
        }
        
        response = await client.post("/api/metrics/cpu", json=new_cpu_entry)
        assert response.status_code == status.HTTP_201_CREATED
        created_entry = response.json()
        entry_id = created_entry["id"]
        initial_data_count = len(created_entry["data"])
        
        # Add a new data point
        new_data_point = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "load": 55.3,
            "memory": 300.1,
            "threads": 14
        }
        
        response = await client.post(f"/api/metrics/cpu/{entry_id}/data", json=new_data_point)
        assert response.status_code == status.HTTP_200_OK
        updated_entry = response.json()
        # Verify the data point was added
        assert len(updated_entry["data"]) > initial_data_count


@pytest.mark.asyncio
async def test_invalid_cpu_entry_data(client: AsyncClient):
    """Test validation of CPU entry data."""
    # Missing required fields
    invalid_entry = {
        "data": [
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "load": 45.2,
                "memory": 256.7,
                "threads": 12
            }
        ]
    }
    
    response = await client.post("/api/metrics/cpu", json=invalid_entry)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
