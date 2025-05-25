"""User model for authentication."""
from datetime import datetime
from typing import Optional
from bson import ObjectId


class User:
    """
    User class for authentication functionality.
    Contains getters and setters for all user fields.
    """

    def __init__(
        self,
        username: str,
        email: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        disabled: bool = False,
        created_at: Optional[str] = None,
        last_login: Optional[str] = None,
        id: Optional[str] = None,
    ):
        self._id = id
        self._username = username
        self._email = email
        self._hashed_password = hashed_password
        self._full_name = full_name
        self._disabled = disabled
        self._created_at = created_at or datetime.now().isoformat()
        self._last_login = last_login

    # ID property
    @property
    def id(self) -> Optional[str]:
        """Get user ID."""
        return self._id

    @id.setter
    def id(self, value: str):
        """Set user ID."""
        self._id = value

    # Username property
    @property
    def username(self) -> str:
        """Get username."""
        return self._username

    @username.setter
    def username(self, value: str):
        """Set username."""
        if not value:
            raise ValueError("Username cannot be empty")
        self._username = value

    # Email property
    @property
    def email(self) -> str:
        """Get email."""
        return self._email

    @email.setter
    def email(self, value: str):
        """Set email."""
        if not value:
            raise ValueError("Email cannot be empty")
        self._email = value

    # Hashed password property
    @property
    def hashed_password(self) -> str:
        """Get hashed password."""
        return self._hashed_password

    @hashed_password.setter
    def hashed_password(self, value: str):
        """Set hashed password."""
        if not value:
            raise ValueError("Hashed password cannot be empty")
        self._hashed_password = value

    # Full name property
    @property
    def full_name(self) -> Optional[str]:
        """Get full name."""
        return self._full_name

    @full_name.setter
    def full_name(self, value: Optional[str]):
        """Set full name."""
        self._full_name = value

    # Disabled property
    @property
    def disabled(self) -> bool:
        """Get disabled status."""
        return self._disabled

    @disabled.setter
    def disabled(self, value: bool):
        """Set disabled status."""
        self._disabled = value

    # Created at property
    @property
    def created_at(self) -> str:
        """Get created at timestamp."""
        return self._created_at

    @created_at.setter
    def created_at(self, value: str):
        """Set created at timestamp."""
        self._created_at = value

    # Last login property
    @property
    def last_login(self) -> Optional[str]:
        """Get last login timestamp."""
        return self._last_login

    @last_login.setter
    def last_login(self, value: Optional[str]):
        """Set last login timestamp."""
        self._last_login = value

    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {
            "id": self._id,
            "username": self._username,
            "email": self._email,
            "hashed_password": self._hashed_password,
            "full_name": self._full_name,
            "disabled": self._disabled,
            "created_at": self._created_at,
            "last_login": self._last_login,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create user from dictionary."""
        return cls(
            id=data.get("id") or str(data.get("_id", "")),
            username=data.get("username", ""),
            email=data.get("email", ""),
            hashed_password=data.get("hashed_password", ""),
            full_name=data.get("full_name"),
            disabled=data.get("disabled", False),
            created_at=data.get("created_at"),
            last_login=data.get("last_login"),
        )
