"""User schemas for validation and serialization."""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common attributes."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user creation with password."""
    password: str


class UserUpdate(BaseModel):
    """Schema for user updates."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(UserBase):
    """Schema for user in database."""
    id: Optional[str] = Field(alias="_id", default=None)
    hashed_password: str
    disabled: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    last_login: Optional[str] = None

    class Config:
        """Pydantic configuration."""
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class User(UserBase):
    """Schema for user response without sensitive data."""
    id: Optional[str] = None
    disabled: bool = False
    created_at: str
    last_login: Optional[str] = None

    class Config:
        """Pydantic configuration."""
        populate_by_name = True


class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str
    user: User


class TokenPayload(BaseModel):
    """Schema for token payload."""
    sub: str
    exp: int
