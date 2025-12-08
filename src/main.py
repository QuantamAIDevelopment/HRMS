from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1 import compliance, attendance, employees, departments, standard_policy
from .api.v1 import unified_dashboard
from .core.logging_config import setup_logging

# Setup logging
setup_logging()

app = FastAPI(
    title="HRMS Backend",
    description="Human Resource Management System API",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(employees.router, prefix="/api/v1")
app.include_router(departments.router, prefix="/api/v1")
app.include_router(compliance.router, prefix="/api/v1/compliance", tags=["Compliance Documents"])
app.include_router(attendance.router, prefix="/api/v1/attendance_tracking", tags=["Attendance Tracking"])
app.include_router(standard_policy.router)


# Existing routers

app.include_router(unified_dashboard.router, prefix="/api/v1", tags=["Unified Dashboard"])


# HR Manager Dashboard routers


@app.get("/")
def read_root():
    return {"message": "HRMS Backend API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
    return {"message": "HRMS Dashboard API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)