from fastapi import FastAPI
from .api.v1.job_titles import router as job_title_router
from .api.v1.timesheet import router as timesheet_router
from .api.v1.employee import router as employee_router
from .api.v1.profile import router as profile_router
from .api.v1.approval import router as approval_router

app = FastAPI(title="HRMS Backend")

# Include routers
app.include_router(job_title_router)
app.include_router(timesheet_router)
app.include_router(employee_router)
app.include_router(profile_router)
app.include_router(approval_router)

@app.get("/")
def read_root():
    return {"message": "HRMS Backend API"}
