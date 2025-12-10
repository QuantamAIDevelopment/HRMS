# Database Errors Fixed

## Summary
Fixed 3 critical database errors that were causing 500 Internal Server Errors.

---

## Error 1: Column users.user_id does not exist ✅ FIXED

### Problem
```
psycopg2.errors.UndefinedColumn: column users.user_id does not exist
```

The User model defined a `user_id` column, but the actual PostgreSQL database table didn't have this column.

### Root Cause
- User model had both `id` (primary key) and `user_id` columns
- Database table only had `id` column
- SQLAlchemy was trying to SELECT a non-existent column

### Solution Applied
**File: `src/models/user.py`**
- Removed `user_id = Column(Integer, unique=True, index=True)` 
- Kept only `id` as the primary key
- This matches the actual database schema

**File: `src/api/v1/auth.py`**
- Changed `user.user_id` to `user.id` in token creation (2 places)
- Changed `user.user_id` to `user.id` in LoginResponse

---

## Error 2: Multiple classes found for path "EmployeePersonalDetails" ✅ FIXED

### Problem
```
sqlalchemy.exc.InvalidRequestError: Multiple classes found for path "EmployeePersonalDetails" 
in the registry of this declarative base.
```

### Root Cause
Two different model classes were mapping to the same database table:
1. `EmployeePersonalDetails` in `Employee_models.py` (plural)
2. `EmployeePersonalDetail` in `hrms_models.py` (singular)

Both mapped to table `employee_personal_details`, causing SQLAlchemy registry conflict.

### Solution Applied
**File: `src/models/hrms_models.py`**
- Removed the duplicate `EmployeePersonalDetail` class entirely
- Added comment to use `EmployeePersonalDetails` from `Employee_models.py` instead
- This eliminates the registry conflict

---

## Error 3: Textual SQL expression should be explicitly declared as text() ✅ FIXED

### Problem
```
Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')
```

### Root Cause
Raw SQL string was passed to `db.execute()` without wrapping it in SQLAlchemy's `text()` function.

### Solution Applied
**File: `src/api/v1/complete_employee.py`**
- Added import: `from sqlalchemy import text`
- Changed `db.execute("SELECT 1")` to `db.execute(text("SELECT 1"))`
- This follows SQLAlchemy 2.0+ best practices

---

## Testing Instructions

1. **Restart your FastAPI server**
   ```bash
   # Stop the current server (Ctrl+C)
   # Start it again
   uvicorn src.main:app --reload --port 8001
   ```

2. **Test the login endpoint**
   ```bash
   POST http://127.0.0.1:8001/api/v1/auth/login
   {
     "email": "user@example.com",
     "password": "your_password"
   }
   ```

3. **Test the database connection**
   ```bash
   GET http://127.0.0.1:8001/api/v1/test-db
   ```

4. **Test available assets**
   ```bash
   GET http://127.0.0.1:8001/api/v1/get-available-assets
   ```

---

## What Changed

### Modified Files
1. ✅ `src/models/user.py` - Removed user_id column
2. ✅ `src/api/v1/auth.py` - Updated to use user.id instead of user.user_id
3. ✅ `src/api/v1/complete_employee.py` - Wrapped SQL in text()
4. ✅ `src/models/hrms_models.py` - Removed duplicate EmployeePersonalDetail class

### No Database Migration Needed
Since we removed a column that didn't exist in the database anyway, no migration is required. The code now matches your existing database schema.

---

## Prevention Tips

1. **Always sync models with database**: Use Alembic migrations to keep models and database in sync
2. **Avoid duplicate model definitions**: Each table should have only ONE model class
3. **Use text() for raw SQL**: Always wrap raw SQL strings in `text()` function
4. **Test after changes**: Run all endpoints after model changes to catch issues early

---

## Status: ✅ ALL ERRORS FIXED

Your application should now work without these 500 errors!
