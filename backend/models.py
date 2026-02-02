"""
Database models using SQLModel.
"""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text, JSON
from datetime import datetime
from typing import Optional


class Task(SQLModel, table=True):
    """
    Task model with user isolation.

    CRITICAL: All queries MUST filter by user_id to ensure data isolation.
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # From JWT 'sub' claim - CRITICAL for user isolation
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Conversation(SQLModel, table=True):
    """Conversation model with user isolation."""
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(default="New Conversation", max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    """Message model for chat history."""
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(index=True)
    role: str = Field(max_length=20)  # 'user', 'assistant', 'tool'
    content: str = Field(sa_column=Column(Text))
    tool_calls: Optional[str] = Field(default=None, sa_column=Column(JSON))
    tokens_used: Optional[int] = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserUsage(SQLModel, table=True):
    """Track user API usage for rate limiting."""
    __tablename__ = "user_usage"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, unique=True)
    messages_today: int = Field(default=0)
    tokens_this_month: int = Field(default=0)
    last_message_date: datetime = Field(default_factory=datetime.utcnow)
    last_reset_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
