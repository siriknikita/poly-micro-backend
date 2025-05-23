"""
Compatibility module for enum-related functionality.
Provides implementations for features not available in older Python versions.
"""
from enum import Enum

# Python 3.10 doesn't have StrEnum natively (it was added in 3.11)
class StrEnum(str, Enum):
    """
    Enum where members are also str instances.
    This is a backport of the StrEnum class from Python 3.11.
    """
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"
