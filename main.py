from pymongo.server_api import ServerApi
import motor.motor_asyncio
from fastapi import FastAPI, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field
from enum import Enum as PyEnum
from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware
import os
import dotenv
from datetime import datetime

dotenv.load_dotenv()

# Replace sync client with async Motor client
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"), server_api=ServerApi('1'))
db = client.Lab2  # Assuming database name, adjust if needed

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:5174/*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

class ProjectBase(BaseModel):
    name: str
    path: str

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class Project(ProjectBase):
    id: str
    
    class Config:
        populate_by_name = True

class ServiceBase(BaseModel):
    project_id: str
    name: str
    port: Optional[int] = None
    url: Optional[str] = None
    status: Optional[str] = None  # e.g., 'Running', 'Stopped'
    health: Optional[str] = None  # e.g., 'Healthy', 'Warning'
    uptime: Optional[str] = None
    version: Optional[str] = None
    last_deployment: Optional[str] = None

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    project_id: Optional[str] = None
    name: Optional[str] = None
    port: Optional[int] = None
    url: Optional[str] = None
    status: Optional[str] = None
    health: Optional[str] = None
    uptime: Optional[str] = None
    version: Optional[str] = None
    last_deployment: Optional[str] = None

class Service(ServiceBase):
    id: str
    
    class Config:
        populate_by_name = True

class Severity(str, PyEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"

class LogBase(BaseModel):
    service: str
    severity: Severity
    message: str
    timestamp: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    model_config = {
        "arbitrary_types_allowed": True
    }

class LogCreate(LogBase):
    pass

class LogUpdate(BaseModel):
    service: Optional[str] = None
    severity: Optional[Severity] = None
    message: Optional[str] = None
    timestamp: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    model_config = {
        "arbitrary_types_allowed": True
    }

class Log(LogBase):
    id: str
    
    class Config:
        populate_by_name = True

class CPUData(BaseModel):
    time: str
    load: float
    memory: float
    threads: int

class CPUDataCreate(BaseModel):
    time: str
    load: float
    memory: float
    threads: int

class CPUEntryBase(BaseModel):
    project_id: str
    service_name: str
    data: List[CPUData]

class CPUEntryCreate(BaseModel):
    project_id: str
    service_name: str
    data: List[CPUDataCreate]

class CPUEntryUpdate(BaseModel):
    data: Optional[List[CPUDataCreate]] = None

class CPUEntry(CPUEntryBase):
    id: Optional[str] = None
    
    class Config:
        populate_by_name = True

# Add startup event to insert sample data if collections are empty
@app.on_event("startup")
async def startup_event():
    if await db.projects.count_documents({}) == 0:
        await db.projects.insert_many([
            {"id": "1", "name": "E-commerce Platform", "path": "/path/to/ecommerce"},
            {"id": "2", "name": "Banking System", "path": "/path/to/banking"},
            {"id": "3", "name": "Healthcare Portal", "path": "/path/to/healthcare"},
            {"id": "4", "name": "Education Platform", "path": "/path/to/education"}
        ])
    if await db.services.count_documents({}) == 0:
        await db.services.insert_many([
            # Project 1 services
            {"project_id": "1", "name": "User Service", "port": 3001, "status": "Running", "health": "Healthy", "uptime": "5d 12h 30m", "version": "1.2.0", "last_deployment": "2024-02-25 14:30"},
            {"project_id": "1", "name": "Payment Service", "port": 3002, "status": "Running", "health": "Warning", "uptime": "3d 8h 15m", "version": "1.1.5", "last_deployment": "2024-02-26 09:45"},
            {"project_id": "1", "name": "Inventory Service", "port": 3003, "status": "Stopped", "health": "Critical", "uptime": "0d 0h 0m", "version": "1.0.0", "last_deployment": "2024-02-28 08:00"},
            
            # Project 2 services
            {"project_id": "2", "name": "User Service", "port": 3001, "status": "Running", "health": "Healthy", "uptime": "5d 12h 30m", "version": "1.2.0", "last_deployment": "2024-02-25 14:30"},
            {"project_id": "2", "name": "Payment Service", "port": 3002, "status": "Running", "health": "Warning", "uptime": "3d 8h 15m", "version": "1.1.5", "last_deployment": "2024-02-26 09:45"},
            {"project_id": "2", "name": "Loan Service", "port": 3004, "status": "Running", "health": "Healthy", "uptime": "4d 6h 20m", "version": "1.3.0", "last_deployment": "2024-02-24 11:00"},
            {"project_id": "2", "name": "Authentication Service", "port": 3005, "status": "Running", "health": "Healthy", "uptime": "7d 3h 45m", "version": "2.0.1", "last_deployment": "2024-02-22 16:20"},
            
            # Project 3 services
            {"project_id": "3", "name": "User Service", "port": 3001, "status": "Running", "health": "Healthy", "uptime": "5d 12h 30m", "version": "1.2.0", "last_deployment": "2024-02-25 14:30"},
            {"project_id": "3", "name": "Notification Service", "port": 3009, "status": "Running", "health": "Healthy", "uptime": "1d 10h 45m", "version": "1.0.2", "last_deployment": "2024-02-27 09:00"},
            {"project_id": "3", "name": "Authentication Service", "port": 3005, "status": "Running", "health": "Healthy", "uptime": "7d 3h 45m", "version": "2.0.1", "last_deployment": "2024-02-22 16:20"},
            {"project_id": "3", "name": "Health Monitoring Service", "port": 3007, "status": "Running", "health": "Healthy", "uptime": "3d 7h 50m", "version": "1.1.0", "last_deployment": "2024-02-26 12:45"},
            
            # Project 4 services
            {"project_id": "4", "name": "User Service", "port": 3001, "status": "Running", "health": "Healthy", "uptime": "5d 12h 30m", "version": "1.2.0", "last_deployment": "2024-02-25 14:30"},
            {"project_id": "4", "name": "Payment Service", "port": 3002, "status": "Running", "health": "Warning", "uptime": "3d 8h 15m", "version": "1.1.5", "last_deployment": "2024-02-26 09:45"},
            {"project_id": "4", "name": "Notification Service", "port": 3009, "status": "Running", "health": "Healthy", "uptime": "1d 10h 45m", "version": "1.0.2", "last_deployment": "2024-02-27 09:00"},
            {"project_id": "4", "name": "Course Management Service", "port": 3008, "status": "Running", "health": "Healthy", "uptime": "5d 4h 30m", "version": "1.2.1", "last_deployment": "2024-02-25 10:20"}
        ])
    if await db.logs.count_documents({}) == 0:
        await db.logs.insert_many([
            {"id": "1", "service": "User Service", "severity": "INFO", "message": "User authentication successful", "timestamp": "2024-02-28 12:00:00", "details": {"userId": "123", "method": "OAuth"}},
            {"id": "2", "service": "Payment Service", "severity": "ERROR", "message": "Payment processing failed", "timestamp": "2024-02-28 12:01:00", "details": {"transactionId": "tx_789", "errorCode": "INVALID_CARD"}}
            # Add more logs as needed
        ])
    if await db.cpu_data.count_documents({}) == 0:
        await db.cpu_data.insert_many([
            {
                "project_id": "1", "service_name": "User Service", "data": [
                    {"time": "2024-02-28 12:00:00", "load": 25.0, "memory": 40.0, "threads": 10},
                    {"time": "2024-02-28 12:05:00", "load": 26.0, "memory": 41.0, "threads": 11}
                ]
            },
            # Add more sample data for other services and projects as needed
        ])

# Project CRUD operations
@app.get("/projects", response_model=List[Project])
async def get_projects():
    """Get all projects"""
    return await db.projects.find().to_list(length=100)

@app.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str = Path(..., description="The ID of the project to get")):
    """Get a specific project by ID"""
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.post("/projects", response_model=Project, status_code=201)
async def create_project(project: ProjectCreate):
    """Create a new project"""
    # Generate a new ID (simple implementation)
    all_projects = await db.projects.find().to_list(length=1000)
    max_id = 0
    for p in all_projects:
        try:
            p_id = int(p["id"])
            if p_id > max_id:
                max_id = p_id
        except ValueError:
            continue
    
    new_id = str(max_id + 1)
    new_project = {"id": new_id, **project.model_dump()}
    
    await db.projects.insert_one(new_project)
    return new_project

@app.put("/projects/{project_id}", response_model=Project)
async def update_project(
    project: ProjectUpdate,
    project_id: str = Path(..., description="The ID of the project to update")
):
    """Update a project"""
    existing_project = await db.projects.find_one({"id": project_id})
    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    updated_project = {"id": project_id, **project.model_dump()}
    await db.projects.replace_one({"id": project_id}, updated_project)
    return updated_project

@app.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: str = Path(..., description="The ID of the project to delete")):
    """Delete a project"""
    delete_result = await db.projects.delete_one({"id": project_id})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")

# Service CRUD operations
@app.get("/services", response_model=List[Service])
async def get_all_services():
    """Get all services across all projects"""
    services = await db.services.find().to_list(length=100)
    # Convert _id to id for response compatibility
    for service in services:
        if "_id" in service:
            service["id"] = str(service["_id"])
    return services

@app.get("/services/{project_id}", response_model=List[Service])
async def get_services(project_id: str = Path(..., description="The ID of the project to get services for")):
    """Get all services for a specific project"""
    services = await db.services.find({"project_id": project_id}).to_list(length=100)
    # Convert _id to id for response compatibility
    for service in services:
        if "_id" in service:
            service["id"] = str(service["_id"])
    return services

@app.get("/services/detail/{service_id}", response_model=Service)
async def get_service(service_id: str = Path(..., description="The ID of the service to get")):
    """Get a specific service by ID"""
    from bson import ObjectId
    try:
        service = await db.services.find_one({"_id": ObjectId(service_id)})
    except:
        service = await db.services.find_one({"_id": service_id})
        
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Convert _id to id for response compatibility
    service["id"] = str(service["_id"])
    return service

@app.post("/services", response_model=Service, status_code=201)
async def create_service(service: ServiceCreate):
    """Create a new service"""
    # Validate that the referenced project exists
    project = await db.projects.find_one({"id": service.project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Handle the service creation
    service_dict = service.model_dump()
    result = await db.services.insert_one(service_dict)
    
    # Return the created service with its ID
    created_service = {**service_dict, "id": str(result.inserted_id)}
    return created_service

@app.put("/services/{service_id}", response_model=Service)
async def update_service(
    service: ServiceUpdate,
    service_id: str = Path(..., description="The ID of the service to update")
):
    """Update a service"""
    from bson import ObjectId
    
    # Check if service exists
    try:
        existing_service = await db.services.find_one({"_id": ObjectId(service_id)})
    except:
        existing_service = await db.services.find_one({"_id": service_id})
        
    if not existing_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # If project_id is being updated, validate that the new project exists
    if service.project_id and service.project_id != existing_service["project_id"]:
        project = await db.projects.find_one({"id": service.project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
    
    # Update only provided fields
    update_data = {k: v for k, v in service.model_dump().items() if v is not None}
    
    # Don't update with empty values
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid update data provided")
    
    # Perform the update
    try:
        await db.services.update_one({"_id": ObjectId(service_id)}, {"$set": update_data})
        updated_service = await db.services.find_one({"_id": ObjectId(service_id)})
    except:
        await db.services.update_one({"_id": service_id}, {"$set": update_data})
        updated_service = await db.services.find_one({"_id": service_id})
    
    # Convert _id to id for response compatibility
    updated_service["id"] = str(updated_service["_id"])
    return updated_service

@app.delete("/services/{service_id}", status_code=204)
async def delete_service(service_id: str = Path(..., description="The ID of the service to delete")):
    """Delete a service"""
    from bson import ObjectId
    
    try:
        delete_result = await db.services.delete_one({"_id": ObjectId(service_id)})
    except:
        delete_result = await db.services.delete_one({"_id": service_id})
        
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Service not found")
    return None

# Logs CRUD operations
@app.get("/logs", response_model=List[Log])
async def get_logs(service: Optional[str] = Query(None, description="Filter logs by service name"),
                 severity: Optional[Severity] = Query(None, description="Filter logs by severity")):
    """Get all logs with optional filtering"""
    filter_query = {}
    if service:
        filter_query["service"] = service
    if severity:
        filter_query["severity"] = severity.value
        
    logs = await db.logs.find(filter_query).to_list(length=100)
    return logs

@app.get("/logs/{log_id}", response_model=Log)
async def get_log(log_id: str = Path(..., description="The ID of the log to get")):
    """Get a specific log by ID"""
    log = await db.logs.find_one({"id": log_id})
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

@app.post("/logs", response_model=Log, status_code=201)
async def create_log(log: LogCreate):
    """Create a new log entry"""
    # Generate timestamp if not provided
    log_dict = log.model_dump()
    if not log_dict.get("timestamp"):
        log_dict["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Generate a new ID (simple implementation)
    all_logs = await db.logs.find().to_list(length=1000)
    max_id = 0
    for l in all_logs:
        try:
            l_id = int(l["id"])
            if l_id > max_id:
                max_id = l_id
        except ValueError:
            continue
    
    new_id = str(max_id + 1)
    log_dict["id"] = new_id
    
    # Create the log entry
    await db.logs.insert_one(log_dict)
    return log_dict

@app.put("/logs/{log_id}", response_model=Log)
async def update_log(
    log: LogUpdate,
    log_id: str = Path(..., description="The ID of the log to update")
):
    """Update a log entry"""
    existing_log = await db.logs.find_one({"id": log_id})
    if not existing_log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    # Update only provided fields
    update_data = {k: v for k, v in log.model_dump().items() if v is not None}
    
    # Don't update with empty values
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid update data provided")
    
    # Perform the update
    await db.logs.update_one({"id": log_id}, {"$set": update_data})
    updated_log = await db.logs.find_one({"id": log_id})
    return updated_log

@app.delete("/logs/{log_id}", status_code=204)
async def delete_log(log_id: str = Path(..., description="The ID of the log to delete")):
    """Delete a log entry"""
    delete_result = await db.logs.delete_one({"id": log_id})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Log not found")
    return None

# CPU metrics CRUD operations
@app.get("/cpu", response_model=List[CPUEntry])
async def get_all_cpu_data():
    """Get all CPU metrics data"""
    cpu_data = await db.cpu_data.find().to_list(length=100)
    # Convert _id to id for response compatibility
    for entry in cpu_data:
        if "_id" in entry:
            entry["id"] = str(entry["_id"])
    return cpu_data

@app.get("/cpu/{project_id}", response_model=List[CPUEntry])
async def get_cpu_data(project_id: str = Path(..., description="The project ID to get CPU data for")):
    """Get CPU metrics data for a specific project"""
    cpu_data = await db.cpu_data.find({"project_id": project_id}).to_list(length=100)
    # Convert _id to id for response compatibility
    for entry in cpu_data:
        if "_id" in entry:
            entry["id"] = str(entry["_id"])
    return cpu_data

@app.get("/cpu/service/{service_name}", response_model=List[CPUEntry])
async def get_cpu_data_by_service(service_name: str = Path(..., description="The service name to get CPU data for")):
    """Get CPU metrics data for a specific service"""
    cpu_data = await db.cpu_data.find({"service_name": service_name}).to_list(length=100)
    # Convert _id to id for response compatibility
    for entry in cpu_data:
        if "_id" in entry:
            entry["id"] = str(entry["_id"])
    return cpu_data

@app.get("/cpu/detail/{cpu_entry_id}", response_model=CPUEntry)
async def get_cpu_entry(cpu_entry_id: str = Path(..., description="The ID of the CPU entry to get")):
    """Get a specific CPU metrics entry by ID"""
    from bson import ObjectId
    try:
        cpu_entry = await db.cpu_data.find_one({"_id": ObjectId(cpu_entry_id)})
    except:
        cpu_entry = await db.cpu_data.find_one({"_id": cpu_entry_id})
        
    if not cpu_entry:
        raise HTTPException(status_code=404, detail="CPU metrics entry not found")
    
    # Convert _id to id for response compatibility
    cpu_entry["id"] = str(cpu_entry["_id"])
    return cpu_entry

@app.post("/cpu", response_model=CPUEntry, status_code=201)
async def create_cpu_entry(cpu_entry: CPUEntryCreate):
    """Create a new CPU metrics entry"""
    # Validate that the referenced project exists
    project = await db.projects.find_one({"id": cpu_entry.project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Validate that the service exists
    service = await db.services.find_one({"project_id": cpu_entry.project_id, "name": cpu_entry.service_name})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found for the given project")
    
    # Create the CPU metrics entry
    cpu_entry_dict = cpu_entry.model_dump()
    result = await db.cpu_data.insert_one(cpu_entry_dict)
    
    # Return the created entry with its ID
    created_entry = {**cpu_entry_dict, "id": str(result.inserted_id)}
    return created_entry

@app.put("/cpu/{cpu_entry_id}", response_model=CPUEntry)
async def update_cpu_entry(
    cpu_entry: CPUEntryUpdate,
    cpu_entry_id: str = Path(..., description="The ID of the CPU metrics entry to update")
):
    """Update a CPU metrics entry"""
    from bson import ObjectId
    
    # Check if the entry exists
    try:
        existing_entry = await db.cpu_data.find_one({"_id": ObjectId(cpu_entry_id)})
    except:
        existing_entry = await db.cpu_data.find_one({"_id": cpu_entry_id})
        
    if not existing_entry:
        raise HTTPException(status_code=404, detail="CPU metrics entry not found")
    
    # Update only provided fields
    update_data = {k: v for k, v in cpu_entry.model_dump().items() if v is not None}
    
    # Don't update with empty values
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid update data provided")
    
    # Perform the update
    try:
        await db.cpu_data.update_one({"_id": ObjectId(cpu_entry_id)}, {"$set": update_data})
        updated_entry = await db.cpu_data.find_one({"_id": ObjectId(cpu_entry_id)})
    except:
        await db.cpu_data.update_one({"_id": cpu_entry_id}, {"$set": update_data})
        updated_entry = await db.cpu_data.find_one({"_id": cpu_entry_id})
    
    # Convert _id to id for response compatibility
    updated_entry["id"] = str(updated_entry["_id"])
    return updated_entry

@app.delete("/cpu/{cpu_entry_id}", status_code=204)
async def delete_cpu_entry(cpu_entry_id: str = Path(..., description="The ID of the CPU metrics entry to delete")):
    """Delete a CPU metrics entry"""
    from bson import ObjectId
    
    try:
        delete_result = await db.cpu_data.delete_one({"_id": ObjectId(cpu_entry_id)})
    except:
        delete_result = await db.cpu_data.delete_one({"_id": cpu_entry_id})
        
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="CPU metrics entry not found")
    return None

@app.post("/cpu/{cpu_entry_id}/data", response_model=CPUEntry)
async def add_cpu_data_point(
    cpu_data: CPUDataCreate,
    cpu_entry_id: str = Path(..., description="The ID of the CPU metrics entry to add data to")
):
    """Add a new data point to an existing CPU metrics entry"""
    from bson import ObjectId
    
    # Check if the entry exists
    try:
        existing_entry = await db.cpu_data.find_one({"_id": ObjectId(cpu_entry_id)})
    except:
        existing_entry = await db.cpu_data.find_one({"_id": cpu_entry_id})
        
    if not existing_entry:
        raise HTTPException(status_code=404, detail="CPU metrics entry not found")
    
    # Add the new data point
    new_data_point = cpu_data.model_dump()
    
    try:
        await db.cpu_data.update_one(
            {"_id": ObjectId(cpu_entry_id)},
            {"$push": {"data": new_data_point}}
        )
        updated_entry = await db.cpu_data.find_one({"_id": ObjectId(cpu_entry_id)})
    except:
        await db.cpu_data.update_one(
            {"_id": cpu_entry_id},
            {"$push": {"data": new_data_point}}
        )
        updated_entry = await db.cpu_data.find_one({"_id": cpu_entry_id})
    
    # Convert _id to id for response compatibility
    updated_entry["id"] = str(updated_entry["_id"])
    return updated_entry

@app.get("/")
def read_root():
    return {"message": "FastAPI server is running"}

from datetime import datetime, timedelta
import random

def generate_mock_data(start_time: datetime) -> list[dict]:
    return [
        {
            "time": (start_time + timedelta(minutes=5 * i)).strftime("%Y-%m-%d %H:%M:%S"),
            "load": round(25 + random.random() * 60, 2),
            "memory": round(40 + random.random() * 45, 2),
            "threads": random.randint(10, 30),
        }
        for i in range(24)
    ]

async def insert_mock_cpu_data():

    start_time = datetime.now() - timedelta(minutes=23 * 5)
    projects = {
        '1': ['User Service', 'Payment Service', 'Inventory Service'],
        '2': ['User Service', 'Payment Service', 'Loan Service', 'Authentication Service'],
        '3': ['User Service', 'Notification Service', 'Authentication Service', 'Health Monitoring Service'],
        '4': ['User Service', 'Payment Service', 'Notification Service', 'Course Management Service']
    }

    documents = []
    for project_id, services in projects.items():
        for service_name in services:
            data = generate_mock_data(start_time)
            documents.append({
                "project_id": project_id,
                "service_name": service_name,
                "data": data
            })

    await db.cpu_data.insert_many(documents)
    print(f"Inserted mock CPU data for {len(documents)} services.")

@app.on_event("startup")
async def startup_event():
    pass