"""Question schemas for validation and serialization."""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class QuestionBase(BaseModel):
    """Base question schema with common attributes."""
    title: str
    content: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None


class QuestionCreate(QuestionBase):
    """Schema for question creation."""
    pass


class QuestionInDB(QuestionBase):
    """Schema for question in database."""
    id: Optional[str] = Field(alias="_id", default=None)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    status: str = "pending"  # pending, answered, closed

    class Config:
        """Pydantic configuration."""
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class Question(QuestionBase):
    """Schema for question response."""
    id: Optional[str] = None
    created_at: str
    status: str = "pending"

    class Config:
        """Pydantic configuration."""
        populate_by_name = True
