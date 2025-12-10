from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from fastapi import HTTPException, status
from ..models.compliance_document import ComplianceDocument
from ..schemas.compliance_document import ComplianceDocumentCreate, ComplianceDocumentUpdate

class ComplianceService:
    
    @staticmethod
    def check_upload_permission(designation: str) -> bool:
        """Check if user has permission to upload documents"""
        allowed_roles = ['HR Manager', 'HR Executive']
        return designation in allowed_roles
    
    @staticmethod
    def create_document(
        db: Session,
        document: ComplianceDocumentCreate,
        employee_id: str,
        designation: str
    ) -> ComplianceDocument:
        """Create a new compliance document"""
        if not ComplianceService.check_upload_permission(designation):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only HR Manager or HR Executive can upload documents"
            )
        
        db_document = ComplianceDocument(
            title=document.title,
            category=document.category,
            description=document.description,
            uploaded_document=document.uploaded_document,
            uploaded_by=employee_id
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document
    
    @staticmethod
    def get_document(db: Session, document_id: int) -> Optional[ComplianceDocument]:
        """Get a single document by ID"""
        return db.query(ComplianceDocument).filter(
            ComplianceDocument.document_id == document_id
        ).first()
    
    @staticmethod
    def get_all_documents(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None
    ) -> List[ComplianceDocument]:
        """Get all documents with optional filtering"""
        query = db.query(ComplianceDocument)
        if category:
            query = query.filter(ComplianceDocument.category == category)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_document(
        db: Session,
        document_id: int,
        document_update: ComplianceDocumentUpdate,
        designation: str
    ) -> ComplianceDocument:
        """Update an existing document"""
        if not ComplianceService.check_upload_permission(designation):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only HR Manager or HR Executive can update documents"
            )
        
        db_document = ComplianceService.get_document(db, document_id)
        if not db_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        update_data = document_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_document, field, value)
        
        db.commit()
        db.refresh(db_document)
        return db_document
    
    @staticmethod
    def delete_document(
        db: Session,
        document_id: int,
        designation: str
    ) -> bool:
        """Delete a document"""
        if not ComplianceService.check_upload_permission(designation):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only HR Manager or HR Executive can delete documents"
            )
        
        db_document = ComplianceService.get_document(db, document_id)
        if not db_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        db.delete(db_document)
        db.commit()
        return True
