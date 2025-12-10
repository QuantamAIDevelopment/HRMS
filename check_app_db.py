from src.models.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # Check current database
    result = db.execute(text('SELECT current_database()'))
    print(f'App connected to: {result.fetchone()[0]}')
    
    # Check if users table exists
    result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users'"))
    tables = result.fetchall()
    print(f'Users table found: {len(tables) > 0}')
    
    if len(tables) > 0:
        # Check table structure
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'"))
        columns = result.fetchall()
        print('Columns in users table:')
        for col in columns:
            print(f'  - {col[0]}')
    else:
        print('Users table does not exist in this database connection')
        
finally:
    db.close()