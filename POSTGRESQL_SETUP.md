# PostgreSQL Setup for HRMS

## 1. Install PostgreSQL Driver
```bash
pip install psycopg2-binary
```

## 2. Configure Database Connection

Update `.env` file with your PostgreSQL credentials:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/hrms_db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Replace:
- `username` - Your PostgreSQL username
- `password` - Your PostgreSQL password
- `localhost` - Database host (use localhost for local)
- `5432` - PostgreSQL port (default is 5432)
- `hrms_db` - Your database name

## 3. Create Database

Connect to PostgreSQL and create the database:
```sql
CREATE DATABASE hrms_db;
```

## 4. Run SQL Schema

Execute the HRMS schema SQL file to create all tables including the compliance_documents_and_policy_management table.

## 5. Start Application
```bash
uvicorn src.main:app --reload
```

## Connection String Format
```
postgresql://[user]:[password]@[host]:[port]/[database]
```

## Example Configurations

### Local Development
```
DATABASE_URL=postgresql://postgres:admin123@localhost:5432/hrms_db
```

### Docker
```
DATABASE_URL=postgresql://postgres:postgres@db:5432/hrms_db
```

### Cloud (AWS RDS)
```
DATABASE_URL=postgresql://admin:password@hrms.xxxxx.us-east-1.rds.amazonaws.com:5432/hrms_db
```
