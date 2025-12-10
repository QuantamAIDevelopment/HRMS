import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv('.env')
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    result = conn.execute(text("SELECT email, LENGTH(hashed_password) as pwd_len, hashed_password FROM users WHERE email = 'gugulothuasmitha@gmail.com'")).fetchone()
    if result:
        print(f"Email: {result[0]}")
        print(f"Password Length: {result[1]}")
        print(f"Hash starts with: {result[2][:20]}")
        
        # Update with a proper bcrypt hash
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        new_hash = pwd_context.hash("Admin@123")
        
        conn.execute(text("UPDATE users SET hashed_password = :hash WHERE email = 'gugulothuasmitha@gmail.com'"), {"hash": new_hash})
        conn.commit()
        print(f"\nUpdated password hash to: {new_hash}")
