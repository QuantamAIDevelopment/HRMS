# HRMS Backend API

## Overview
HRMS (Human Resource Management System) Backend API built with FastAPI, providing comprehensive leave management, asset management, and attendance tracking.

## Folder Structure

```
HRMS/src/
├── api/v1/                    # API Routes
│   ├── leave.py              # Leave management routes (Employee, Manager, HR Executive)
│   ├── asset.py              # Asset management routes
│   ├── attendance.py         # Attendance/punch in-out routes
│   └── __init__.py           # Router exports
├── models/                    # Database Models
│   ├── base.py               # SQLAlchemy Base
│   ├── employee.py           # Employee model
│   ├── leave.py              # Leave and balance models
│   ├── asset.py              # Asset model
│   ├── attendance.py         # Attendance model
│   ├── session.py            # Database session & get_db()
│   └── __init__.py           # Model exports
├── schemas/                   # Pydantic Schemas
│   ├── leave.py              # Leave schemas for all roles
│   ├── asset.py              # Asset schemas
│   └── __init__.py
├── services/                  # Business Logic
│   ├── leave_service.py      # Leave services for all roles
│   ├── asset_service.py      # Asset service
│   └── __init__.py
├── config/                    # Configuration
│   └── settings.py           # Database URL, app settings
└── main.py                    # FastAPI app with all routers
```

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database in `.env` file or update `config/settings.py`

3. Run the application:
```bash
python main.py
```

4. Access Swagger UI:
```
http://localhost:8000/docs
```

## Database Configuration

Database settings in `config/settings.py`:
```python
database_url: str = "postgresql://postgres:password@127.0.0.1:5432/hrms_app"
```

## API Endpoints

### Leave Management
- POST /api/v1/leave/apply
- GET /api/v1/leave/history/{employee_id}
- GET /api/v1/leave/pending/{manager_id}
- PUT /api/v1/leave/approve/{leave_id}
- GET /api/v1/leave/balance/{employee_id}

### Manager Leave
- POST /api/v1/manager/apply-leave
- GET /api/v1/manager/history/{manager_id}
- GET /api/v1/manager/pending/{hr_executive_id}
- GET /api/v1/manager/balance/{manager_id}
- PUT /api/v1/manager/approve/{leave_id}

### HR Executive Leave
- POST /api/v1/hr-executive/apply-leave
- GET /api/v1/hr-executive/history/{hr_executive_id}
- GET /api/v1/hr-executive/pending/{hr_manager_id}
- GET /api/v1/hr-executive/balance/{hr_executive_id}
- PUT /api/v1/hr-executive/approve/{leave_id}

### Asset Management
- POST /api/v1/assets/ - Create asset
- GET /api/v1/assets/summary - Asset summary
- GET /api/v1/assets/history - Asset history
- PUT /api/v1/assets/edit/{asset_id} - Edit asset
- PUT /api/v1/assets/{asset_id}/return - Return asset
- DELETE /api/v1/assets/{asset_id} - Delete asset

### Attendance
- POST /api/v1/attendance/punch-in
- POST /api/v1/attendance/punch-out
- GET /api/v1/attendance/recent

## Database Tables

- `employees` - Employee information
- `leave_management` - Leave records
- `assets` - Asset information
- `attendance` - Attendance/punch records

## Key Features

- **Role-based Leave Management**: Different leave workflows for employees, managers, and HR executives
- **Asset Management**: Track and manage company assets
- **Attendance Tracking**: Punch in/out system with time tracking
- **RESTful API**: Clean API design with proper HTTP methods
- **Database Integration**: PostgreSQL with SQLAlchemy ORM
- **API Documentation**: Auto-generated Swagger/OpenAPI docs

## Recent Updates

- Removed team lead management endpoints
- Fixed database schema compatibility
- Added proper error handling for duplicate serial numbers
- Simplified server startup (now uses `python main.py`)
- Updated API documentation
