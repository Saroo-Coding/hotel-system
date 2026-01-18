from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

import secrets
import string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_temp_password(length=settings.LENGTH_OF_TEMP_PASSWORD):
    ''' Generate a random temporary password '''
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))

def hash_password(password: str) -> str:
    ''' Hash the password '''
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    ''' Verify the password '''
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    ''' Create a JWT token '''
    to_encode = data.copy()
    expire = datetime.now() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def decode_token(token: str) -> dict:
    ''' Decode a JWT token '''
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
