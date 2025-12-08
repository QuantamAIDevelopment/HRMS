from sqlalchemy import Column, Integer, String, Date, Text, Numeric, DateTime
from sqlalchemy.sql import func
from .base import Base

class Timesheet(Base):
    __tablename__ = "time_entries"
    __table_args__ = {'extend_existing': True}

    time_entry_id = Column(String(50), primary_key=True, index=True, nullable=False)
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
            from sqlalchemy import text
            result = db.execute(text("SELECT time_entry_id FROM time_entries WHERE time_entry_id LIKE 'TE%' ORDER BY time_entry_id DESC LIMIT 1")).fetchone()
            if result and result[0]:
                last_num = int(result[0][2:])
                new_num = last_num + 1
            else:
                new_num = 1
            return f"TE{new_num:06d}"
        except:
            return "TE000001"

