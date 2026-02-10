"""
Database models using SQLModel.
"""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text, JSON
from datetime import datetime
from typing import Optional, Literal


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

    # Phase V: Advanced features
    priority: str = Field(default="medium", max_length=10)  # low, medium, high
    due_date: Optional[datetime] = Field(default=None)
    is_recurring: bool = Field(default=False)
    parent_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")
    recurrence_instance_date: Optional[datetime] = Field(default=None)

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


# ============================================================================
# Phase V: Advanced Features Models
# ============================================================================


class TaskTag(SQLModel, table=True):
    """Tags associated with tasks for categorization."""
    __tablename__ = "task_tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    tag_name: str = Field(max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RecurringPattern(SQLModel, table=True):
    """Defines how recurring tasks should be generated."""
    __tablename__ = "recurring_patterns"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    frequency: str = Field(max_length=20)  # daily, weekly, monthly, yearly
    interval: int = Field(default=1)  # Every N days/weeks/months/years
    days_of_week: Optional[str] = Field(default=None, max_length=50)  # JSON array: [0,1,2,3,4,5,6]
    day_of_month: Optional[int] = Field(default=None)  # 1-31
    month_of_year: Optional[int] = Field(default=None)  # 1-12
    end_date: Optional[datetime] = Field(default=None)
    last_generated_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskReminder(SQLModel, table=True):
    """Reminders for tasks."""
    __tablename__ = "task_reminders"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    user_id: str = Field(index=True)
    reminder_time: datetime
    reminder_type: str = Field(default="notification", max_length=20)  # notification, email, both
    is_sent: bool = Field(default=False)
    sent_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):
    """Audit trail for all task operations."""
    __tablename__ = "audit_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    entity_type: str = Field(max_length=50)  # task, conversation, message
    entity_id: int
    action: str = Field(max_length=20)  # create, update, delete, complete, uncomplete
    old_values: Optional[str] = Field(default=None, sa_column=Column(JSON))
    new_values: Optional[str] = Field(default=None, sa_column=Column(JSON))
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)
