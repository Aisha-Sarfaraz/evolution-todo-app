"""T051-T053: Conversation API routes.

GET /api/{user_id}/conversations — list conversations
GET /api/{user_id}/conversations/{id}/messages — paginated messages
DELETE /api/{user_id}/conversations/{id} — cascade delete
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import ValidatedUser
from src.database import get_session

from src.models.conversation import Conversation, ConversationRead
from src.models.message import Message, MessageRead

logger = logging.getLogger("conversations.route")

router = APIRouter(prefix="/api/{user_id}", tags=["conversations"])


async def _get_user_conversations(
    user_id: str,
    session: AsyncSession,
) -> list[dict]:
    """Load all conversations for a user, sorted by updated_at DESC."""
    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()

    conv_list = []
    for conv in conversations:
        # Get last message preview
        msg_result = await session.execute(
            select(Message.content)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        last_msg = msg_result.scalar_one_or_none()

        conv_list.append({
            "id": conv.id,
            "title": conv.title,
            "last_message_preview": last_msg[:100] if last_msg else None,
            "updated_at": conv.updated_at,
        })

    return conv_list


@router.get("/conversations")
async def list_conversations(
    user_id: str,
    current_user: ValidatedUser,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """List all conversations for the authenticated user."""
    conversations = await _get_user_conversations(current_user.user_id, session)
    return {"conversations": conversations}


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    user_id: str,
    conversation_id: str,
    current_user: ValidatedUser,
    session: AsyncSession = Depends(get_session),
    limit: int = Query(default=50, ge=1, le=100),
    before: Optional[str] = Query(default=None),
) -> dict:
    """Get messages for a conversation with cursor-based pagination."""
    try:
        conv_uuid = UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")

    # Verify conversation belongs to user
    conv_result = await session.execute(
        select(Conversation).where(
            Conversation.id == conv_uuid,
            Conversation.user_id == current_user.user_id,
        )
    )
    if not conv_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Conversation not found")

    query = (
        select(Message)
        .where(Message.conversation_id == conv_uuid)
        .order_by(Message.created_at.asc())
        .limit(limit + 1)  # Fetch one extra to detect has_more
    )

    if before:
        try:
            before_uuid = UUID(before)
            # Get the created_at of the cursor message
            cursor_result = await session.execute(
                select(Message.created_at).where(Message.id == before_uuid)
            )
            cursor_time = cursor_result.scalar_one_or_none()
            if cursor_time:
                query = query.where(Message.created_at < cursor_time)
        except ValueError:
            pass

    result = await session.execute(query)
    messages = result.scalars().all()

    has_more = len(messages) > limit
    if has_more:
        messages = messages[:limit]

    return {
        "messages": [
            MessageRead(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                tool_calls=msg.tool_calls,
                created_at=msg.created_at,
            ).model_dump()
            for msg in messages
        ],
        "has_more": has_more,
    }


async def _delete_conversation(
    conversation_id: str,
    user_id: str,
    session: AsyncSession,
) -> bool:
    """Delete a conversation and its messages (cascade)."""
    try:
        conv_uuid = UUID(conversation_id)
    except ValueError:
        return False

    result = await session.execute(
        select(Conversation).where(
            Conversation.id == conv_uuid,
            Conversation.user_id == user_id,
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        return False

    await session.delete(conversation)
    await session.commit()
    return True


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    user_id: str,
    conversation_id: str,
    current_user: ValidatedUser,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Delete a conversation and all its messages."""
    deleted = await _delete_conversation(conversation_id, current_user.user_id, session)

    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"deleted": True}
