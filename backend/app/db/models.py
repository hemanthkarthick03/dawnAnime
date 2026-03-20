# Aggregate imports for Alembic discovery
from app.domains.identity.models import (
    Role, User, UserRole, RefreshToken, Ban, Device
)

__all__ = [
    "Role",
    "User", 
    "UserRole",
    "RefreshToken",
    "Ban",
    "Device",
]
