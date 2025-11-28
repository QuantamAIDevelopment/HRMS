import psycopg2
from psycopg2 import sql

def create_job_titles_table():
    conn = psycopg2.connect(
        host="localhost",
        database="hrms",
        user="postgres",
        password="password"
    )
    
    cursor = conn.cursor()
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS job_titles (
        id SERIAL PRIMARY KEY,
        title VARCHAR(100) NOT NULL,
        description TEXT,
        department VARCHAR(100),
        level VARCHAR(50),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE
    );
    
    CREATE INDEX IF NOT EXISTS idx_job_titles_title ON job_titles(title);
    """
    
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()
    print("Job titles table created successfully")

if __name__ == "__main__":
    create_job_titles_table()