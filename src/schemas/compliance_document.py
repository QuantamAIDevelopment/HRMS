from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class ComplianceDocumentBase(BaseModel):
    title: str = Field(..., max_length=255)
    category: Literal['Policy', 'Compliance', 'Legal', 'Training']
    description: Optional[str] = None

class ComplianceDocumentCreate(ComplianceDocumentBase):
    uploaded_document: str  # Base64 encoded string

class ComplianceDocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    category: Optional[Literal['Policy', 'Compliance', 'Legal', 'Training']] = None
    description: Optional[str] = None
    uploaded_document: Optional[str] = None

class ComplianceDocumentResponse(ComplianceDocumentBase):
    document_id: int
    uploaded_by: str
    uploaded_on: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ComplianceDocumentDownload(ComplianceDocumentResponse):
    uploaded_document: str
