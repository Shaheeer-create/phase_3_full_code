"""
Conversations API router for chat functionality.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel

from database import get_session
from dependencies import get_current_user_id
from models import Conversation, Message
from services.gemini_agent import generate_response, generate_conversation_title
from services.usage_tracker import check_limits, increment_usage, get_usage_stats
from services.streaming import stream_gemini_response

router = APIRouter(prefix="/api")


# Request/Response Models
class CreateConversationRequest(BaseModel):
    title: str = "New Conversation"


class UpdateConversationRequest(BaseModel):
    title: str


class SendMessageRequest(BaseModel):
    content: str


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    tool_calls: Optional[Any] = None  # Can be list or dict depending on tool execution
    tokens_used: Optional[int] = None
    created_at: datetime


class ConversationWithMessagesResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]


class UsageResponse(BaseModel):
    messages_today: int
    tokens_this_month: int
    max_messages_per_day: int
    max_tokens_per_month: int
    messages_remaining: int
    tokens_remaining: int


# Endpoints

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: CreateConversationRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """Create a new conversation."""
    conversation = Conversation(
        user_id=user_id,
        title=request.title,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)

    return conversation


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """List all conversations for the current user."""
    query = select(Conversation).where(
        Conversation.user_id == user_id
    ).order_by(Conversation.updated_at.desc())

    result = await session.execute(query)
    conversations = result.scalars().all()

    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessagesResponse)
async def get_conversation(
    conversation_id: int,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """Get a specific conversation with all its messages."""
    # Verify ownership
    conv_query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    conv_result = await session.execute(conv_query)
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get messages
    msg_query = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc())

    msg_result = await session.execute(msg_query)
    messages = msg_result.scalars().all()

    return ConversationWithMessagesResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                tool_calls=msg.tool_calls,
                tokens_used=msg.tokens_used,
                created_at=msg.created_at
            )
            for msg in messages
        ]
    )


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    request: UpdateConversationRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """Update conversation title."""
    query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    result = await session.execute(query)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation.title = request.title
    conversation.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(conversation)

    return conversation


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """Delete a conversation and all its messages."""
    query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    result = await session.execute(query)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Delete all messages first
    msg_query = select(Message).where(Message.conversation_id == conversation_id)
    msg_result = await session.execute(msg_query)
    messages = msg_result.scalars().all()

    for message in messages:
        await session.delete(message)

    # Delete conversation
    await session.delete(conversation)
    await session.commit()

    return {"message": "Conversation deleted successfully"}


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: int,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """Get all messages in a conversation."""
    # Verify ownership
    conv_query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    conv_result = await session.execute(conv_query)
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get messages
    msg_query = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc())

    msg_result = await session.execute(msg_query)
    messages = msg_result.scalars().all()

    return [
        MessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            tool_calls=msg.tool_calls,
            tokens_used=msg.tokens_used,
            created_at=msg.created_at
        )
        for msg in messages
    ]


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: int,
    request: SendMessageRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """Send a message and get AI response (non-streaming)."""
    # Verify ownership
    conv_query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    conv_result = await session.execute(conv_query)
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Check usage limits
    await check_limits(user_id, session)

    # Save user message
    user_msg = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=request.content,
        tokens_used=0,
        created_at=datetime.utcnow()
    )
    session.add(user_msg)
    await session.commit()

    # Auto-generate title if this is the first message
    msg_count_query = select(Message).where(Message.conversation_id == conversation_id)
    msg_count_result = await session.execute(msg_count_query)
    message_count = len(msg_count_result.scalars().all())

    if message_count == 1:  # First message (just added user message)
        title = await generate_conversation_title(request.content)
        conversation.title = title
        conversation.updated_at = datetime.utcnow()
        await session.commit()

    # Get recent message history
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

    # Generate response
    response_data = await generate_response(messages, user_id, session)

    # Save assistant message
    assistant_msg = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="assistant",
        content=response_data["content"],
        tool_calls=response_data.get("tool_calls"),
        tokens_used=response_data["tokens_used"],
        created_at=datetime.utcnow()
    )
    session.add(assistant_msg)

    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(assistant_msg)

    # Increment usage tracking
    await increment_usage(user_id, session, response_data["tokens_used"])

    return MessageResponse(
        id=assistant_msg.id,
        role=assistant_msg.role,
        content=assistant_msg.content,
        tool_calls=assistant_msg.tool_calls,
        tokens_used=assistant_msg.tokens_used,
        created_at=assistant_msg.created_at
    )


@router.post("/conversations/{conversation_id}/stream")
async def stream_message(
    conversation_id: int,
    request: SendMessageRequest,
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """Send a message and stream AI response via SSE."""
    # Auto-generate title if this is the first message
    msg_count_query = select(Message).where(Message.conversation_id == conversation_id)
    msg_count_result = await session.execute(msg_count_query)
    message_count = len(msg_count_result.scalars().all())

    if message_count == 0:  # First message
        conv_query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conv_result = await session.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()

        if conversation:
            title = await generate_conversation_title(request.content)
            conversation.title = title
            conversation.updated_at = datetime.utcnow()
            await session.commit()

    return StreamingResponse(
        stream_gemini_response(conversation_id, request.content, user_id, session),
        media_type="text/event-stream"
    )


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """Get current usage statistics for the user."""
    stats = await get_usage_stats(user_id, session)
    return UsageResponse(**stats)
