from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

# JWT Configuration
SECRET_KEY = "SUPER_SECRET_KEY"  # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash a password
def hash_password(password: str) -> str:
    # bcrypt only supports up to 72 bytes
    truncated = password.encode("utf-8")[:72]
    return pwd_context.hash(truncated)

# Verify a password
def verify_password(password: str, hashed: str) -> bool:
    truncated = password.encode("utf-8")[:72]
    return pwd_context.verify(truncated, hashed)

# Create JWT access token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
