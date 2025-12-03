from sqlalchemy import Column, Integer, String, Text, DateTime, CheckConstraint
from sqlalchemy.sql import func
from .base import Base

class ComplianceDocument(Base):
    __tablename__ = "compliance_documents_and_policy_management"
    
    document_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text)
    uploaded_document = Column(Text)
    uploaded_by = Column(String(50), nullable=False)
    uploaded_on = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint("category IN ('Policy','Compliance','Legal','Training')", name='check_category'),
    )
