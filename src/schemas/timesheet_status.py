from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Union

class TimesheetStatusUpdate(BaseModel):
    entry_date: Union[date, str]
    status: str
    
    @field_validator('entry_date')
    @classmethod
    def validate_entry_date(cls, v):
        if isinstance(v, str):
            try:
                # Try multiple date formats
                for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y'):
                    try:
                        return datetime.strptime(v, fmt).date()
                    except ValueError:
                        continue
                raise ValueError('Invalid date format')
            except ValueError:
                raise ValueError('Invalid date format. Use YYYY-MM-DD, DD-MM-YYYY, MM/DD/YYYY, or DD/MM/YYYY')
        return v