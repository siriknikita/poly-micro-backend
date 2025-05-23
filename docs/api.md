# API Documentation

This document provides details about the RESTful API endpoints available in the Poly Micro Manager backend.

## Base URL

When running locally:
```
http://localhost:8000
```

## Authentication

Currently, the API doesn't require authentication.

## API Endpoints

### Projects

#### Get All Projects

```
GET /api/projects
```

Returns a list of all projects.

**Response**
```json
[
  {
    "id": "string",
    "name": "string",
    "description": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
]
```

#### Get Project by ID

```
GET /api/projects/{id}
```

Returns a single project by ID.

**Response**
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Create Project

```
POST /api/projects
```

Creates a new project.

**Request Body**
```json
{
  "name": "string",
  "description": "string"
}
```

**Response**
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Services

#### Get All Services

```
GET /api/services
```

Returns a list of all services.

**Response**
```json
[
  {
    "id": "string",
    "name": "string",
    "project_id": "string",
    "description": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
]
```

#### Get Services by Project ID

```
GET /api/services/project/{project_id}
```

Returns all services for a specific project.

**Response**
```json
[
  {
    "id": "string",
    "name": "string",
    "project_id": "string",
    "description": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
]
```

### Logs

#### Get All Logs

```
GET /api/logs
```

Returns a list of all logs.

**Query Parameters**
- `project_id` (optional): Filter logs by project ID
- `service_id` (optional): Filter logs by service ID
- `severity` (optional): Filter logs by severity level
- `start_date` (optional): Filter logs starting from this date
- `end_date` (optional): Filter logs until this date
- `skip` (optional): Number of records to skip
- `limit` (optional): Maximum number of records to return

**Response**
```json
[
  {
    "id": "string",
    "project_id": "string",
    "service_id": "string",
    "message": "string",
    "severity": "string",
    "timestamp": "datetime",
    "metadata": {}
  }
]
```

### Metrics

#### Get CPU Metrics

```
GET /api/metrics/cpu
```

Returns CPU metrics data.

**Query Parameters**
- `project_id` (optional): Filter by project ID
- `service_name` (optional): Filter by service name

**Response**
```json
[
  {
    "id": "string",
    "project_id": "string",
    "service_name": "string",
    "timestamp": "datetime",
    "cpu_usage": "number",
    "cpu_count": "number"
  }
]
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request

```json
{
  "detail": "Error message explaining the issue"
}
```

### 404 Not Found

```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

## Interactive Documentation

For interactive API documentation, you can use the Swagger UI:

```
http://localhost:8000/docs
```

Or ReDoc:

```
http://localhost:8000/redoc
```
