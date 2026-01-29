"""User SQLModel - Authentication and profile management."""

from datetime import datetime
from typing import Optional
from uuid import uuid4
import sqlalchemy as sa
from sqlmodel import Field, SQLModel, Relationship, Column


class User(SQLModel, table=True):
    """User entity for authentication and profile management.

    Attributes:
        id: Unique identifier (string, Better Auth format)
        email: Unique email address (RFC 5322 format)
        password_hash: Bcrypt hashed password (never exposed in API responses)
        email_verified: Email verification status (default: False)
        display_name: Optional display name for user profile
        created_at: Account creation timestamp (immutable)
        last_signin_at: Last successful signin timestamp (updated on each signin)

    Relationships:
        tasks: All tasks owned by this user
        categories: All custom categories created by this user
        tags: All tags created by this user
    """

    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid4()), sa_column=Column(sa.VARCHAR(64), primary_key=True, nullable=False))
    email: str = Field(max_length=255, nullable=False, unique=True, index=True)
    password_hash: str = Field(max_length=255, nullable=False)
    email_verified: bool = Field(default=False, nullable=False)
    display_name: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    last_signin_at: Optional[datetime] = Field(default=None)

    # Relationships (will be defined after all models are created to avoid circular imports)
    # tasks: list["Task"] = Relationship(back_populates="user")
    # categories: list["Category"] = Relationship(back_populates="user")
    # tags: list["Tag"] = Relationship(back_populates="user")


class UserCreate(SQLModel):
    """Schema for user registration."""
    email: str
    password: str  # Plain text password (will be hashed before storage)
    display_name: Optional[str] = None


class UserRead(SQLModel):
    """Schema for user profile responses (excludes password_hash)."""
    id: str
    email: str
    email_verified: bool
    display_name: Optional[str]
    created_at: datetime
    last_signin_at: Optional[datetime]


class UserUpdate(SQLModel):
    """Schema for user profile updates."""
    display_name: Optional[str] = None
    password: Optional[str] = None  # Plain text password (will be hashed before storage)
