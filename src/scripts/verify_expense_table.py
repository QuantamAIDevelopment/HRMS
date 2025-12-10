import os
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:psycho539@localhost:5432/hrms_db")
engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

print("employee_expenses table columns:")
for column in inspector.get_columns('employee_expenses'):
    print(f"  - {column['name']}: {column['type']} (nullable={column['nullable']})")
