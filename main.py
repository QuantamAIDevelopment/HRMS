import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from src.api.v1.auth import router as auth_router
from src.api.v1.users import router as users_router
from src.api.v1.payroll_routes import router as payroll_router
from src.api.v1.expenses import router as expenses_router

app = FastAPI(
    title="HRMS Backend API",
    version="1.0.0",
    description="Human Resource Management System Backend with JWT Authentication"
)

# Simple approach - just add the security scheme
app.openapi_schema = None

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(users_router, prefix="/api/v1", tags=["users"])
app.include_router(payroll_router, prefix="/api/v1", tags=["payroll"])
app.include_router(expenses_router, prefix="/api/v1", tags=["expenses"])

@app.get("/")
def read_root():
    return {"message": "HRMS Backend API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)