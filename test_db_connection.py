import psycopg2
import subprocess

print("=== PostgreSQL Connection Troubleshooting ===")

# Check PostgreSQL service
print("\n1. Checking PostgreSQL service...")
try:
    result = subprocess.run(['sc', 'query', 'postgresql-x64-14'], capture_output=True, text=True)
    if 'RUNNING' in result.stdout:
        print("[OK] PostgreSQL service is running")
    else:
        print("[ERROR] PostgreSQL service not running")
        print("Try: net start postgresql-x64-14")
except:
    # Try alternative service names
    services = ['postgresql-x64-13', 'postgresql-x64-15', 'postgresql']
    for service in services:
        try:
            result = subprocess.run(['sc', 'query', service], capture_output=True, text=True)
            if 'RUNNING' in result.stdout:
                print(f"[OK] Found running service: {service}")
                break
        except:
            continue
    else:
        print("[ERROR] No PostgreSQL service found running")

# Test common passwords
print("\n2. Testing common passwords...")
passwords = ["postgres", "admin", "password", "123456", "", "Rishi@123"]

for password in passwords:
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            port="5432",
            database="postgres",
            user="postgres",
            password=password
        )
        print(f"[SUCCESS] Connected with password: '{password}'")
        
        # Check if hrms_app database exists
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='hrms_app'")
        if cursor.fetchone():
            print("[OK] hrms_app database exists")
        else:
            print("[INFO] hrms_app database does not exist - will create it")
            cursor.execute("CREATE DATABASE hrms_app")
            conn.commit()
            print("[OK] Created hrms_app database")
        
        cursor.close()
        conn.close()
        
        # Test connection to hrms_app
        conn = psycopg2.connect(
            host="127.0.0.1",
            port="5432",
            database="hrms_app",
            user="postgres",
            password=password
        )
        print("[SUCCESS] Connected to hrms_app database")
        conn.close()
        
        print(f"\n=== SOLUTION FOUND ===")
        print(f"Use password: '{password}'")
        break
        
    except Exception as e:
        print(f"[FAILED] Password '{password}': {str(e)[:80]}...")

else:
    print("\n=== NO PASSWORD WORKED ===")
    print("Solutions:")
    print("1. Reset password via pgAdmin")
    print("2. Or reinstall PostgreSQL")
    print("3. Or check if PostgreSQL is installed at all")