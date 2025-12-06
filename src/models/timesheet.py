from sqlalchemy import Column, Integer, String, Date, Text, Numeric, DateTime
from sqlalchemy.sql import func
from .base import Base

class Timesheet(Base):
    __tablename__ = "time_entries"

    id = Column(Integer, primary_key=True, index=True)
    time_entry_id = Column(String(50), unique=True, index=True, nullable=False)
    employee_id = Column(String(50))
    entry_date = Column(Date)
    project = Column(String(150))
    task_description = Column(Text)
    hours = Column(Numeric(5, 2))
    status = Column(String(50), default="PENDING_MANAGER_APPROVAL")
    approver_id = Column(String(50))
    approver_type = Column(String(20))  # MANAGER, HR_MANAGER, HR_EXECUTIVE
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    @staticmethod
    def generate_time_entry_id(db):
        try:
            last_entry = db.query(Timesheet).order_by(Timesheet.id.desc()).first()
            if last_entry and last_entry.time_entry_id and last_entry.time_entry_id.startswith('TE'):
                last_num = int(last_entry.time_entry_id[2:])
                new_num = last_num + 1
            else:
                new_num = 1
            return f"TE{new_num:06d}"
        except:
            return "TE000001"

