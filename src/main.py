from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1 import leave_router, asset_router, attendance_router
from src.models.base import Base
from src.models.session import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="HRMS Backend API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leave_router, prefix="/api/v1")
app.include_router(asset_router, prefix="/api/v1")
app.include_router(attendance_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "HRMS Backend API", "version": "1.0.0", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)