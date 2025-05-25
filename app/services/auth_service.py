"""Authentication service for user management and login."""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from app.db.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, Token
from app.core.auth import verify_password, get_password_hash, create_access_token


class AuthService:
    """Service for authentication and user management."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def register_user(self, user_data: UserCreate) -> User:
        """
        Register a new user.
        
        Args:
            user_data: The user data for registration
            
        Returns:
            User: The created user
            
        Raises:
            HTTPException: If the username or email is already taken
        """
        # Check if username already exists
        existing_user = await self.user_repository.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already registered"
            )
        
        # Check if email already exists
        existing_email = await self.user_repository.get_user_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Create new user with hashed password
        hashed_password = get_password_hash(user_data.password)
        user_dict = {
            **user_data.dict(exclude={"password"}),
            "hashed_password": hashed_password,
            "created_at": datetime.now().isoformat(),
            "disabled": False,
        }
        
        created_user = await self.user_repository.create_user(user_dict)
        return User.from_dict(created_user)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: The username
            password: The plain text password
            
        Returns:
            Optional[User]: The authenticated user if credentials are valid, None otherwise
        """
        user_data = await self.user_repository.get_user_by_username(username)
        if not user_data:
            return None
        
        user = User.from_dict(user_data)
        if not verify_password(password, user.hashed_password):
            return None
        
        # Update last login timestamp
        if user.id:
            await self.user_repository.update_last_login(user.id)
            
            # Get updated user data
            updated_user_data = await self.user_repository.get_user_by_id(user.id)
            if updated_user_data:
                return User.from_dict(updated_user_data)
        
        return user
    
    async def login(self, username: str, password: str) -> Token:
        """
        Login a user and generate access token.
        
        Args:
            username: The username
            password: The plain text password
            
        Returns:
            Token: The access token and user information
            
        Raises:
            HTTPException: If credentials are invalid
        """
        user = await self.authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if user.disabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is disabled"
            )
        
        # Create access token
        access_token = create_access_token(subject=user.id)
        
        # Return token and user info (exclude hashed_password)
        user_dict = user.to_dict()
        user_dict.pop("hashed_password", None)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_dict
        )
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: The user ID
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        user_data = await self.user_repository.get_user_by_id(user_id)
        if not user_data:
            return None
        
        return User.from_dict(user_data)
    
    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """
        Update user information.
        
        Args:
            user_id: The user ID
            user_update: The user data to update
            
        Returns:
            Optional[User]: The updated user if found, None otherwise
        """
        # Convert to dict for updates
        update_data = user_update.dict(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_data:
            hashed_password = get_password_hash(update_data.pop("password"))
            update_data["hashed_password"] = hashed_password
        
        # Update user
        updated_user = await self.user_repository.update_user(user_id, update_data)
        if not updated_user:
            return None
        
        return User.from_dict(updated_user)
