import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('src/.env')

DATABASE_URL = os.getenv('DATABASE_URL')

def get_next_user_id():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Get next value from sequence
        cur.execute("SELECT nextval('users_user_id_seq');")
        next_id = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return next_id
    except Exception as e:
        print(f"Error getting next user ID: {e}")
        return None

if __name__ == "__main__":
    print(f"Next user ID: {get_next_user_id()}")