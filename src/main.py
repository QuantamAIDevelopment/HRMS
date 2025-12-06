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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from api.v1.auth import router as auth_router
from api.v1.users import router as users_router
from api.v1.employees import router as employees_router
from api.v1.onboarding_simple import router as onboarding_router
from api.v1.expenses import router as expense_router
from api.v1.salary import router as salary_router
from api.v1.complete_employee import router as complete_employee_router
from api.v1.file_upload import router as file_upload_router


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
        error_msg = errors[0].get("ctx", {}).get("error", "JSON decode error")
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
            "detail": errors,
            "message": "Validation failed",
            "missing_fields": [error["loc"][-1] for error in errors if error["type"] == "missing"]
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
        "http://127.0.0.1:8005",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(users_router, prefix="/api/v1", tags=["users"])
app.include_router(employees_router, prefix="/api/v1", tags=["employees"])
app.include_router(onboarding_router, prefix="/api/v1", tags=["onboarding"])
app.include_router(complete_employee_router, prefix="/api/v1", tags=["complete-employee"])
app.include_router(expense_router, prefix="/api/v1", tags=["expenses"])
app.include_router(salary_router, prefix="/api/v1", tags=["salary"])
app.include_router(file_upload_router, prefix="/api/v1", tags=["file-upload"])


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "HRMS Backend API is running", "docs": "/docs"}





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)