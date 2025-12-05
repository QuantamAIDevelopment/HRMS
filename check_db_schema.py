import psycopg2
from src.config.settings import settings

def check_attendance_table():
    try:
        conn = psycopg2.connect(
            host=settings.DATABASE_HOST,
            database=settings.DATABASE_NAME,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            port=settings.DATABASE_PORT
        )
        cursor = conn.cursor()
        
        # Check if attendance table exists and get its columns
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'attendance'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("Attendance table columns:")
        for col_name, col_type in columns:
            print(f"  {col_name}: {col_type}")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error checking database schema: {e}")

if __name__ == "__main__":
    check_attendance_table()