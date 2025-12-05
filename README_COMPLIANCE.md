# Compliance Documents and Policy Management Module

## Overview
This module handles compliance documents and policy management with role-based access control.

## Features
- ✅ Upload documents as base64 encoded strings
- ✅ Store documents in PostgreSQL database
- ✅ Role-based access control (HR Manager/Executive can upload, all users can download)
- ✅ Document categorization (Policy, Compliance, Legal, Training)
- ✅ Full CRUD operations

## Database Schema
```sql
CREATE TABLE compliance_documents_and_policy_management (
    document_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(50) CHECK (category IN ('Policy','Compliance','Legal','Training')) NOT NULL,
    description TEXT,
    uploaded_document TEXT,
    uploaded_by VARCHAR(50) NOT NULL,
    uploaded_on TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (uploaded_by) REFERENCES employees(employee_id)
);
```

## API Endpoints

### 1. Upload Document (HR Manager/Executive Only)
```http
POST /api/v1/compliance/documents
Content-Type: application/json

{
  "title": "Employee Handbook",
  "category": "Policy",
  "description": "Company employee handbook 2024",
  "uploaded_document": "base64_encoded_string_here"
}
```

**Response:** `201 Created`
```json
{
  "document_id": 1,
  "title": "Employee Handbook",
  "category": "Policy",
  "description": "Company employee handbook 2024",
  "uploaded_by": "EMP001",
  "uploaded_on": "2024-01-15T10:30:00",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### 2. List All Documents (All Users)
```http
GET /api/v1/compliance/documents?skip=0&limit=100&category=Policy
```

**Response:** `200 OK`
```json
[
  {
    "document_id": 1,
    "title": "Employee Handbook",
    "category": "Policy",
    "description": "Company employee handbook 2024",
    "uploaded_by": "EMP001",
    "uploaded_on": "2024-01-15T10:30:00",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
]
```

### 3. Download Document (All Users)
```http
GET /api/v1/compliance/documents/{document_id}
```

**Response:** `200 OK`
```json
{
  "document_id": 1,
  "title": "Employee Handbook",
  "category": "Policy",
  "description": "Company employee handbook 2024",
  "uploaded_document": "base64_encoded_string_here",
  "uploaded_by": "EMP001",
  "uploaded_on": "2024-01-15T10:30:00",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### 4. Update Document (HR Manager/Executive Only)
```http
PUT /api/v1/compliance/documents/{document_id}
Content-Type: application/json

{
  "title": "Updated Employee Handbook",
  "description": "Updated for 2024"
}
```

### 5. Delete Document (HR Manager/Executive Only)
```http
DELETE /api/v1/compliance/documents/{document_id}
```

**Response:** `204 No Content`

## Role-Based Access Control

| Role | Upload | Download | Update | Delete |
|------|--------|----------|--------|--------|
| HR Manager | ✅ | ✅ | ✅ | ✅ |
| HR Executive | ✅ | ✅ | ✅ | ✅ |
| Other Users | ❌ | ✅ | ❌ | ❌ |

## File Structure
```
HRMS/src/
├── models/
│   └── compliance_document.py       # SQLAlchemy model
├── schemas/
│   └── compliance_document.py       # Pydantic schemas
├── services/
│   └── compliance_service.py        # Business logic
├── api/v1/
│   └── compliance.py                # API endpoints
└── utils/
    └── file_handler.py              # Base64 utilities
```

## Usage Example

### Python Client
```python
import requests
import base64

# Encode file to base64
with open('document.pdf', 'rb') as f:
    base64_content = base64.b64encode(f.read()).decode('utf-8')

# Upload document
response = requests.post(
    'http://localhost:8000/api/v1/compliance/documents',
    json={
        'title': 'Safety Policy',
        'category': 'Policy',
        'description': 'Workplace safety guidelines',
        'uploaded_document': base64_content
    }
)

# Download document
doc = requests.get('http://localhost:8000/api/v1/compliance/documents/1').json()
file_data = base64.b64decode(doc['uploaded_document'])
with open('downloaded.pdf', 'wb') as f:
    f.write(file_data)
```

## Error Responses

### 403 Forbidden (Insufficient Permissions)
```json
{
  "detail": "Only HR Manager or HR Executive can upload documents"
}
```

### 404 Not Found
```json
{
  "detail": "Document not found"
}
```

## Setup Instructions

1. Run database migration to create the table
2. Update `get_current_employee()` in `compliance.py` with actual authentication
3. Start the FastAPI server: `uvicorn src.main:app --reload`
4. Access API docs: `http://localhost:8000/docs`

## Notes
- Documents are stored as base64 encoded TEXT in PostgreSQL
- Maximum recommended file size: 10MB
- Supported categories: Policy, Compliance, Legal, Training
- All timestamps are in UTC
