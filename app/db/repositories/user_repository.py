"""User repository for database operations."""
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from .base_repository import BaseRepository
from app.models.user import User
from app.core.cache import cached, invalidate_cache
from bson import ObjectId


class UserRepository(BaseRepository):
    """Repository for user-related database operations"""
    
    def __init__(self, db):
        super().__init__(db, "users")
    
    @cached(ttl=300, prefix="users:all")
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users with caching"""
        return await self.find_all()
    
    @cached(ttl=300, prefix="users:by_id")
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID with caching"""
        return await self.find_one(user_id)
    
    @cached(ttl=300, prefix="users:by_username")
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get a user by username with caching"""
        return await self.find_one_by_field("username", username)
    
    @cached(ttl=300, prefix="users:by_email")
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by email with caching"""
        return await self.find_one_by_field("email", email)
    
    @invalidate_cache(prefix="users")
    async def create_user(self, user: Union[Dict[str, Any], User]) -> Dict[str, Any]:
        """Create a new user and invalidate cache"""
        # Convert User object to dictionary if needed
        if isinstance(user, User):
            user_dict = user.to_dict()
        else:
            user_dict = user
        
        # Set created_at if not provided
        if not user_dict.get("created_at"):
            user_dict["created_at"] = datetime.now().isoformat()
        
        return await self.create(user_dict)
    
    @invalidate_cache(prefix="users")
    async def update_user(self, user_id: str, user_update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a user and invalidate cache"""
        # Only update provided fields
        update_data = {k: v for k, v in user_update.items() if v is not None}
        
        if not update_data:
            return await self.find_one(user_id)  # Return current user if no updates
        
        return await self.update(user_id, update_data)
    
    @invalidate_cache(prefix="users")
    async def update_last_login(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Update user's last login timestamp and invalidate cache"""
        update_data = {"last_login": datetime.now().isoformat()}
        return await self.update(user_id, update_data)
    
    @invalidate_cache(prefix="users")
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user and invalidate cache"""
        return await self.delete(user_id)
