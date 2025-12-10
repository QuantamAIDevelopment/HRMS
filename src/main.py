import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging

# Import all routers
from api.v1.auth import router as auth_router
from api.v1.expenses import router as expense_router
from api.v1.salary import router as salary_router
from api.v1.file_upload import router as file_upload_router
from api.v1.complete_employee import router as complete_employee_router
from .api.v1 import compliance, attendance, employees, departments, standard_policy, unified_dashboard, leave_router, asset_router
from .api.v1.job_titles import router as job_title_router
from .api.v1.timesheet import router as timesheet_router
from .api.v1.employee import router as employee_router
from .api.v1.profile import router as profile_router
from .api.v1.approval import router as approval_router
from .api.v1.shifts import router as shifts_router
from .api.v1.off_boarding import router as off_boarding_router
from .api.v1.events_holidays import router as events_holidays_router
from .core.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HRMS Backend API",
    version="1.0.0",
    description="Human Resource Management System - Complete Employee Onboarding",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    logger.error(f"Validation error on {request.url}: {errors}")
    
    if any(e.get("type") == "json_invalid" for e in errors):
        error_msg = str(errors[0].get("ctx", {}).get("error", "JSON decode error"))
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Invalid JSON format in request body",
                "error": error_msg,
                "hint": "Check line 7 around character 76 - likely missing comma between fields"
            }
        )
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": str(errors),
            "message": "Validation failed",
            "missing_fields": [error["loc"][-1] for error in errors if error["type"] == "missing"]
        }
    )

# Add global exception handler for Internal Server Errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    error_traceback = traceback.format_exc()
    logger.error(f"Internal Server Error on {request.url}: {str(exc)}")
    logger.error(f"Full traceback: {error_traceback}")
    print(f"GLOBAL ERROR: {type(exc).__name__}: {str(exc)}")
    print(f"TRACEBACK: {error_traceback}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal Server Error: {type(exc).__name__}: {str(exc)}",
            "error_type": type(exc).__name__,
            "traceback": error_traceback.split('\n')[-10:]  # Last 10 lines of traceback
        }
    )

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(expense_router, prefix="/api/v1", tags=["expenses"])
app.include_router(salary_router, prefix="/api/v1", tags=["salary"])
app.include_router(file_upload_router, prefix="/api/v1", tags=["file-upload"])
app.include_router(complete_employee_router, prefix="/api/v1", tags=["complete-employee"])
app.include_router(employees.router, prefix="/api/v1")
app.include_router(departments.router, prefix="/api/v1")
app.include_router(compliance.router, prefix="/api/v1/compliance", tags=["Compliance Documents"])
app.include_router(attendance.router, prefix="/api/v1/attendance_tracking", tags=["Attendance Tracking"])
app.include_router(standard_policy.router)
app.include_router(job_title_router, prefix="/api/v1/job-titles", tags=["job-titles"])
app.include_router(timesheet_router, prefix="/api/v1/timesheets", tags=["timesheets"])
app.include_router(employee_router, prefix="/api/v1/employees", tags=["employees"])
app.include_router(profile_router, prefix="/api/v1/profile", tags=["profile"])
app.include_router(approval_router, prefix="/api/v1/approval", tags=["approval"])
app.include_router(shifts_router, prefix="/api/v1/shifts", tags=["shifts"])
app.include_router(off_boarding_router, prefix="/api/v1/off-boarding", tags=["off-boarding"])
app.include_router(events_holidays_router, prefix="/api/v1/events-holidays", tags=["events-holidays"])
app.include_router(unified_dashboard.router, prefix="/api/v1", tags=["Unified Dashboard"])
app.include_router(leave_router, prefix="/api/v1")
app.include_router(asset_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def read_root():
    logger.info("Root endpoint hit")
    return {"message": "HRMS Backend API is running", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)