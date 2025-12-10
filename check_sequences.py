import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('src/.env')

DATABASE_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Check what sequences exist
    cur.execute("""
        SELECT sequence_name 
        FROM information_schema.sequences 
        WHERE sequence_schema = 'public';
    """)
    
    sequences = cur.fetchall()
    print("Available sequences:")
    for seq in sequences:
        print(f"  {seq[0]}")
    
    # Check the actual sequence for users table
    cur.execute("SELECT pg_get_serial_sequence('users', 'user_id');")
    actual_seq = cur.fetchone()
    print(f"\nActual sequence for users.user_id: {actual_seq[0] if actual_seq else 'None'}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")