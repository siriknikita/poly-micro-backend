import asyncio
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any
from app.db.database import get_database
from app.schemas.log import Severity

async def generate_sample_data():
    """Generate and insert sample data if collections are empty"""
    db = get_database()
    
    # Sample projects
    projects = [
        {"id": "1", "name": "E-commerce Platform", "path": "/path/to/ecommerce"},
        {"id": "2", "name": "Banking System", "path": "/path/to/banking"},
        {"id": "3", "name": "Healthcare Portal", "path": "/path/to/healthcare"},
        {"id": "4", "name": "Education Platform", "path": "/path/to/education"}
    ]
    
    # Sample services
    services = [
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
    ]
    
    # Sample logs
    logs = [
        {"id": "1", "service": "User Service", "severity": "INFO", "message": "User authentication successful", "timestamp": "2024-02-28 12:00:00", "details": {"userId": "123", "method": "OAuth"}},
        {"id": "2", "service": "Payment Service", "severity": "ERROR", "message": "Payment processing failed", "timestamp": "2024-02-28 12:01:00", "details": {"transactionId": "tx_789", "errorCode": "INVALID_CARD"}},
        {"id": "3", "service": "Notification Service", "severity": "WARN", "message": "Email delivery delayed: Rate limit exceeded", "timestamp": "2024-02-28 12:02:00", "details": {"emailId": "em_456", "retryCount": 2}},
        {"id": "4", "service": "Authentication Service", "severity": "DEBUG", "message": "Token refresh completed", "timestamp": "2024-02-28 12:03:00", "details": {"userId": "124", "tokenType": "refresh"}},
        {"id": "5", "service": "User Service", "severity": "ERROR", "message": "User authentication failed: Invalid credentials", "timestamp": "2024-02-28 12:05:00", "details": {"userId": "125", "method": "OAuth"}},
        {"id": "6", "service": "Payment Service", "severity": "INFO", "message": "Payment processed successfully", "timestamp": "2024-02-28 12:06:00", "details": {"transactionId": "tx_790", "amount": 100}},
        {"id": "7", "service": "Notification Service", "severity": "INFO", "message": "Notification sent successfully", "timestamp": "2024-02-28 12:07:00", "details": {"notificationId": "notif_123", "recipient": "user@example.com"}},
        {"id": "8", "service": "Authentication Service", "severity": "ERROR", "message": "Token refresh failed: Expired token", "timestamp": "2024-02-28 12:08:00", "details": {"userId": "126", "tokenType": "refresh"}}
    ]
    
    # Insert sample projects if collection is empty
    if await db.projects.count_documents({}) == 0:
        await db.projects.insert_many(projects)
        print(f"Inserted {len(projects)} sample projects.")
        
    # Insert sample services if collection is empty
    if await db.services.count_documents({}) == 0:
        await db.services.insert_many(services)
        print(f"Inserted {len(services)} sample services.")
        
    # Insert sample logs if collection is empty
    if await db.logs.count_documents({}) == 0:
        await db.logs.insert_many(logs)
        print(f"Inserted {len(logs)} sample logs.")
        
    # Generate and insert sample CPU data if collection is empty
    if await db.cpu_data.count_documents({}) == 0:
        await generate_sample_cpu_data()
        print("Inserted sample CPU data.")
        
async def generate_sample_cpu_data():
    """Generate and insert sample CPU metrics data"""
    db = get_database()
    
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
    
    if documents:
        await db.cpu_data.insert_many(documents)
        print(f"Inserted mock CPU data for {len(documents)} services.")

def generate_mock_data(start_time: datetime) -> List[Dict[str, Any]]:
    """Generate mock CPU data points"""
    return [
        {
            "time": (start_time + timedelta(minutes=5 * i)).strftime("%Y-%m-%d %H:%M:%S"),
            "load": round(25 + random.random() * 60, 2),
            "memory": round(40 + random.random() * 45, 2),
            "threads": random.randint(10, 30),
        }
        for i in range(24)
    ]
