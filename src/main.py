from fastapi import FastAPI
from .api.v1 import compliance, attendance

app = FastAPI(title="HRMS Backend")

app.include_router(compliance.router, prefix="/api/v1")
app.include_router(attendance.router, prefix="/api/v1/attendance_tracking", tags=["Attendance Tracking"])

@app.get("/")
def read_root():
    return {"message": "HRMS Backend API"}