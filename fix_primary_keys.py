import psycopg2

# Database connection
conn = psycopg2.connect(
    host="127.0.0.1",
    database="HRMS-Backend",
    user="postgres",
    password="Panda@123"
)

cur = conn.cursor()

# Fix primary keys to auto-increment
tables_and_columns = [
    ("job_titles", "job_title_id"),
    ("shift_master", "shift_id"),
    ("departments", "department_id"),
    ("events_holidays", "id"),
    ("off_boarding", "id"),
    ("time_entries", "id"),
    ("assets", "asset_id"),
    ("bank_details", "bank_id")
]

for table, column in tables_and_columns:
    try:
        # Create sequence
        cur.execute(f"CREATE SEQUENCE IF NOT EXISTS {table}_{column}_seq")
        
        # Set sequence ownership
        cur.execute(f"ALTER SEQUENCE {table}_{column}_seq OWNED BY {table}.{column}")
        
        # Set current sequence value
        cur.execute(f"SELECT setval('{table}_{column}_seq', COALESCE(MAX({column}), 0) + 1, false) FROM {table}")
        
        # Set column default
        cur.execute(f"ALTER TABLE {table} ALTER COLUMN {column} SET DEFAULT nextval('{table}_{column}_seq')")
        
        print(f"Fixed {table}.{column}")
        
    except Exception as e:
        print(f"Error fixing {table}.{column}: {e}")

conn.commit()
cur.close()
conn.close()
print("All primary keys fixed!")