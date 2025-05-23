"""
Migration script to update existing logs to match the new schema.

This script:
1. Adds required fields (project_id, service_id) to logs that don't have them
2. Converts uppercase severity values to lowercase
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from bson import ObjectId

# Define lowercase severity values
VALID_SEVERITIES = ["debug", "info", "warn", "error"]

async def fix_logs():
    """Update existing logs to match the new schema"""
    print("Starting logs migration...")
    
    # Connect to MongoDB
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db = client.poly_micro
    
    # Find all logs
    all_logs = await db.logs.find({}).to_list(length=None)
    print(f"Found {len(all_logs)} logs to check.")
    
    update_count = 0
    
    for log in all_logs:
        update_needed = False
        update_data = {}
        
        # Check for missing required fields
        if "project_id" not in log or not log.get("project_id"):
            update_data["project_id"] = "1"  # Default project ID
            update_needed = True
            
        if "service_id" not in log or not log.get("service_id"):
            update_data["service_id"] = "Unknown Service"  # Default service name
            update_needed = True
            
        # Check for uppercase severity values
        if "severity" in log and log["severity"] and isinstance(log["severity"], str):
            severity = log["severity"]
            if severity.lower() in VALID_SEVERITIES and severity != severity.lower():
                update_data["severity"] = severity.lower()
                update_needed = True
            elif severity.lower() not in VALID_SEVERITIES:
                update_data["severity"] = "info"  # Default to info
                update_needed = True
                
        # Check for missing message field
        if "message" not in log or not log.get("message"):
            update_data["message"] = "No message provided"
            update_needed = True
        
        # Perform update if needed
        if update_needed:
            result = await db.logs.update_one(
                {"_id": log["_id"]},
                {"$set": update_data}
            )
            if result.modified_count:
                update_count += 1
    
    print(f"Updated {update_count} logs to match the new schema.")

if __name__ == "__main__":
    asyncio.run(fix_logs())
