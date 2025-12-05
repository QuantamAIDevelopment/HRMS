# HRMS Backend

A FastAPI-based Human Resource Management System backend with Policies Setup module.

## Features

- **Policies Setup**: Complete attendance policy management system
- **PostgreSQL**: Production-ready database
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: Powerful ORM with Alembic migrations
- **Pydantic**: Data validation and serialization
- **Docker**: Containerized deployment

## Policies Setup Module

The Policies Setup module provides comprehensive attendance policy management with the following features:

### Data Models
- **Policy**: Main policy configuration (working hours, days, activation status)
- **PolicyTiming**: Grace periods, late marking, half-day rules
- **PolicyOvertime**: Overtime settings and multipliers
- **PolicyTracking**: Check-in/out requirements

### API Endpoints
- `GET /api/policies` - List all policies
- `GET /api/policies/{id}` - Get policy details with nested configuration
- `POST /api/policies` - Create new policy
- `PUT /api/policies/{id}` - Update entire policy
- `PATCH /api/policies/{id}/activate` - Activate policy (deactivates others)
- `PATCH /api/policies/{id}/overtime` - Update overtime settings
- `PATCH /api/policies/{id}/tracking` - Update tracking settings
- `DELETE /api/policies/{id}` - Delete policy

### Validation Rules
- Policy names must be unique
- Working hours: 0-24 hours per day
- Working days: 1-7 days per week
- Half-day hours must be less than working hours per day
- Overtime multipliers must be > 1.0 when enabled
- Only one policy can be active at a time

## Project Structure

```
hrms-backend/
├── src/
│   ├── main.py                               # FastAPI app with policies router
│   ├── api/
│   │   ├── policies/
│   │   │   └── router.py                     # Policies API endpoints
│   │   └── v1/                               # Other API versions
│   ├── models/
│   │   ├── policy.py                         # Policy database models
│   │   ├── base.py                           # SQLAlchemy base
│   │   └── migrations/                       # Alembic migrations
│   ├── schemas/
│   │   └── policy.py                         # Pydantic schemas
│   ├── services/
│   │   └── policies_service.py               # Business logic
│   └── config/
│       └── settings.py                       # PostgreSQL configuration
├── tests/
│   └── test_policies.py                      # Comprehensive test suite
├── docker-compose.yml                        # PostgreSQL + FastAPI services
└── requirements.txt                          # Dependencies with psycopg2
```

## Setup

### Local Development

1. **Environment Setup**
   ```bash
   cp .env.sample .env
   # Edit .env with your PostgreSQL credentials
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**
   ```bash
   # Start PostgreSQL (or use Docker)
   docker run -d --name postgres -e POSTGRES_DB=hrms_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15
   
   # Run migrations
   alembic upgrade head
   ```

4. **Start Server**
   ```bash
   uvicorn src.main:app --reload
   ```

### Docker Deployment

```bash
docker-compose up --build
```

This will start:
- PostgreSQL database on port 5432
- FastAPI application on port 8000

## Testing

```bash
# Run all tests
pytest

# Run policies tests specifically
pytest tests/test_policies.py -v

# Run with coverage
pytest --cov=src tests/
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Example Usage

### Create a Policy

```bash
curl -X POST "http://localhost:8000/api/policies/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Standard Policy",
       "description": "Default attendance policy",
       "working_hours_per_day": 9,
       "working_days_per_week": 5,
       "timing": {
         "grace_period_minutes": 15,
         "mark_late_after_minutes": 15,
         "half_day_hours": 4.5,
         "auto_deduct_for_absence": true
       },
       "overtime": {
         "overtime_enabled": true,
         "overtime_multiplier_weekdays": 1.5,
         "overtime_multiplier_weekend": 2.0
       },
       "tracking": {
         "require_check_in": true,
         "require_check_out": true
       }
     }'
```

### Activate a Policy

```bash
curl -X PATCH "http://localhost:8000/api/policies/{policy_id}/activate"
```