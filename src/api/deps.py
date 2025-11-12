from fastapi import Depends
from sqlalchemy.orm import Session
from ..models.session import get_db

def get_current_user():
    pass