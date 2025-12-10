# HRMS Testing Guide

## 🚀 Quick Start

### 1. Setup Database with Dummy Data
```bash
# Install dependencies
pip install faker

# Run dummy data generator
python run_dummy_data.py
```

### 2. Start the Server
```bash
python src/main.py
```

### 3. Import Postman Collection
- Import `HRMS_Postman_Collection.json` into Postman
- Set environment variables:
  - `base_url`: http://localhost:8000/api/v1
  - `access_token`: (will be set after login)
  - `employee_id`: EMP001

## 🔑 Test Credentials

| Role | Email | Password | Employee ID |
|------|-------|----------|-------------|
| HR Manager | john.manager@company.com | password123 | EMP001 |
| HR Executive | sarah.executive@company.com | password123 | EMP002 |
| Team Lead | mike.teamlead@company.com | password123 | EMP003 |
| Finance Manager | lisa.manager@company.com | password123 | EMP004 |

## 📊 Generated Test Data

### Core Data
- **50 Employees** across 8 departments
- **4 Shift Types** (Day, Night, Flexible, Weekend)
- **8 Job Titles** with salary ranges
- **User accounts** for first 10 employees

### Transactional Data
- **Attendance records** for last 30 days
- **Leave applications** (2-5 per employee)
- **Salary structures** with components
- **Expense records** across categories
- **Time entries** for last 15 days
- **Asset assignments** (100 assets)
- **Compliance documents** (20 documents)
- **Events & holidays** (30 events)

## 🧪 API Testing Workflow

### 1. Authentication Flow
1. **Login** → Get access token
2. **Change Password** → Update credentials
3. **Forgot Password** → Reset flow
4. **Verify OTP** → Validate reset
5. **Reset Password** → Complete reset

### 2. Employee Management
1. **Get All Employees** → List with pagination
2. **Get Employee Details** → Individual profile
3. **Update Employee** → Modify details
4. **Search/Filter** → By department/name

### 3. Attendance Tracking
1. **Punch In** → Start work session
2. **Punch Out** → End work session
3. **Get Records** → View attendance history
4. **Get Breakdown** → Detailed analytics

### 4. Leave Management
1. **Apply Leave** → Submit request
2. **Get History** → View past leaves
3. **Get Balance** → Check available leaves
4. **Approve/Reject** → Manager actions

### 5. Salary Management
1. **Create Structure** → Setup salary components
2. **Save Structure** → Store configuration
3. **Get Payslip** → View salary details
4. **Get History** → Past salary records

### 6. Expense Management
1. **Create Expense** → Submit with receipt
2. **Get Expenses** → View all/employee specific
3. **Update Status** → Approve/reject
4. **Get Summary** → Status overview

### 7. Timesheet Management
1. **Create Entry** → Log work hours
2. **Edit Entry** → Modify existing
3. **Update Status** → Approval workflow
4. **Get Analytics** → Summary cards

### 8. Asset Management
1. **Create Asset** → Add new asset
2. **Assign Asset** → Link to employee
3. **Return Asset** → Release assignment
4. **Get Summary** → Asset overview

## 🔍 Key Test Scenarios

### Authentication
- ✅ Valid login with correct credentials
- ❌ Invalid login with wrong credentials
- ✅ Password change with current password
- ❌ Password change with wrong current password
- ✅ Forgot password flow completion

### Authorization
- ✅ HR Manager can access all endpoints
- ✅ HR Executive can access most endpoints
- ❌ Regular employee cannot access admin endpoints
- ✅ Manager can approve subordinate leaves

### Data Validation
- ❌ Invalid email format in employee update
- ❌ Future joining date in employee creation
- ❌ Negative salary amounts
- ❌ Invalid leave date ranges
- ✅ Proper expense categories

### Business Logic
- ✅ Leave balance calculation
- ✅ Attendance work hours calculation
- ✅ Salary component calculations
- ✅ Asset assignment tracking
- ✅ Timesheet approval workflow

## 📈 Performance Testing

### Load Testing Endpoints
- `GET /employees` - List performance with 50 employees
- `GET /attendance` - Monthly attendance data
- `GET /expenses` - Expense history
- `POST /timesheets` - Bulk timesheet creation

### Database Queries
- Employee search with filters
- Attendance aggregation queries
- Leave balance calculations
- Salary component summations

## 🐛 Common Issues & Solutions

### Database Connection
```bash
# Check PostgreSQL status
pg_ctl status

# Restart if needed
pg_ctl restart
```

### Migration Issues
```bash
# Run migrations
alembic upgrade head

# Check migration status
alembic current
```

### Import Errors
```bash
# Install missing dependencies
pip install -r requirements.txt

# Check Python path
export PYTHONPATH="${PYTHONPATH}:./src"
```

## 📝 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔧 Environment Variables

Required in `.env` file:
```env
DATABASE_URL=postgresql://postgres:password@localhost/HRMS--BACKEND
SECRET_KEY=your-secret-key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 📊 Test Coverage Areas

### Functional Testing
- ✅ All CRUD operations
- ✅ Authentication & authorization
- ✅ Business rule validation
- ✅ Error handling
- ✅ Data relationships

### Integration Testing
- ✅ Database operations
- ✅ Email notifications
- ✅ File uploads
- ✅ API response formats
- ✅ Cross-module interactions

### Security Testing
- ✅ JWT token validation
- ✅ Password hashing
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ CORS configuration