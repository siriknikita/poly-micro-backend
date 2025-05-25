"""JWT secret key generator utility.

This module provides functions to generate and validate JWT secret keys.
"""
import os
import secrets
import base64
import logging

logger = logging.getLogger(__name__)

def generate_jwt_secret_key(length=32):
    """Generate a secure random JWT secret key.
    
    Args:
        length: The length of the key in bytes
        
    Returns:
        str: Base64 encoded secret key
    """
    # Generate a secure random key
    key = secrets.token_bytes(length)
    # Encode as base64 for storage
    encoded_key = base64.urlsafe_b64encode(key).decode('utf-8')
    return encoded_key


def get_or_create_jwt_secret():
    """Get JWT secret key from environment or generate a new one.
    
    Returns:
        str: The JWT secret key
    """
    # Try to get from environment variable
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    
    # If not set or is the default value, generate a new one
    if not jwt_secret or jwt_secret == "YourSuperSecretKeyHere" or jwt_secret == "CHANGE_ME_IN_PRODUCTION_ENVIRONMENT":
        jwt_secret = generate_jwt_secret_key()
        logger.info("Generated new JWT secret key")
        
        # Save to .env file if it exists and we have write permissions
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        if os.path.exists(env_file):
            try:
                with open(env_file, "r") as f:
                    lines = f.readlines()
                
                # Check if JWT_SECRET_KEY already exists in file
                jwt_line_index = None
                for i, line in enumerate(lines):
                    if line.startswith("JWT_SECRET_KEY="):
                        jwt_line_index = i
                        break
                
                # Replace or add the line
                if jwt_line_index is not None:
                    lines[jwt_line_index] = f"JWT_SECRET_KEY={jwt_secret}\n"
                else:
                    # Check if JWT section exists
                    jwt_section_exists = False
                    for line in lines:
                        if "# JWT Authentication" in line:
                            jwt_section_exists = True
                            break
                    
                    if not jwt_section_exists:
                        lines.append("\n# JWT Authentication\n")
                    
                    lines.append(f"JWT_SECRET_KEY={jwt_secret}\n")
                
                # Write back to file
                with open(env_file, "w") as f:
                    f.writelines(lines)
                
                logger.info(f"Updated JWT secret key in {env_file}")
            except Exception as e:
                logger.warning(f"Could not update JWT secret key in .env file: {e}")
    
    return jwt_secret
