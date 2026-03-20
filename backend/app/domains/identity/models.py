# app/domains/identity/models.py
from datetime import datetime, timedelta
from typing import Optional
import uuid

from sqlalchemy import (
    Column, String, Text, Boolean, ForeignKey, CheckConstraint,
    UniqueConstraint, PrimaryKeyConstraint, DateTime, SmallInteger, Uuid
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import func

from app.db.base import Base


# ──────────────────────────────────────────────────────────────────────────────
# Role Model
# ──────────────────────────────────────────────────────────────────────────────
class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("name", name="uq_roles_name"),
    )

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    user_roles = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan"
    )


# ──────────────────────────────────────────────────────────────────────────────
# User Model
# ──────────────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("username", name="uq_users_username"),
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    roles = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="UserRole.user_id"
    )
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    bans_received = relationship(
        "Ban",
        back_populates="user",
        foreign_keys="Ban.user_id",
        cascade="all, delete-orphan"
    )
    bans_issued = relationship(
        "Ban",
        back_populates="banned_by_user",
        foreign_keys="Ban.banned_by",
        cascade="all, delete-orphan"
    )
    devices = relationship(
        "Device",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# ──────────────────────────────────────────────────────────────────────────────
# User Roles Join Table
# ──────────────────────────────────────────────────────────────────────────────
class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (
        PrimaryKeyConstraint("user_id", "role_id", name="pk_user_roles"),
    )

    user_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role_id = Column(
        SmallInteger,
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    assigned_by = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    assigned_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="roles")
    role = relationship("Role", back_populates="user_roles")
    assigned_by_user = relationship(
        "User",
        foreign_keys=[assigned_by],
        viewonly=True
    )


# ──────────────────────────────────────────────────────────────────────────────
# Refresh Tokens
# ──────────────────────────────────────────────────────────────────────────────
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    jti = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    is_revoked = Column(Boolean, default=False, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")


# ──────────────────────────────────────────────────────────────────────────────
# Bans
# ──────────────────────────────────────────────────────────────────────────────
class Ban(Base):
    __tablename__ = "bans"
    __table_args__ = (
        CheckConstraint("length(reason) >= 10", name="ck_ban_reason_length"),
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    banned_by = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    reason = Column(Text, nullable=False)
    banned_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    lifted_at = Column(DateTime(timezone=True), nullable=True)
    lifted_by = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="bans_received"
    )
    banned_by_user = relationship(
        "User",
        foreign_keys=[banned_by],
        back_populates="bans_issued"
    )
    lifted_by_user = relationship(
        "User",
        foreign_keys=[lifted_by],
        viewonly=True
    )


# ──────────────────────────────────────────────────────────────────────────────
# Devices (TTL: 90 days)
# ──────────────────────────────────────────────────────────────────────────────
class Device(Base):
    __tablename__ = "devices"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "device_hash",
            name="uq_devices_user_device_hash"
        ),
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    device_hash = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="devices")

    @classmethod
    def calculate_expiry(cls) -> datetime:
        """Calculate device expiry as 90 days from now"""
        return datetime.utcnow() + timedelta(days=90)