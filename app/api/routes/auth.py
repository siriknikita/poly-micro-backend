"""Authentication routes for user registration, login, and token refresh."""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.user import UserCreate, User as UserSchema, Token, UserUpdate
from app.services.auth_service import AuthService
from app.db.repositories.user_repository import UserRepository
from app.db.database import get_database
from app.core.auth import get_current_active_user
from app.models.user import User

router = APIRouter(tags=["Authentication"])


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate = Body(...),
    db=Depends(get_database)
):
    """
    Register a new user.
    
    Args:
        user_data: The user data for registration
        db: The database connection
        
    Returns:
        User: The created user
    """
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    user = await auth_service.register_user(user_data)
    
    # Convert to response model (exclude hashed_password)
    user_dict = user.to_dict()
    user_dict.pop("hashed_password", None)
    
    return user_dict


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(get_database)
):
    """
    Login with username and password.
    
    Args:
        form_data: The login form data with username and password
        db: The database connection
        
    Returns:
        Token: The access token and user information
    """
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    return await auth_service.login(form_data.username, form_data.password)


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        User: The current user information
    """
    # Convert to response model (exclude hashed_password)
    user_dict = current_user.to_dict()
    user_dict.pop("hashed_password", None)
    
    return user_dict


@router.put("/me", response_model=UserSchema)
async def update_current_user(
    user_update: UserUpdate = Body(...),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Update current user information.
    
    Args:
        user_update: The user data to update
        current_user: The current authenticated user
        db: The database connection
        
    Returns:
        User: The updated user information
    """
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    
    updated_user = await auth_service.update_user(current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Convert to response model (exclude hashed_password)
    user_dict = updated_user.to_dict()
    user_dict.pop("hashed_password", None)
    
    return user_dict
