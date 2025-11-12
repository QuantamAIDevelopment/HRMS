# HRMS Backend

A FastAPI-based Human Resource Management System backend.

## Project Structure

```
hrms-backend/
├── src/                                      
│   ├── main.py                               # FastAPI app entrypoint
│   │
│   ├── core/                                 # security & core utilities
│   │   ├── __init__.py
│   │   ├── security.py                       # password hashing, JWT helpers
│   │   └── logging_config.py                 # structured logging setup
│   │
│   ├── config/                               # environment & application config
│   │   ├── __init__.py
│   │   ├── settings.py                       # Pydantic BaseSettings / .env loader
│   │   └── constants.py                      # constants, env variable keys
│   │
│   ├── models/                               # ORM layer
│   │   ├── __init__.py
│   │   ├── base.py                           # SQLAlchemy Base / SQLModel metadata
│   │   ├── session.py                        # database engine & session
│   │   ├── user.py                           # user table model
│   │   ├── role.py                           # role / permission models
│   │   ├── crud.py                           # repository / CRUD functions
│   │   └── migrations/                       # Alembic migrations
│   │       ├── env.py
│   │       ├── versions/
│   │       └── README.md
│   │
│   ├── api/                                  # FastAPI routers
│   │   ├── __init__.py
│   │   ├── deps.py                           # dependencies (db, current_user, etc.)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py                       # login, register, refresh tokens
│   │       └── users.py                      # CRUD for users
│   │
│   ├── schemas/                              # Pydantic models (request/response)
│   │   ├── __init__.py
│   │   ├── auth.py                           # login/register schemas
│   │   └── user.py                           # user schemas (base, create, read)
│   │
│   ├── services/                             # domain logic layer
│   │   ├── __init__.py
│   │   ├── email_service.py                  # email (welcome, reset, payslip)
│   │   └── token_service.py                  # access/refresh token generation
│   │
│   └── scripts/                              # helper utilities / one-off scripts
│       ├── __init__.py
│       ├── db_migrate.py                     # alembic wrapper
│       └── seed_data.py                      # seed admin user / roles
│
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   └── test_users.py
│
├── alembic.ini                               # Alembic main config
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.sample
└── README.md
```

## Setup

1. Copy `.env.sample` to `.env` and configure your environment variables
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python -m src.scripts.db_migrate`
4. Start the server: `uvicorn src.main:app --reload`

## Docker

```bash
docker-compose up --build
```