#!/usr/bin/env python
"""
Poly Micro Manager Logging Demo

This script demonstrates the logging functionality for Poly Micro Manager.
It creates sample services that log messages to the MongoDB database,
which can then be viewed in the Poly Micro Manager dashboard.

Usage:
  python run_logging_demo.py
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure MongoDB connection is available
if not os.getenv("MONGO_URI"):
    print("Error: MONGO_URI environment variable is not set.")
    print("Please set it in the .env file or export it in your shell.")
    sys.exit(1)

# Import the setup and demo code
from app.demo.setup_demo_project import setup_demo
from app.demo.run_demo import run_demo

async def main():
    # First, set up the project and services in the database
    print("Setting up demo project and services...")
    demo_data = await setup_demo()
    
    # Get the project and service IDs
    project_id = demo_data["project_id"]
    service_ids = demo_data["service_ids"]
    
    print(f"\nUsing Project ID: {project_id}")
    print("Using Service IDs:")
    for demo_id, actual_id in service_ids.items():
        print(f"  {demo_id} -> {actual_id}")
    
    # Run the actual demo with these IDs
    print("\nStarting the logging demo...")
    await run_demo(project_id, service_ids)

if __name__ == "__main__":
    print("Starting Poly Micro Manager Logging Demo...")
    asyncio.run(main())
