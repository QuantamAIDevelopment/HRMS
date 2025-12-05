from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1 import users, dashboard, health, teamlead_dashboard, manager_dashboard, hr_manager_dashboard, hr_executive_dashboard, non_employee_dashboard
from .models.base import Base
from .models.session import engine
from .models.all_models import *  # Import all models
import logging

app = FastAPI(title="HRMS Dashboard API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables with error handling
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Error creating tables: {e}")
    logging.error(f"Database table creation failed: {e}")

# Existing routers
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Employee Dashboard"])
app.include_router(teamlead_dashboard.router, prefix="/api/v1", tags=["Team Lead Dashboard"])
app.include_router(manager_dashboard.router, prefix="/api/v1", tags=["Manager Dashboard"])
app.include_router(hr_manager_dashboard.router, prefix="/api/v1", tags=["HR Manager Dashboard"])
app.include_router(hr_executive_dashboard.router, prefix="/api/v1", tags=["HR Executive Dashboard"])
app.include_router(non_employee_dashboard.router, prefix="/api/v1", tags=["Non-Employee Dashboard"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])

# HR Manager Dashboard routers


@app.get("/")
def read_root():
    return {"message": "HRMS Dashboard API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)