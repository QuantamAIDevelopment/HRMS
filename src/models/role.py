from sqlalchemy import Column, String
from .base import BaseModel

class Role(BaseModel):
    __tablename__ = "roles"
    
    name = Column(String, unique=True, index=True)
    description = Column(String)