"""
Server-Sent Events (SSE) streaming service for real-time chat responses.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models import Conversation, Message
from services.gemini_agent import stream_response
from services.usage_tracker import check_limits, increment_usage
from datetime import datetime
import json


async def stream_gemini_response(
    conversation_id: int,
    user_message: str,
    user_id: str,
    session: AsyncSession
) -> AsyncGenerator[str, None]:
    """
    Stream Gemini response tokens via Server-Sent Events.

    Args:
        conversation_id: ID of the conversation
        user_message: User's message content
        user_id: Current user ID
        session: Database session

    Yields:
        SSE-formatted strings with tokens and metadata
    """
    try:
        # Verify conversation ownership
        conv_query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conv_result = await session.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()

        if not conversation:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Conversation not found'})}\n\n"
            return

        # Check usage limits
        await check_limits(user_id, session)

        # Save user message
        user_msg = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="user",
            content=user_message,
            tokens_used=0,
            created_at=datetime.utcnow()
        )
        session.add(user_msg)
        await session.commit()

        # Get recent message history (last 10 messages for context)
        history_query = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(10)
        history_result = await session.execute(history_query)
        history_messages = list(reversed(history_result.scalars().all()))

        # Convert to format expected by Gemini agent
        messages = [
            {
                "role": msg.role if msg.role != "assistant" else "model",
                "content": msg.content
            }
            for msg in history_messages
        ]

        # Stream response
        full_response = ""
        tool_calls = None
        tokens_used = 0

        async for chunk in stream_response(messages, user_id, session):
            if chunk["type"] == "token":
                full_response += chunk["content"]
                yield f"data: {json.dumps(chunk)}\n\n"

            elif chunk["type"] == "tool_call":
                yield f"data: {json.dumps(chunk)}\n\n"

            elif chunk["type"] == "complete":
                full_response = chunk["full_response"]
                tool_calls = chunk.get("tool_calls")
                tokens_used = chunk["tokens_used"]

        # Save assistant message
        assistant_msg = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="assistant",
            content=full_response,
            tool_calls=json.dumps(tool_calls) if tool_calls else None,
            tokens_used=tokens_used,
            created_at=datetime.utcnow()
        )
        session.add(assistant_msg)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()

        await session.commit()

        # Increment usage tracking
        await increment_usage(user_id, session, tokens_used)

        # Send completion signal
        yield f"data: {json.dumps({'type': 'done', 'tokens_used': tokens_used})}\n\n"

    except Exception as e:
        error_msg = {
            "type": "error",
            "message": str(e)
        }
        yield f"data: {json.dumps(error_msg)}\n\n"
