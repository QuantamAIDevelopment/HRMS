from fastapi import FastAPI

app = FastAPI(title="HRMS Backend")

@app.get("/")
def read_root():
    return {"message": "HRMS Backend API"}