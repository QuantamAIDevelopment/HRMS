from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1 import compliance, attendance

app = FastAPI(title="HRMS Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(compliance.router, prefix="/api/v1")
app.include_router(attendance.router, prefix="/api/v1/attendance_tracking", tags=["Attendance Tracking"])

@app.get("/")
def read_root():
    return {"message": "HRMS Backend API"}