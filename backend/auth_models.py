"""
Authentication models for user management.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class User(SQLModel, table=True):
    """User model for authentication."""
    __tablename__ = "users"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, sa_column_kwargs={"server_default": "gen_random_uuid()"})
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    hashed_password: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
