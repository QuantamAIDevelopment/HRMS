# HRMS Backend API

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database in `.env` file

3. Run the application:
```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. Access Swagger UI:
```
http://localhost:8000/docs
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

### Team Lead Leave
- POST /api/v1/team-lead/apply-leave
- GET /api/v1/team-lead/leave-history/{team_lead_id}
- GET /api/v1/team-lead/pending/{manager_id}
- GET /api/v1/team-lead/balance/{team_lead_id}
- PUT /api/v1/team-lead/approve/{leave_id}

### HR Executive Leave
- POST /api/v1/hr-executive/apply-leave
- GET /api/v1/hr-executive/history/{hr_executive_id}
- GET /api/v1/hr-executive/pending/{hr_manager_id}
- GET /api/v1/hr-executive/balance/{hr_executive_id}
- PUT /api/v1/hr-executive/approve/{leave_id}

### Asset Management
- POST /api/v1/assets/
- GET /api/v1/assets/
- GET /api/v1/assets/summary
- GET /api/v1/assets/types
- GET /api/v1/assets/history
- GET /api/v1/assets/{serial_number}
- PUT /api/v1/assets/edit/{asset_id}
- PUT /api/v1/assets/{asset_id}/return
- DELETE /api/v1/assets/{asset_id}

### Attendance
- POST /api/v1/attendance/punch-in
- POST /api/v1/attendance/punch-out
- GET /api/v1/attendance/status
- GET /api/v1/attendance/recent
