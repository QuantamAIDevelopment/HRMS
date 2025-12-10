import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def migrate_expense_table():
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:psycho539@localhost:5432/hrms_db")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("Adding expense_code column...")
        conn.execute(text("ALTER TABLE employee_expenses ADD COLUMN IF NOT EXISTS expense_code VARCHAR(20)"))
        conn.commit()
        
        print("Adding receipt_url column...")
        conn.execute(text("ALTER TABLE employee_expenses ADD COLUMN IF NOT EXISTS receipt_url TEXT"))
        conn.commit()
        
        print("Updating status default...")
        conn.execute(text("ALTER TABLE employee_expenses ALTER COLUMN status SET DEFAULT 'PENDING'"))
        conn.commit()
        
        print("Updating NULL descriptions...")
        conn.execute(text("UPDATE employee_expenses SET description = '' WHERE description IS NULL"))
        conn.commit()
        
        print("Setting description as NOT NULL...")
        conn.execute(text("ALTER TABLE employee_expenses ALTER COLUMN description SET NOT NULL"))
        conn.commit()
        
        print("Migration completed successfully!")

if __name__ == "__main__":
    migrate_expense_table()
