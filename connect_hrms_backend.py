import psycopg2
from sqlalchemy import create_engine, text

# Connect to Hrms-backend database
DATABASE_URL = "postgresql://postgres:Bhavitha1$@localhost/Hrms-backend"
engine = create_engine(DATABASE_URL)

print("Connecting to Hrms-backend database...")

try:
    with engine.connect() as conn:
        # Verify connection
        result = conn.execute(text("SELECT current_database()"))
        db_name = result.fetchone()[0]
        print(f"Connected to: {db_name}")
        
        # Check if users table exists
        result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"))
        users_exists = result.fetchone()[0]
        
        if users_exists:
            print("Users table exists")
            # Check user count
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            count = result.fetchone()[0]
            print(f"Users table has {count} records")
        else:
            print("Users table does not exist - creating it...")
            # Create users table
            conn.execute(text("""
                CREATE TABLE users (
                    user_id VARCHAR(20) PRIMARY KEY,
                    email VARCHAR UNIQUE,
                    hashed_password VARCHAR,
                    employee_id VARCHAR UNIQUE,
                    role VARCHAR,
                    full_name VARCHAR,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """))
            
            # Insert sample data
            conn.execute(text("""
                INSERT INTO users (user_id, employee_id, email, full_name, role, hashed_password, created_at, updated_at) 
                VALUES 
                ('EMP001', 'EMP001', 'john.manager@company.com', 'John Manager', 'Manager', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXzgVrqUm/pW', NOW(), NOW()),
                ('EMP002', 'EMP002', 'sarah.executive@company.com', 'Sarah Executive', 'Executive', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdXzgVrqUm/pW', NOW(), NOW())
            """))
            conn.commit()
            print("Users table created with sample data")
            
except Exception as e:
    print(f"Error: {e}")

print("\nHrms-backend database is ready for your application!")