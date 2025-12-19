# HRMS Backend - Human Resource Management System

## 🚀 Production-Ready AKS Deployment

This is a FastAPI-based HRMS backend system optimized for deployment on Azure Kubernetes Service (AKS) with comprehensive environment variable management and security best practices.

---

## ✅ Deployment Status

**Security Audit**: ✅ COMPLETE  
**AKS Ready**: ✅ YES  
**Production Safe**: ✅ YES  

All critical security issues have been fixed. The application is ready for production deployment.

---

## 📋 Quick Start (5 Minutes)

### 1. Prerequisites
- Python 3.11+
- PostgreSQL database
- Docker & Docker Compose (optional, for containerized deployment)

### 2. Local Setup
```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp example.env .env
# Edit .env with your local settings
```

### 3. Run Locally
```bash
# With auto-reload
uvicorn src.main:app --reload

# Application available at http://localhost:8000
# API docs: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### 4. Docker Compose (Local with PostgreSQL)
```bash
docker-compose up -d
curl http://localhost:8000/health
```

---

## 🔐 Environment Variables Guide

### Required Variables (Must be set)

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `DATABASE_URL` | String | `postgresql://user:pass@host:5432/hrms_db` | PostgreSQL connection string |
| `SECRET_KEY` | String | `<32+ char random string>` | JWT signing key for authentication |

### Important Variables (Recommended for Production)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `FRONTEND_URL` | String | `http://localhost:3000` | Frontend application URL (used in email links) |
| `CORS_ORIGINS` | String | `http://localhost:3000` | Comma-separated allowed CORS origins |
| `DEBUG` | Boolean | `false` | Debug mode (NEVER true in production) |
| `DEV_MODE` | Boolean | `false` | Development mode (NEVER true in production) |

### Email Configuration (Optional)

| Variable | Type | Description |
|----------|------|-------------|
| `SMTP_SERVER` | String | SMTP server address (e.g., smtp.gmail.com) |
| `SMTP_PORT` | Integer | SMTP port (usually 587) |
| `SMTP_USERNAME` | String | SMTP authentication username |
| `SMTP_PASSWORD` | String | SMTP authentication password |
| `FROM_EMAIL` | String | Sender email address |

### Application Settings

| Variable | Type | Default |
|----------|------|---------|
| `ALGORITHM` | String | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Integer | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Integer | `7` |
| `RESET_TOKEN_EXPIRE_MINUTES` | Integer | `15` |
| `HOST` | String | `0.0.0.0` |
| `PORT` | Integer | `8000` |

---

## 📝 Generate Secret Key

```bash
# Generate a strong 32+ character secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Copy the output to SECRET_KEY in your environment
```

---

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t hrms-service:latest .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/hrms_db" \
  -e SECRET_KEY="your-secret-key" \
  -e FRONTEND_URL="https://your-domain.com" \
  hrms-service:latest
```

---

## ☸️ Kubernetes (AKS) Deployment

### Prerequisites
- AKS cluster running
- kubectl configured
- Docker image in container registry (ACR)

### 1. Create Secrets
```bash
kubectl create secret generic hrms-secrets \
  --from-literal=database-url="postgresql://user:pass@host:5432/hrms_db" \
  --from-literal=secret-key="your-secret-key" \
  --from-literal=smtp-server="smtp.gmail.com" \
  --from-literal=smtp-username="your-email@gmail.com" \
  --from-literal=smtp-password="your-app-password" \
  --from-literal=from-email="noreply@company.com" \
  --from-literal=db-username="postgres" \
  --from-literal=db-password="your-db-password"
```

### 2. Create ConfigMap
```bash
kubectl create configmap hrms-config \
  --from-literal=ALGORITHM=HS256 \
  --from-literal=ACCESS_TOKEN_EXPIRE_MINUTES=30 \
  --from-literal=REFRESH_TOKEN_EXPIRE_DAYS=7 \
  --from-literal=RESET_TOKEN_EXPIRE_MINUTES=15 \
  --from-literal=DEBUG=false \
  --from-literal=DEV_MODE=false \
  --from-literal=HOST=0.0.0.0 \
  --from-literal=PORT=8000 \
  --from-literal=FRONTEND_URL="https://your-domain.com" \
  --from-literal=CORS_ORIGINS="https://your-domain.com"
