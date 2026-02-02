"""
Usage tracking and rate limiting service.
Tracks message counts and token usage per user.
"""
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import UserUsage
from datetime import datetime, timedelta
from fastapi import HTTPException
from config import settings


async def check_limits(user_id: str, session: AsyncSession) -> None:
    """
    Check if user has exceeded usage limits.
    Raises HTTPException if limits exceeded.

    Args:
        user_id: User ID from JWT
        session: Database session

    Raises:
        HTTPException: If usage limits exceeded
    """
    usage = await get_or_create_usage(user_id, session)

    # Reset daily counter if it's a new day
    today = datetime.utcnow().date()
    last_message_date = usage.last_message_date.date()

    if today > last_message_date:
        usage.messages_today = 0
        usage.last_message_date = datetime.utcnow()
        await session.commit()

    # Reset monthly counter if it's a new month
    current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_reset = usage.last_reset_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    if current_month > last_reset:
        usage.tokens_this_month = 0
        usage.last_reset_date = datetime.utcnow()
        await session.commit()

    # Check daily message limit
    if usage.messages_today >= settings.max_messages_per_day:
        raise HTTPException(
            status_code=429,
            detail=f"Daily message limit reached ({settings.max_messages_per_day} messages per day). Try again tomorrow."
        )

    # Check monthly token limit
    if usage.tokens_this_month >= settings.max_tokens_per_month:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly token limit reached ({settings.max_tokens_per_month} tokens per month). Limit resets next month."
        )


async def increment_usage(
    user_id: str,
    session: AsyncSession,
    tokens: int
) -> None:
    """
    Increment usage counters for a user.

    Args:
        user_id: User ID from JWT
        session: Database session
        tokens: Number of tokens used in this request
    """
    usage = await get_or_create_usage(user_id, session)

    usage.messages_today += 1
    usage.tokens_this_month += tokens
    usage.last_message_date = datetime.utcnow()
    usage.updated_at = datetime.utcnow()

    await session.commit()


async def get_or_create_usage(
    user_id: str,
    session: AsyncSession
) -> UserUsage:
    """
    Get existing usage record or create a new one.

    Args:
        user_id: User ID from JWT
        session: Database session

    Returns:
        UserUsage record
    """
    query = select(UserUsage).where(UserUsage.user_id == user_id)
    result = await session.execute(query)
    usage = result.scalar_one_or_none()

    if not usage:
        usage = UserUsage(
            user_id=user_id,
            messages_today=0,
            tokens_this_month=0,
            last_message_date=datetime.utcnow(),
            last_reset_date=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(usage)
        await session.commit()
        await session.refresh(usage)

    return usage


async def get_usage_stats(
    user_id: str,
    session: AsyncSession
) -> dict:
    """
    Get current usage statistics for a user.

    Args:
        user_id: User ID from JWT
        session: Database session

    Returns:
        Dict with usage statistics
    """
    usage = await get_or_create_usage(user_id, session)

    # Reset counters if needed (same logic as check_limits)
    today = datetime.utcnow().date()
    last_message_date = usage.last_message_date.date()

    if today > last_message_date:
        usage.messages_today = 0
        usage.last_message_date = datetime.utcnow()
        await session.commit()

    current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_reset = usage.last_reset_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    if current_month > last_reset:
        usage.tokens_this_month = 0
        usage.last_reset_date = datetime.utcnow()
        await session.commit()

    return {
        "messages_today": usage.messages_today,
        "tokens_this_month": usage.tokens_this_month,
        "max_messages_per_day": settings.max_messages_per_day,
        "max_tokens_per_month": settings.max_tokens_per_month,
        "messages_remaining": settings.max_messages_per_day - usage.messages_today,
        "tokens_remaining": settings.max_tokens_per_month - usage.tokens_this_month
    }
