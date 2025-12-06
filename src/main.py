from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.job_titles import router as job_title_router
from .api.v1.timesheet import router as timesheet_router
from .api.v1.employee import router as employee_router
from .api.v1.profile import router as profile_router
from .api.v1.approval import router as approval_router
from .api.v1.shifts import router as shifts_router
from .api.v1.off_boarding import router as off_boarding_router
from .api.v1.events_holidays import router as events_holidays_router

app = FastAPI(title="HRMS Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(job_title_router, prefix="/api/v1/job-titles", tags=["job-titles"])
app.include_router(timesheet_router, prefix="/api/v1/timesheets", tags=["timesheets"])
app.include_router(employee_router, prefix="/api/v1/employees", tags=["employees"])
app.include_router(profile_router, prefix="/api/v1/profile", tags=["profile"])
app.include_router(approval_router, prefix="/api/v1/approval", tags=["approval"])
app.include_router(shifts_router, prefix="/api/v1/shifts", tags=["shifts"])
app.include_router(off_boarding_router, prefix="/api/v1/off-boarding", tags=["off-boarding"])
app.include_router(events_holidays_router, prefix="/api/v1/events-holidays", tags=["events-holidays"])

@app.get("/")
def read_root():
    return {"message": "HRMS Backend API"}
