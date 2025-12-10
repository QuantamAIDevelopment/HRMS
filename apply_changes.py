from sqlalchemy import create_engine, text
from src.config.settings import settings

engine = create_engine(settings.database_url)

with engine.connect() as conn:
    # Make employee_id NOT NULL in employee_personal_details
    conn.execute(text("ALTER TABLE employee_personal_details ALTER COLUMN employee_id SET NOT NULL"))
    conn.commit()
    print("Applied foreign key changes successfully!")