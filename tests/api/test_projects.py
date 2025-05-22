"""Integration tests for the projects API endpoints."""
import pytest
from bson import ObjectId
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_get_all_projects(client: AsyncClient):
    """Test getting all projects."""
    response = await client.get("/api/projects/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    # Verify the structure of a project
    if data:
        project = data[0]
        assert "id" in project
        assert "name" in project
        assert "path" in project


@pytest.mark.asyncio
async def test_get_project_by_id(client: AsyncClient, test_db):
    """Test getting a project by ID."""
    # First, get all projects to find an ID
    response = await client.get("/api/projects/")
    assert response.status_code == status.HTTP_200_OK
    projects = response.json()
    
    if projects:
        project_id = projects[0]["id"]
        # Test getting the specific project
        response = await client.get(f"/api/projects/{project_id}")
        assert response.status_code == status.HTTP_200_OK
        project = response.json()
        assert project["id"] == project_id
    
    # Test with invalid ID
    response = await client.get(f"/api/projects/{str(ObjectId())}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient):
    """Test creating a new project."""
    new_project = {
        "name": "Test Project",
        "path": "/path/to/test-project"
    }
    
    response = await client.post("/api/projects/", json=new_project)
    assert response.status_code == status.HTTP_201_CREATED
    created_project = response.json()
    assert created_project["name"] == new_project["name"]
    assert created_project["path"] == new_project["path"]
    assert "id" in created_project
    
    # Verify the project was actually created
    response = await client.get(f"/api/projects/{created_project['id']}")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient):
    """Test updating a project."""
    # First, create a project to update
    new_project = {
        "name": "Project to Update",
        "path": "/path/to/update-project"
    }
    
    response = await client.post("/api/projects/", json=new_project)
    assert response.status_code == status.HTTP_201_CREATED
    project_id = response.json()["id"]
    
    # Update the project
    updated_data = {
        "name": "Updated Project",
        "path": "/path/to/updated-project"
    }
    
    response = await client.put(f"/api/projects/{project_id}", json=updated_data)
    assert response.status_code == status.HTTP_200_OK
    updated_project = response.json()
    assert updated_project["name"] == updated_data["name"]
    assert updated_project["path"] == updated_data["path"]
    
    # Verify the update was persisted
    response = await client.get(f"/api/projects/{project_id}")
    assert response.status_code == status.HTTP_200_OK
    project = response.json()
    assert project["name"] == updated_data["name"]


@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient):
    """Test deleting a project."""
    # First, create a project to delete
    new_project = {
        "name": "Project to Delete",
        "path": "/path/to/delete-project"
    }
    
    response = await client.post("/api/projects/", json=new_project)
    assert response.status_code == status.HTTP_201_CREATED
    project_id = response.json()["id"]
    
    # Delete the project
    response = await client.delete(f"/api/projects/{project_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify the project was deleted
    response = await client.get(f"/api/projects/{project_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_invalid_project_data(client: AsyncClient):
    """Test validation of project data."""
    # Missing required field (path)
    invalid_project = {
        "name": "Project with missing path"
    }
    
    response = await client.post("/api/projects/", json=invalid_project)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
