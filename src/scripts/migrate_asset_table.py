import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def migrate_asset_table():
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:psycho539@localhost:5432/hrms_db")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("Dropping old constraints...")
        conn.execute(text("ALTER TABLE assets DROP CONSTRAINT IF EXISTS check_status"))
        conn.execute(text("ALTER TABLE assets DROP CONSTRAINT IF EXISTS check_condition"))
        conn.commit()
        
        print("Dropping old assigned_employee_id column...")
        conn.execute(text("ALTER TABLE assets DROP COLUMN IF EXISTS assigned_employee_id"))
        conn.commit()
        
        print("Making serial_number NOT NULL...")
        conn.execute(text("UPDATE assets SET serial_number = 'SN' || asset_id WHERE serial_number IS NULL"))
        conn.execute(text("ALTER TABLE assets ALTER COLUMN serial_number SET NOT NULL"))
        conn.commit()
        
        print("Migration completed successfully!")

if __name__ == "__main__":
    migrate_asset_table()
