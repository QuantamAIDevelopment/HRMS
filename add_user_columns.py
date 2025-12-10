"""
Add employee_id and role columns to users table
Run from HRMS directory: python add_user_columns.py
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

load_dotenv('.env')
DATABASE_URL = os.getenv('DATABASE_URL')

def add_user_columns():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        inspector = inspect(engine)
        existing_columns = [col['name'] for col in inspector.get_columns('users')]
        
        print(f"Existing columns: {existing_columns}\n")
        
        # Add employee_id if missing
        if 'employee_id' not in existing_columns:
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN employee_id VARCHAR UNIQUE"))
                conn.commit()
                print("[OK] Added employee_id column")
            except Exception as e:
                print(f"[ERROR] Failed to add employee_id: {str(e)}")
        else:
            print("- employee_id already exists")
        
        # Add role if missing
        if 'role' not in existing_columns:
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR NOT NULL DEFAULT 'EMPLOYEE'"))
                conn.commit()
                print("[OK] Added role column")
            except Exception as e:
                print(f"[ERROR] Failed to add role: {str(e)}")
        else:
            print("- role already exists")
        
        # Add full_name column
        if 'full_name' not in existing_columns:
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR NOT NULL DEFAULT ''"))
                conn.commit()
                print("[OK] Added full_name column")
            except Exception as e:
                print(f"[ERROR] Failed to add full_name: {str(e)}")
        else:
            print("- full_name already exists")
        
        print("\nMigration completed!")

if __name__ == "__main__":
    add_user_columns()
