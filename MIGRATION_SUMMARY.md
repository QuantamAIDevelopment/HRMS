# HRMS Code Migration Summary

## Overview
All backend code has been successfully reorganized into the existing `HRMS/src/` folder structure.

## Folder Structure

```
HRMS/src/
├── api/v1/                    # API Routes
│   ├── leave.py              # All leave management routes (Employee, Manager, Team Lead, HR Executive)
│   ├── asset.py              # Asset management routes
│   ├── attendance.py         # Attendance/punch in-out routes
│   └── __init__.py           # Router exports
├── models/                    # Database Models
│   ├── base.py               # SQLAlchemy Base
│   ├── employee.py           # Employee model
│   ├── leave.py              # Leave, EmployeeBalance, ManagerBalance, TeamLeadBalance, HRExecutiveBalance
│   ├── asset.py              # Asset model
│   ├── attendance.py         # Attendance model
│   ├── session.py            # Database session & get_db()
│   └── __init__.py           # Model exports
├── schemas/                   # Pydantic Schemas
│   ├── leave.py              # All leave schemas (Employee, Manager, Team Lead, HR Executive)
│   ├── asset.py              # Asset schemas
│   └── __init__.py
├── services/                  # Business Logic
│   ├── leave_service.py      # LeaveService, ManagerService, TeamLeadService, HRExecutiveService
│   ├── asset_service.py      # AssetService
│   └── __init__.py
├── config/                    # Configuration
│   └── settings.py           # Database URL, app settings
└── main.py                    # FastAPI app with all routers

```

## What Was Done

### 1. Models Consolidated
- All models now use single `Base` from `models/base.py`
- Created unified models:
  - `models/employee.py` - Employee model
  - `models/leave.py` - Leave + all balance models (Employee, Manager, TeamLead, HRExecutive)
  - `models/asset.py` - Asset model
  - `models/attendance.py` - Attendance model
  - `models/session.py` - Database session configuration

### 2. Schemas Organized
- `schemas/leave.py` - All leave-related schemas for all roles
- `schemas/asset.py` - Asset schemas

### 3. Services Consolidated
- `services/leave_service.py` - Contains:
  - LeaveService (Employee leaves)
  - ManagerService (Manager leaves)
  - TeamLeadService (Team Lead leaves)
  - HRExecutiveService (HR Executive leaves)
- `services/asset_service.py` - Asset business logic

### 4. API Routes Organized
- `api/v1/leave.py` - All leave endpoints for all roles
- `api/v1/asset.py` - All asset endpoints
- `api/v1/attendance.py` - All attendance endpoints

### 5. Main Application
- `main.py` updated to:
  - Import all routers
  - Setup CORS middleware
  - Create database tables on startup
  - Include all routes with `/api/v1` prefix

## Database Configuration

Database settings in `config/settings.py`:
```python
database_url: str = "postgresql://postgres:bhavani%40123@127.0.0.1:5432/hrms_app"
```

## How to Run

1. Navigate to HRMS folder:
```bash
cd c:\Users\Admin\OneDrive - QAID\Documents\Desktop\hrms2\HRMS\src\HRMS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or use the batch file:
```bash
run.bat
```

4. Access Swagger UI:
```
http://localhost:8000/docs
```

## API Endpoints

All endpoints are now under `/api/v1` prefix:

### Employee Leave Management
- POST `/api/v1/leave/apply`
- GET `/api/v1/leave/history/{employee_id}`
- GET `/api/v1/leave/pending/{manager_id}`
- PUT `/api/v1/leave/approve/{leave_id}`
- GET `/api/v1/leave/balance/{employee_id}`

### Manager Leave Management
- POST `/api/v1/manager/apply-leave`
- GET `/api/v1/manager/history/{manager_id}`
- GET `/api/v1/manager/pending/{hr_executive_id}`
- GET `/api/v1/manager/balance/{manager_id}`
- PUT `/api/v1/manager/approve/{leave_id}`

### Team Lead Leave Management
- POST `/api/v1/team-lead/apply-leave`
- GET `/api/v1/team-lead/leave-history/{team_lead_id}`
- GET `/api/v1/team-lead/pending/{manager_id}`
- GET `/api/v1/team-lead/balance/{team_lead_id}`
- PUT `/api/v1/team-lead/approve/{leave_id}`

### HR Executive Leave Management
- POST `/api/v1/hr-executive/apply-leave`
- GET `/api/v1/hr-executive/history/{hr_executive_id}`
- GET `/api/v1/hr-executive/pending/{hr_manager_id}`
- GET `/api/v1/hr-executive/balance/{hr_executive_id}`
- PUT `/api/v1/hr-executive/approve/{leave_id}`

### Asset Management
- POST `/api/v1/assets/`
- GET `/api/v1/assets/`
- GET `/api/v1/assets/summary`
- GET `/api/v1/assets/types`
- GET `/api/v1/assets/history`
- GET `/api/v1/assets/{serial_number}`
- PUT `/api/v1/assets/edit/{asset_id}`
- PUT `/api/v1/assets/{asset_id}/return`
- DELETE `/api/v1/assets/{asset_id}`

### Attendance Management
- POST `/api/v1/attendance/punch-in`
- POST `/api/v1/attendance/punch-out`
- GET `/api/v1/attendance/status`
- GET `/api/v1/attendance/recent`

## Key Changes

1. **Single Database Session**: All modules now use `models/session.py` for database connection
2. **Unified Base Model**: All models inherit from single `Base` in `models/base.py`
3. **Centralized Configuration**: Database URL and settings in `config/settings.py`
4. **Organized Routes**: All routes properly organized under `/api/v1` prefix
5. **No Duplicate Code**: Services consolidated to avoid duplication

## Database Tables Used

- `employees` - Employee information
- `leave_management` - All leave records (Employee, Manager, Team Lead, HR Executive)
- `employee_balances` - Employee leave balances
- `manager_balances` - Manager leave balances
- `team_lead_balances` - Team Lead leave balances
- `hr_executive_balances` - HR Executive leave balances
- `assets` - Asset information
- `attendance` - Attendance/punch records

## Notes

- All existing folder structure preserved
- No new folders created
- Code properly fitted into existing HRMS folder
- All imports updated to work with new structure
- FastAPI/Swagger will load without errors
- Database connection configured for PostgreSQL
