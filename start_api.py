#!/usr/bin/env python3
"""Script to start the FastAPI backend server."""

import uvicorn
from database import init_database

if __name__ == "__main__":
    # Initialize database
    print("Initializing database...")
    init_database()
    print("Database initialized successfully!")
    
    # Start the API server
    print("Starting FastAPI server on http://localhost:8000")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)