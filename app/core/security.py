from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


from passlib.context import CryptContext
from app.core.config import settings


""" hashing algorithm and methods to verify plain password with hash and token creation"""

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_access_token(sub: str, minutes: int | None = None, secret: str | None = None) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": sub, "exp": exp},
        secret or settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
