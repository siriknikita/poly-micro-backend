"""
Entry point for the Poly Micro Manager Backend application.
Run this file to start the FastAPI server with uvicorn.
"""
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment or use defaults
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
RELOAD = os.getenv("RELOAD", "True").lower() in ("true", "1", "t")

if __name__ == "__main__":
    print(f"Starting Poly Micro Manager API on {HOST}:{PORT}")
    uvicorn.run(
        "app.main:app", 
        host=HOST, 
        port=PORT, 
        reload=RELOAD
    )
