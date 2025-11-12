import subprocess

def run_migrations():
    subprocess.run(["alembic", "upgrade", "head"])

if __name__ == "__main__":
    run_migrations()