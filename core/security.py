import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from config import JWT_SECRET, JWT_ALGORITHM

def hash_password(p: str) -> str:
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def create_access_token(data: dict) -> str:
    d = data.copy()
    d["exp"] = datetime.now(timezone.utc) + timedelta(days=30)
    return jwt.encode(d, JWT_SECRET, algorithm=JWT_ALGORITHM)

def jwt_decode(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])