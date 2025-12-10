"""
Add missing columns to employee_personal_details table
Run from HRMS directory: python add_columns.py
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

# Load environment variables
load_dotenv('.env')

DATABASE_URL = os.getenv('DATABASE_URL')

def add_missing_columns():
    engine = create_engine(DATABASE_URL)
    
    # Columns to add with their SQL types
    columns_to_add = [
        ('city', 'VARCHAR(100)'),
        ('pincode', 'VARCHAR(20)'),
        ('country', 'VARCHAR(100)'),
        ('state', 'VARCHAR(100)'),
    ]
    
    with engine.connect() as conn:
        # Get existing columns
        inspector = inspect(engine)
        existing_columns = [col['name'] for col in inspector.get_columns('employee_personal_details')]
        
        print(f"Existing columns: {existing_columns}\n")
        
        # Add missing columns
        for col_name, col_type in columns_to_add:
            if col_name not in existing_columns:
                try:
                    alter_sql = f"ALTER TABLE employee_personal_details ADD COLUMN {col_name} {col_type}"
                    print(f"Adding: {col_name}")
                    conn.execute(text(alter_sql))
                    conn.commit()
                    print(f"[OK] Added column: {col_name}")
                except Exception as e:
                    print(f"[ERROR] Failed to add {col_name}: {str(e)}")
            else:
                print(f"- Column {col_name} already exists")
        
        print("\nMigration completed!")

if __name__ == "__main__":
    add_missing_columns()
