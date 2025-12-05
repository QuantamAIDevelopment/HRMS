from pydantic import BaseModel, EmailStr
from typing import Optional
from fastapi import UploadFile

class FileUploadRequest(BaseModel):
    email: EmailStr

class FileUploadResponse(BaseModel):
    id: int
    email: str
    message: str