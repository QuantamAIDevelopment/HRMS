#!/usr/bin/env python3
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import uvicorn
    print("Starting HRMS Backend server...")
    print("Server will be available at: http://127.0.0.1:8000")
    print("API Documentation: http://127.0.0.1:8000/docs")
    
    uvicorn.run(
        "src.main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True,
        log_level="info"
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install required dependencies: pip install fastapi uvicorn sqlalchemy")
except Exception as e:
    print(f"Error starting server: {e}")
    import traceback
    traceback.print_exc()