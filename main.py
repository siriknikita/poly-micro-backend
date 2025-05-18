from pymongo.server_api import ServerApi
import motor.motor_asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum as PyEnum
from typing import List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
import os
import dotenv

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

class Project(BaseModel):
    id: str
    name: str
    path: str

class Service(BaseModel):
    _id: str | None = None
    project_id: str
    name: str
    port: int | None = None
    url: str | None = None
    status: str | None = None  # e.g., 'Running', 'Stopped'
    health: str | None = None  # e.g., 'Healthy', 'Warning'
    uptime: str | None = None
    version: str | None = None
    last_deployment: str | None = None

class Severity(str, PyEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"

class Log(BaseModel):
    model_config = {
        "arbitrary_types_allowed": True
    }
    id: str
    service: str
    severity: Severity
    message: str
    timestamp: str
    details: Dict[str, Any] | None = None

class CPUData(BaseModel):
    time: str
    load: float
    memory: float
    threads: int

class CPUEntry(BaseModel):
    service_name: str
    data: List[CPUData]

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
            {"project_id": "1", "name": "User Service", "port": 3001, "status": "Running", "health": "Healthy", "uptime": "5d 12h 30m", "version": "1.2.0", "last_deployment": "2024-02-25 14:30"},
            {"project_id": "1", "name": "Payment Service", "port": 3002, "status": "Running", "health": "Healthy", "uptime": "4d 10h 20m", "version": "2.1.0", "last_deployment": "2024-02-26 15:45"},
            {"project_id": "1", "name": "Inventory Service", "port": 3003, "status": "Running", "health": "Warning", "uptime": "3d 8h 15m", "version": "1.0.5", "last_deployment": "2024-02-27 09:00"},
            # Add more services for other projects as needed
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

# Pydantic models remain, endpoints modified to query DB
@app.get("/projects", response_model=List[Project])
async def get_projects():
    return await db.projects.find().to_list(length=100)

@app.get("/services/{project_id}", response_model=List[Service])
async def get_services(project_id: str):
    return await db.services.find({"project_id": project_id}).to_list(length=100)

@app.get("/logs", response_model=List[Log])
async def get_logs():
    return await db.logs.find().to_list(length=100)

@app.get("/cpu/{project_id}", response_model=List[CPUEntry])
async def get_cpu_data(project_id: str):
    return await db.cpu_data.find({"project_id": project_id}, {'_id': 0}).to_list(length=100)

@app.get("/")
def read_root():
    return {"message": "FastAPI server is running"}
