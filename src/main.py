import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routers from v1 API
from src.api.v1.auth import router as auth_router
from src.api.v1.expenses import router as expense_router
from src.api.v1.salary import router as salary_router
from src.api.v1.file_upload import router as file_upload_router
from src.api.v1.complete_employee import router as complete_employee_router
from src.api.v1 import compliance, attendance, employees, departments, standard_policy, unified_dashboard, leave_router, asset_router
from src.api.v1.job_titles import router as job_title_router
from src.api.v1.timesheet import router as timesheet_router
from src.api.v1.employee import router as employee_router
from src.api.v1.profile import router as profile_router
from src.api.v1.approval import router as approval_router
from src.api.v1.shifts import router as shifts_router
from src.api.v1.off_boarding import router as off_boarding_router
from src.api.v1.events_holidays import router as events_holidays_router

try:
    from src.core.logging_config import setup_logging
    setup_logging()
except ImportError:
    pass

app = FastAPI(
    title="HRMS Backend API",
    description="Human Resource Management System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

# Add custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    logger.error(f"Validation error on {request.url}: {errors}")
    
    if any(e.get("type") == "json_invalid" for e in errors):
        error_msg = errors[0].get("ctx", {}).get("error", "JSON decode error")
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Invalid JSON format in request body",
                "error": error_msg,
            }
        )
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": [{"loc": e["loc"], "msg": e["msg"], "type": e["type"]} for e in errors],
            "message": "Validation failed",
        }
    )

# Add global exception handler for Internal Server Errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    error_traceback = traceback.format_exc()
    logger.error(f"Internal Server Error on {request.url}: {str(exc)}")
    logger.error(f"Full traceback: {error_traceback}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal Server Error: {type(exc).__name__}: {str(exc)}",
            "error_type": type(exc).__name__,
        }
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8005",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8001",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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
    return {"message": "HRMS Backend API", "version": "1.0.0", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    from fastapi.responses import FileResponse
    return FileResponse("favicon.ico", media_type="image/x-icon")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
