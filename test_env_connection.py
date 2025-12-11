import psycopg2
from urllib.parse import unquote

database_url = "postgresql://postgres:Rishi%40123@127.0.0.1:5432/hrms_app"

parts = database_url.replace("postgresql://", "").split("@")
user_pass = parts[0].split(":")
user = user_pass[0]
password = unquote(user_pass[1])
host_db = parts[1].split("/")
host_port = host_db[0].split(":")
host = host_port[0]
port = host_port[1]
database = host_db[1]

print(f"Host: {host}, Port: {port}, DB: {database}, User: {user}, Password: {password}")

try:
    conn = psycopg2.connect(host=host, port=port, database=database, user=user, password=password)
    print("SUCCESS: .env connection works!")
    conn.close()
except Exception as e:
    print(f"FAILED: {e}")
    
    # Check if PostgreSQL service is running
    import subprocess
    try:
        result = subprocess.run(['sc', 'query', 'postgresql-x64-17'], capture_output=True, text=True)
        if 'RUNNING' in result.stdout:
            print("PostgreSQL service is running")
        else:
            print("PostgreSQL service NOT running - start it first!")
    except:
        print("Could not check service status")