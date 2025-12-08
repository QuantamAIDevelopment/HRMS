# HRMS Backend

A comprehensive FastAPI-based Human Resource Management System backend with complete employee lifecycle management, attendance tracking, compliance, and dashboard analytics.

## Features

### Core HR Management
- **Employee Management**: Complete CRUD operations for employee profiles, departments, and job titles
- **Attendance Tracking**: Punch in/out system with timesheet management and approvals
- **Shift Management**: Flexible shift scheduling and assignment
- **Leave Management**: Leave request and approval workflow

### Compliance & Policy
- **Compliance Documents**: Upload, manage, and track compliance documentation
- **Standard Policies**: Define and manage company-wide HR policies
- **Off-boarding**: Structured employee exit process management

### Analytics & Reporting
- **Unified Dashboard**: Real-time HR metrics and KPIs
- **Employee Analytics**: Growth tracking and department-wise statistics
- **Attendance Reports**: Comprehensive attendance and timesheet analytics

### Additional Features
- **Events & Holidays**: Company calendar management
- **Profile Management**: Employee self-service profile updates
- **Approval Workflows**: Multi-level approval system for various HR processes

## Project Structure

```
HRMS/
├── src/
│   ├── main.py                               # FastAPI application entry point
│   │
│   ├── core/                                 # Core utilities
│   │   ├── security.py                       # Password hashing, authentication stubs
│   │   └── logging_config.py                 # Structured logging configuration
│   │
│   ├── config/                               # Configuration management
│   │   ├── settings.py                       # Pydantic settings from environment
│   │   └── constants.py                      # Application constants
│   │
│   ├── models/                               # Database models (SQLAlchemy)
│   │   ├── base.py                           # Base model class
│   │   ├── session.py                        # Database session management
│   │   ├── hrms_models.py                    # Core HR models (Employee, Department, etc.)
│   │   ├── employee_profile.py               # Employee profile model
│   │   ├── job_title.py                      # Job title model
│   │   ├── shift.py                          # Shift management model
│   │   ├── timesheet.py                      # Timesheet model
│   │   ├── policy.py                         # Policy model
│   │   ├── compliance_document.py            # Compliance document model
│   │   ├── events_holidays.py                # Events and holidays model
│   │   ├── off_boarding.py                   # Off-boarding model
│   │   └── migrations/                       # Alembic database migrations
│   │       ├── env.py
│   │       ├── script.py.mako
│   │       └── versions/
│   │
│   ├── schemas/                              # Pydantic schemas (request/response)
│   │   ├── employee.py                       # Employee schemas
│   │   ├── attendance.py                     # Attendance schemas
│   │   ├── timesheet.py                      # Timesheet schemas
│   │   ├── timesheet_status.py               # Timesheet status schemas
│   │   ├── job_title.py                      # Job title schemas
│   │   ├── shift.py                          # Shift schemas
│   │   ├── policy.py                         # Policy schemas
│   │   ├── compliance_document.py            # Compliance document schemas
│   │   ├── events_holidays.py                # Events and holidays schemas
│   │   ├── off_boarding.py                   # Off-boarding schemas
│   │   ├── profile.py                        # Profile schemas
│   │   └── dashboard.py                      # Dashboard schemas
│   │
│   ├── api/v1/                               # API endpoints (version 1)
│   │   ├── employees.py                      # Employee CRUD endpoints
│   │   ├── employee.py                       # Additional employee endpoints
│   │   ├── departments.py                    # Department management
│   │   ├── job_titles.py                     # Job title management
│   │   ├── attendance.py                     # Attendance tracking
│   │   ├── punch.py                          # Punch in/out endpoints
│   │   ├── timesheet.py                      # Timesheet management
│   │   ├── shifts.py                         # Shift scheduling
│   │   ├── standard_policy.py                # Policy management
│   │   ├── compliance.py                     # Compliance document management
│   │   ├── events_holidays.py                # Events and holidays
│   │   ├── off_boarding.py                   # Off-boarding process
│   │   ├── profile.py                        # Employee profile management
│   │   ├── approval.py                       # Approval workflows
│   │   └── unified_dashboard.py              # Dashboard analytics
│   │
│   ├── services/                             # Business logic layer
│   │   ├── employee_service.py               # Employee business logic
│   │   ├── shift_service.py                  # Shift management logic
│   │   ├── policy_service.py                 # Policy management logic
│   │   ├── compliance_service.py             # Compliance logic
│   │   └── dashboard_service.py              # Dashboard analytics logic
│   │
│   ├── utils/                                # Utility functions
│   │   └── file_handler.py                   # File upload/download utilities
│   │
│   └── scripts/                              # Database and utility scripts
│       ├── db_migrate.py                     # Run Alembic migrations
│       ├── create_migration.py               # Create new migrations
│       └── clean_database.py                 # Database cleanup utility
│
├── tests/                                    # Test suite
│   ├── conftest.py                           # Pytest configuration
│   └── test_employees.py                     # Employee endpoint tests
│
├── alembic.ini                               # Alembic configuration
├── Dockerfile                                # Docker container definition
├── docker-compose.yml                        # Docker Compose orchestration
├── requirements.txt                          # Python dependencies
├── .env.sample                               # Environment variables template
├── .gitignore                                # Git ignore rules
├── hrms_schema.sql                           # Database schema SQL
├── API_ENDPOINTS.md                          # API documentation
└── README.md                                 # This file
```