```

### 3. Deploy Application
```bash
# Apply manifests
kubectl apply -f manifests/deployment.yaml
kubectl apply -f manifests/service.yaml

# Verify deployment
kubectl get pods -l app=hrms-service
kubectl get svc hrms-service

# View logs
kubectl logs -f deployment/hrms-service
```

### 4. Check Health
```bash
# Port forward to local
kubectl port-forward svc/hrms-service 8000:8000

# Test in another terminal
curl http://localhost:8000/health
```

---

## 🔄 Azure Pipeline Deployment

### Setup Variable Groups

Create in Azure DevOps (Pipelines → Library):

**HRMS-PROD-SECRETS**:
```
DATABASE_URL = postgresql://user:pass@host:5432/hrms_db
SECRET_KEY = <generated-secret-key>
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 587
SMTP_USERNAME = your-email@gmail.com
SMTP_PASSWORD = your-app-password
FROM_EMAIL = noreply@company.com
DB_USERNAME = postgres
DB_PASSWORD = your-db-password
```

**HRMS-PROD-CONFIG**:
```
FRONTEND_URL = https://your-domain.com
CORS_ORIGINS = https://your-domain.com
DEBUG = false
DEV_MODE = false
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

### Deploy via Pipeline
```bash
# Manual trigger
az pipelines run --name "hrms-release"

# Or push to trigger automatically
git push origin main
```

---

## 📊 API Endpoints

Base URL: `http://localhost:8000/api/v1`

### Authentication
- `POST /auth/login` - User login
- `POST /auth/signup` - Create new user
- `POST /auth/refresh` - Refresh access token
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password

### Employees
- `GET /employees` - List all employees
- `POST /employees` - Create new employee
- `GET /employees/{id}` - Get employee details
- `PUT /employees/{id}` - Update employee
- `DELETE /employees/{id}` - Delete employee

### Salary
- `GET /salary/payroll` - Get payroll data
- `POST /salary/create` - Create salary structure
- `GET /salary/payslip/{employee_id}` - Get payslip

### Leave Management
- `GET /leave` - List leave records
- `POST /leave` - Request leave
- `PUT /leave/{id}` - Update leave status

### Attendance
- `POST /attendance/punch-in` - Clock in
- `POST /attendance/punch-out` - Clock out
- `GET /attendance/{employee_id}` - Get attendance records

### Expenses
- `POST /expenses` - Submit expense
- `GET /expenses/{employee_id}` - Get employee expenses
- `PUT /expenses/{id}/status` - Update expense status

See full API docs at `http://localhost:8000/docs`

---

## 🗂️ Project Structure

```
src/
├── api/
│   ├── v1/
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── employees.py         # Employee management
│   │   ├── salary.py            # Payroll management
│   │   ├── leave.py             # Leave management
│   │   ├── attendance.py        # Attendance tracking
│   │   ├── expenses.py          # Expense management
│   │   └── ...                  # Other endpoints
│   └── deps.py                  # Dependency injection
├── config/
│   ├── settings.py              # Environment configuration
│   ├── constants.py             # Application constants
│   └── logging_config.py        # Logging setup
├── core/
│   ├── database.py              # Database initialization
│   ├── security.py              # Authentication & encryption
│   └── deps.py                  # Core dependencies
├── models/
│   ├── Employee_models.py       # Employee data model
│   ├── user.py                  # User data model
│   ├── salary.py                # Salary data model
│   └── ...                      # Other models
├── schemas/
│   ├── employee.py              # Employee schemas
│   ├── auth_new.py              # Auth request/response schemas
│   └── ...                      # Other schemas
├── services/
│   ├── employee_service.py      # Employee business logic
│   ├── salary_service.py        # Salary business logic
│   ├── email_service.py         # Email service
│   ├── token_service.py         # Token management
│   └── ...                      # Other services
└── main.py                      # Application entry point

manifests/
├── deployment.yaml              # K8s deployment
├── service.yaml                 # K8s service
└── secrets.yaml                 # K8s secrets & configmap

docker-compose.yml              # Local development setup
Dockerfile                      # Production container image
requirements.txt                # Python dependencies
example.env                     # Environment template
```

---

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_employees.py

# Run with coverage
pytest --cov=src tests/
```

### Test Database
Tests use in-memory SQLite by default (see `tests/conftest.py`)

---

## 🔍 Troubleshooting

### Issue: Database Connection Error
```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Test connection locally
psql "$DATABASE_URL" -c "SELECT 1"

