import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseConnection:
    def __init__(self):
        self.config = {
            'host': '127.0.0.1',
            'port': '5432',
            'database': 'hrms_app',
            'user': 'postgres',
            'password': 'Rishi@123'
        }
    
    def get_connection(self):
        return psycopg2.connect(**self.config)
    
    def get_dict_cursor(self):
        conn = self.get_connection()
        return conn, conn.cursor(cursor_factory=RealDictCursor)

# Test the connection
if __name__ == "__main__":
    db = DatabaseConnection()
    try:
        conn = db.get_connection()
        print("Database connection successful!")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")