## Technology Stack

- **Framework**: FastAPI 0.100+
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Authentication**: JWT (python-jose), Passlib (bcrypt)
- **Testing**: Pytest, Factory Boy
- **Code Quality**: Black, isort, Flake8, Ruff
- **Server**: Uvicorn (ASGI)

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- pip or poetry for dependency management

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd HRMS
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.sample .env
```

Edit `.env` with your configuration:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/hrms_db
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
```

### 5. Setup Database

#### Create Database
```bash
psql -U postgres
CREATE DATABASE hrms_db;
\q
```

#### Run Migrations
```bash
python -m src.scripts.db_migrate
```

### 6. Start the Server

#### Development Mode
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Production Mode
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Using Python directly
```bash
python -m src.main
```

## Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Docker Only
```bash
# Build image
docker build -t hrms-backend .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/hrms_db \
  -e SECRET_KEY=your-secret-key \
  hrms-backend
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

For detailed endpoint documentation, see [API_ENDPOINTS.md](API_ENDPOINTS.md)

## Key API Endpoints

### Health Check
```
GET /health
GET /
```

### Employee Management
```
GET    /api/v1/employees              # List all employees
POST   /api/v1/employees              # Create employee
GET    /api/v1/employees/{id}         # Get employee details
PUT    /api/v1/employees/{id}         # Update employee
DELETE /api/v1/employees/{id}         # Delete employee
```

### Attendance & Timesheet
```
GET    /api/v1/attendance_tracking    # Get attendance records
POST   /api/v1/punch                  # Punch in/out
GET    /api/v1/timesheets              # List timesheets
POST   /api/v1/timesheets              # Submit timesheet
```

### Dashboard
```
GET    /api/v1/dashboard/summary      # Dashboard metrics
GET    /api/v1/dashboard/analytics    # Analytics data
```

### Compliance & Policy
```
GET    /api/v1/compliance             # List compliance documents
POST   /api/v1/compliance             # Upload document
GET    /api/v1/policies               # List policies
```

## Database Migrations

### Create New Migration
```bash
python -m src.scripts.create_migration "description of changes"
```

### Run Migrations
```bash
python -m src.scripts.db_migrate
```

### Alembic Commands
```bash
# Check current version
alembic current

# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# View migration history
alembic history
```

## Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_employees.py -v
```

## Code Quality

### Format Code
```bash
black src/
isort src/
```

### Lint Code
```bash
flake8 src/
ruff check src/
```

## Project Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | 30 |
| `DEBUG` | Enable debug mode | False |

### CORS Configuration

CORS is configured in `src/main.py`. For production, update the `allow_origins` list:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Security Features

- Password hashing using bcrypt
- JWT-based authentication (stub implementation)
- Role-based access control (HR Manager, HR Executive)
- SQL injection prevention via SQLAlchemy ORM
- Request validation using Pydantic
- CORS protection

## Logging

Logs are configured in `src/core/logging_config.py`:

- **Development**: Console output only (DEBUG level)
- **Production**: Console + file output (`logs/hrms.log`, INFO level)

Log format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Troubleshooting

### Database Connection Issues
```bash
# Test PostgreSQL connection
psql -U postgres -h localhost -p 5432

# Check if database exists
psql -U postgres -l | grep hrms_db
```

### Migration Errors
```bash
# Reset migrations (WARNING: drops all data)
python -m src.scripts.clean_database
alembic stamp head
```

### Import Errors
```bash
# Ensure you're in the project root and virtual environment is activated
python -c "import src.main"
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

Proprietary - All rights reserved

## Support

For issues and questions, please contact the development team.