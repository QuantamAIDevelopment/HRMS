import sqlite3

def fix_job_titles_table():
    conn = sqlite3.connect('hrms.db')
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='job_titles';")
    if not cursor.fetchone():
        print("Creating job_titles table...")
        cursor.execute("""
            CREATE TABLE job_titles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(100) NOT NULL,
                description TEXT,
                department VARCHAR(100),
                level VARCHAR(50),
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME
            );
        """)
        cursor.execute("CREATE INDEX idx_job_titles_title ON job_titles(title);")
        print("Table created successfully")
    else:
        print("Table already exists")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_job_titles_table()