# In Docker: check network
docker network ls
docker inspect hrms-default
```

### Issue: Port Already in Use
```bash
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill process (Windows)
taskkill /PID <PID> /F
```

### Issue: Module Import Error
```bash
# Ensure virtual environment is activated
.venv\Scripts\activate

# Reinstall dependencies
pip install --no-cache-dir -r requirements.txt
```

### Issue: CORS Errors
- Check `CORS_ORIGINS` includes your frontend domain
- Verify domain uses correct protocol (https/http)
- No trailing slashes in URLs

### Issue: Email Not Sending
- Verify all SMTP variables are set
- Check credentials are correct
- Ensure firewall allows outbound SMTP
- For Gmail: use app-specific passwords

### Issue: Application Won't Start (Missing FRONTEND_URL)
- Ensure `.env` file exists or environment variables are set
- Default `FRONTEND_URL` is `http://localhost:3000`
- For production, override with your actual frontend URL

---

## 🔒 Security Best Practices

✅ **Implemented**:
- No hardcoded secrets in source code
- Secrets stored in environment variables
- Non-root container user (UID 1000)
- Health checks configured
- Resource limits set
- Proper logging (no debug prints)
- CORS dynamically configured
- JWT token-based authentication
- Password hashing with bcrypt
- SQL injection protection via ORM

⚠️ **Before Production**:
- [ ] Change default SECRET_KEY
- [ ] Use strong DATABASE_URL password
- [ ] Set DEBUG=false
- [ ] Set DEV_MODE=false
- [ ] Configure HTTPS/TLS
- [ ] Enable Azure KeyVault
- [ ] Set up monitoring & alerting
- [ ] Regular security updates

---

## 📈 Performance Tuning

### Database Connection Pool
```python
# In src/models/session.py
engine = create_engine(
    database_url,
    pool_size=20,           # Adjust based on workload
    max_overflow=0,
    pool_pre_ping=True,
    echo=False
)
```

### Kubernetes Resources
```yaml
# In manifests/deployment.yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### Caching
- Implement Redis for session caching
- Cache employee data
- Cache salary calculations

---

## 📦 Dependencies

### Core
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation

### Database
- **psycopg2-binary** - PostgreSQL adapter
- **asyncpg** - Async PostgreSQL driver
- **Alembic** - Database migrations

### Security
- **python-jose** - JWT tokens
- **passlib** - Password hashing
- **bcrypt** - Encryption

### Utilities
- **python-multipart** - Form data
- **email-validator** - Email validation
- **requests** - HTTP client

See `requirements.txt` for full list and versions.

---

## 📞 Support & Documentation

### Built-in API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

### Health Check
```bash
curl http://localhost:8000/health
# Response: {"status": "healthy"}
```

### Configuration Files
- `example.env` - Environment variables template
- `src/config/settings.py` - Configuration class
- `Dockerfile` - Container configuration
- `manifests/deployment.yaml` - K8s deployment config

---

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] All environment variables set
- [ ] SECRET_KEY is strong (32+ chars)
- [ ] DATABASE_URL uses production database
- [ ] FRONTEND_URL set to production domain
- [ ] CORS_ORIGINS includes production domains only
- [ ] DEBUG=false
- [ ] DEV_MODE=false
- [ ] SMTP credentials configured
- [ ] Container image built and pushed to ACR
- [ ] Kubernetes manifests updated with correct image tag
- [ ] Secrets stored in KeyVault, not in repo
- [ ] Health checks passing
- [ ] Logs monitored for errors
- [ ] Database backups configured
- [ ] SSL/TLS certificates configured
- [ ] Firewall rules allowing traffic

---

## 📝 Recent Changes

### Version 1.0 (December 19, 2025)
- ✅ Fixed all hardcoded credentials
- ✅ Made environment variables properly configurable
- ✅ Removed debug print statements
- ✅ Implemented dynamic CORS configuration
- ✅ Added comprehensive documentation
- ✅ Prepared for AKS deployment
- ✅ Security audit complete
- ✅ Production-ready configuration

---

## 📄 License

[Add your license information here]

---

## 👥 Contributors

[Add contributor information here]

---

**Last Updated**: December 19, 2025  
**Status**: Production Ready for AKS  
**Python Version**: 3.11+  
**Database**: PostgreSQL 12+
