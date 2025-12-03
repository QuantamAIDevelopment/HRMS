from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
import io
from ...models.session import get_db
from ...models.hrms_models import ComplianceDocument
from ...schemas.compliance_document import (
    ComplianceDocumentCreate,
    ComplianceDocumentUpdate,
    ComplianceDocumentResponse,
    ComplianceDocumentDownload
)
from ...services.compliance_service import ComplianceService

router = APIRouter(prefix="/compliance", tags=["Compliance Documents"])

# Temporary dependency - replace with actual auth
def get_current_employee():
    """Replace this with actual authentication logic"""
    return {
        "employee_id": "EMP001",
        "designation": "HR Manager"  # Change to test different roles
    }

@router.post("/documents", response_model=ComplianceDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    title: str = Form(...),
    category: str = Form(...),
    description: Optional[str] = Form(None),
    uploaded_by: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_employee: dict = Depends(get_current_employee)
):
    """Upload a new compliance document (HR Manager/Executive only)"""
    file_content = await file.read()
    base64_content = base64.b64encode(file_content).decode('utf-8')
    
    document = ComplianceDocumentCreate(
        title=title,
        category=category.capitalize(),
        description=description,
        uploaded_document=base64_content
    )
    
    return ComplianceService.create_document(
        db=db,
        document=document,
        employee_id=uploaded_by,
        designation=current_employee["designation"]
    )

@router.get("/documents", response_model=List[ComplianceDocumentResponse])
def get_all_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_employee: dict = Depends(get_current_employee)
):
    """Get all compliance documents (All users can view)"""
    return ComplianceService.get_all_documents(
        db=db,
        skip=skip,
        limit=limit,
        category=category
    )

@router.get("/documents/title/{title}", response_model=ComplianceDocumentDownload)
def get_document_by_title(
    title: str,
    db: Session = Depends(get_db),
    current_employee: dict = Depends(get_current_employee)
):
    """Get document details by title (All users)"""
    document = db.query(ComplianceDocument).filter(
        ComplianceDocument.title == title
    ).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document

@router.get("/documents/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_employee: dict = Depends(get_current_employee)
):
    """Download document file (All users)"""
    document = ComplianceService.get_document(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    file_data = base64.b64decode(document.uploaded_document)
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={document.title}.pdf"}
    )

@router.put("/documents/{document_id}", response_model=ComplianceDocumentResponse)
async def update_document(
    document_id: int,
    title: str = Form(...),
    category: str = Form(...),
    description: Optional[str] = Form(None),
    uploaded_by: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_employee: dict = Depends(get_current_employee)
):
    """Update a compliance document (HR Manager/Executive only)"""
    file_content = await file.read()
    base64_content = base64.b64encode(file_content).decode('utf-8')
    
    document_update = ComplianceDocumentUpdate(
        title=title,
        category=category.capitalize(),
        description=description,
        uploaded_document=base64_content
    )
    
    return ComplianceService.update_document(
        db=db,
        document_id=document_id,
        document_update=document_update,
        designation=current_employee["designation"]
    )

@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_employee: dict = Depends(get_current_employee)
):
    """Delete a compliance document (HR Manager/Executive only)"""
    ComplianceService.delete_document(
        db=db,
        document_id=document_id,
        designation=current_employee["designation"]
    )
    return None
