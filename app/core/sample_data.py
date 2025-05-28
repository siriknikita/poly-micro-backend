from datetime import datetime, timedelta
import random
from typing import List, Dict, Any
from app.db.database import get_database
from app.schemas.log import Severity

async def generate_sample_data():
    """Generate and insert sample data if collections are empty"""
    db = get_database()
    
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
