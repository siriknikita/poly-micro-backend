"""Authentication utilities for JWT tokens and password hashing."""
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
import logging

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.jwt_generator import get_or_create_jwt_secret

from app.db.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import TokenPayload
from app.db.database import get_database

# Set up logging
logger = logging.getLogger(__name__)

# Get JWT configuration from environment variables or generate a secure key
SECRET_KEY = get_or_create_jwt_secret()
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

logger.info(f"JWT configured with algorithm {ALGORITHM} and {ACCESS_TOKEN_EXPIRE_MINUTES} minute expiration")

# Initialize password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize OAuth2 password bearer for token extraction from request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that the plain password matches the hashed password.
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password stored in the database
        
    Returns:
        bool: True if the password is correct, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password for storing in the database.
    
    Args:
        password: The plain text password
        
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT token.
    
    Args:
        subject: The subject of the token (usually user ID)
        expires_delta: Optional custom expiration time, defaults to ACCESS_TOKEN_EXPIRE_MINUTES
        
    Returns:
        str: The encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db=Depends(get_database)
) -> User:
    """
    Get the current user from the JWT token.
    
    Args:
        token: The JWT token extracted from the request
        db: The database connection
        
    Returns:
        User: The current authenticated user
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode and validate the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        token_data = TokenPayload(sub=user_id, exp=payload.get("exp"))
        if datetime.fromtimestamp(token_data.exp) < datetime.utcnow():
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user_repo = UserRepository(db)
    user_data = await user_repo.get_user_by_id(user_id)
    
    if user_data is None:
        raise credentials_exception
    
    return User.from_dict(user_data)


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current active user.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        User: The current active user
        
    Raises:
        HTTPException: If the user is disabled
    """
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    
    return current_user
