from fastapi import FastAPI
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi
from src.api.v1.auth import router as auth_router
from src.api.v1.users import router as users_router

app = FastAPI(
    title="HRMS Backend API",
    version="1.0.0",
    description="Human Resource Management System Backend",
    docs_url="/docs",
    redoc_url="/redoc"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="HRMS Backend API",
        version="1.0.0",
        description="Human Resource Management System Backend",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(users_router, prefix="/api/v1", tags=["users"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "HRMS Backend API is running", "docs": "/docs"}

@app.post("/test-email", tags=["Test"])
def test_email(email: str):
    from src.services.email_service import send_otp_email
    from src.core.security import generate_otp
    
    otp = generate_otp()
    result = send_otp_email(email, otp)
    
    return {
        "message": "Test email sent" if result else "Email sending failed",
        "email": email,
        "otp": otp,
        "success": result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8007)