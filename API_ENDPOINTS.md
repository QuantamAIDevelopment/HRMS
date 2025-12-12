# HR Manager Dashboard API Endpoints

## Base URL: `http://localhost:8000/api/v1`

## 1. Dashboard Summary
- **GET** `/dashboard/summary`
- **Response:**
```json
{
  "total_employees": 128,
  "pending_leave_requests": 2,
  "employee_growth_percent": 2.4
}
```

## 2. Self Service APIs

### Dashboard
- **GET** `/self/dashboard`

### Punch In/Out
- **GET** `/self/punch`

### Timesheet
- **GET** `/self/timesheet`

### Leave Management
- **GET** `/self/leave`

### Profile
- **GET** `/self/profile`

### Payslip
- **GET** `/self/payslip`

### Expense
- **GET** `/self/expense`

**Sample Response for Self Service:**
```json
{
  "title": "Timesheet",
  "description": "Employee timesheet management",
  "count": 8
}
```

## 3. Admin Core APIs

### Employee Management
- **GET** `/admin/employees`
- **Response:**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "department": "Engineering",
    "position": "Software Engineer"
  }
]
```

### Access Requests
- **GET** `/admin/access-requests`

### Payroll Setup
- **GET** `/admin/payroll/setup`

### Timesheet Approvals
- **GET** `/admin/timesheet/approvals`

### Leave Approvals
- **GET** `/admin/leave/approvals`

## 4. Admin Extended APIs

### Asset Management
- **GET** `/admin/asset-management`

### Expense Approval
- **GET** `/admin/expense-approval`

### Events & Holidays
- **GET** `/admin/events-holidays`

### Onboarding
- **GET** `/admin/onboarding`

### Offboarding
- **GET** `/admin/offboarding`

### Job Titles
- **GET** `/admin/job-titles`

### Shift Scheduling
- **GET** `/admin/shift-scheduling`

### Attendance Policy
- **GET** `/admin/attendance-policy`

### Compliance Documents
- **GET** `/admin/compliance-documents`

**Sample Response for Admin APIs:**
```json
{
  "title": "Asset Management",
  "description": "Company assets and equipment tracking",
  "count": 45
}
```

## Running the Server

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python run_server.py
```

3. Access API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## CORS Configuration
The API includes CORS middleware to allow frontend integration from any origin.