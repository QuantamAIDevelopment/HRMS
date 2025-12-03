# Database Setup Instructions

## Step 1: Create Database
```bash
psql -U postgres
```

```sql
CREATE DATABASE hrms_db;
\c hrms_db
```

## Step 2: Run Schema
```bash
psql -U postgres -d hrms_db -f hrms_schema.sql
```

Or from psql:
```sql
\i hrms_schema.sql
```

## Step 3: Verify Tables
```sql
\dt
```

You should see all 16 tables including `compliance_documents_and_policy_management`.

## Step 4: Update Connection String
Update `.env` file:
```env
DATABASE_URL=postgresql://postgres:Karthik@2202@localhost:5432/hrms_db
```

## Step 5: Start Application
```bash
uvicorn src.main:app --reload
```

Access API at: http://localhost:8000/docs
