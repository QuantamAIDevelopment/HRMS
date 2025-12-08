from pydantic import BaseModel
from datetime import date

class TimesheetStatusUpdate(BaseModel):
    entry_date: date
    status: str