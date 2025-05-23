"""
Real-world example of using the Poly Micro Logger in a service.

This example shows how a typical microservice would integrate
with the Poly Micro logging system in a production environment.
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from bson import ObjectId

# Import the logger
from app.utils.logger import create_logger

class UserService:
    """Example user management service that uses the Poly Micro Logger."""
    
    def __init__(self, project_id: str, service_id: str):
        """
        Initialize the user service with a logger.
        
        Args:
            project_id: The project ID this service belongs to
            service_id: The service ID for this service
        """
        self.project_id = project_id
        self.service_id = service_id
        
        # Create the logger for this service
        self.logger = create_logger(project_id, service_id)
        
        # Initialize service data
        self.users_db = {}  # Mock database
        self.logger.info("User service initialized")
    
    async def create_user(self, user_id: str, user_data: Dict) -> Dict:
        """
        Create a new user in the system.
        
        Args:
            user_id: The user ID
            user_data: User information
            
        Returns:
            The created user data
        """
        try:
            # Log the operation start
            self.logger.info(f"Creating user {user_id}", func_id="create_user")
            
            # Validate user data
            if not user_data.get("email"):
                self.logger.error(f"Cannot create user {user_id}: missing email", 
                                func_id="create_user")
                raise ValueError("Email is required")
            
            # Create the user (in a real system, this would be a database operation)
            user = {
                "id": user_id,
                "email": user_data.get("email"),
                "name": user_data.get("name", "Unknown"),
                "created_at": datetime.now().isoformat()
            }
            
            # Store in our mock DB
            self.users_db[user_id] = user
            
            # Log success
            self.logger.info(f"User {user_id} created successfully", 
                           func_id="create_user")
            
            return user
            
        except Exception as e:
            # Log any errors
            self.logger.error(f"Failed to create user {user_id}: {str(e)}", 
                            func_id="create_user")
            raise
    
    async def get_user(self, user_id: str) -> Optional[Dict]:
        """
        Retrieve a user from the system.
        
        Args:
            user_id: The user ID
            
        Returns:
            The user data or None if not found
        """
        try:
            # Log the operation
            self.logger.info(f"Getting user {user_id}", func_id="get_user")
            
            # Check if user exists
            if user_id not in self.users_db:
                self.logger.warning(f"User {user_id} not found", func_id="get_user")
                return None
            
            # Get the user
            user = self.users_db[user_id]
            
            # Log success with debug severity (high volume operation)
            self.logger.debug(f"Retrieved user {user_id}", func_id="get_user")
            
            return user
            
        except Exception as e:
            # Log any errors
            self.logger.error(f"Error retrieving user {user_id}: {str(e)}", 
                            func_id="get_user")
            raise
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user from the system.
        
        Args:
            user_id: The user ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Log the operation with warning severity (potentially destructive)
            self.logger.warning(f"Attempting to delete user {user_id}", 
                              func_id="delete_user")
            
            # Check if user exists
            if user_id not in self.users_db:
                self.logger.warning(f"Cannot delete: User {user_id} not found", 
                                  func_id="delete_user")
                return False
            
            # Delete the user
            del self.users_db[user_id]
            
            # Log success
            self.logger.info(f"User {user_id} deleted successfully", 
                           func_id="delete_user")
            
            return True
            
        except Exception as e:
            # Log any errors
            self.logger.error(f"Error deleting user {user_id}: {str(e)}", 
                            func_id="delete_user")
            raise

# Example usage
async def run_example():
    """Run the real-world example."""
    # Create a user service with project and service IDs
    project_id = "example_project"
    service_id = "user_service"
    user_service = UserService(project_id, service_id)
    
    try:
        # Create a user
        user = await user_service.create_user("user123", {
            "name": "John Doe",
            "email": "john@example.com"
        })
        print(f"Created user: {user}")
        
        # Try to create a user with missing email (will cause error)
        try:
            await user_service.create_user("user456", {"name": "Jane Doe"})
        except ValueError as e:
            print(f"Expected error: {e}")
        
        # Get the user
        retrieved_user = await user_service.get_user("user123")
        print(f"Retrieved user: {retrieved_user}")
        
        # Get a non-existent user
        missing_user = await user_service.get_user("nonexistent")
        print(f"Missing user result: {missing_user}")
        
        # Delete the user
        deleted = await user_service.delete_user("user123")
        print(f"User deleted: {deleted}")
        
        # Try to get the deleted user
        deleted_user = await user_service.get_user("user123")
        print(f"Deleted user result: {deleted_user}")
        
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(run_example())
