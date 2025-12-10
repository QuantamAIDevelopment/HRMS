from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.constants import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
import random
import string
import bcrypt

security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')[:72]
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password, hashed_password)

def get_password_hash(password):
    if isinstance(password, str):
        password = password.encode('utf-8')[:72]
    return bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    now = datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": int(now.timestamp())})
    print(f"DEBUG: Token data before encoding: {to_encode}")
    token = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    print(f"DEBUG: Generated token: {token}")
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("email")
        user_id: str = payload.get("sub")
        if email is None and user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return email if email else user_id
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token verification failed")

def get_current_user_email(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return verify_token(credentials.credentials)

def generate_otp(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))

def generate_reset_token(length: int = 32) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))