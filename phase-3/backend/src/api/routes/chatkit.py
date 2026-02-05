"""ChatKit-compatible SSE chat endpoint.

Accepts ChatKit's request format and returns Server-Sent Events (SSE) stream.
This endpoint bridges ChatKit's frontend protocol with the existing ChatService.
"""

import json
import logging
from typing import Any, AsyncGenerator, Optional

from fastapi import APIRouter, HTTPException, Request, status
from sse_starlette.sse import EventSourceResponse

from src.database import async_session_maker
from src.services.chat_service import ChatService

logger = logging.getLogger("chatkit.route")

router = APIRouter(tags=["chatkit"])


async def stream_response(
    user_id: str,
    message: str,
    thread_id: Optional[str] = None,
) -> AsyncGenerator[dict, None]:
    """Run ChatService and yield SSE events with its own session."""
    async with async_session_maker() as session:
        try:
            service = ChatService(session=session)
            result = await service.process_message(
                user_id=user_id,
                message=message,
                conversation_id=thread_id,
            )

            # Yield the full response as a single content event
            yield {
                "event": "message",
                "data": json.dumps({"content": result["response"]}),
            }

            # Signal done with thread_id
            yield {
                "event": "message",
                "data": json.dumps({
                    "done": True,
                    "thread_id": result["conversation_id"],
                }),
            }

        except Exception as e:
            logger.error("ChatKit stream error: %s", e, exc_info=True)
            await session.rollback()
            yield {
                "event": "message",
                "data": json.dumps({"error": str(e)}),
            }


@router.post("/api/chatkit")
async def chatkit_chat(request: Request):
    """ChatKit-compatible SSE chat endpoint.

    Accepts ChatKit's message format and returns SSE stream.
    Very permissive parsing to handle various ChatKit formats.
    """
    # Parse raw JSON to see exactly what ChatKit sends
    try:
        raw_body = await request.body()
        logger.info(f"ChatKit raw body: {raw_body.decode('utf-8', errors='replace')[:1000]}")
        body = json.loads(raw_body)
    except Exception as e:
        logger.error(f"Failed to parse request body: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON body: {e}",
        )

    # Extract messages - try various possible field names
    messages = body.get("messages") or body.get("Messages") or []

    # If messages is empty, check if there's a single message/prompt field
    if not messages:
        single_message = body.get("message") or body.get("prompt") or body.get("input")
        if single_message:
            if isinstance(single_message, str):
                messages = [{"role": "user", "content": single_message}]
            elif isinstance(single_message, dict):
                messages = [single_message]

    if not messages:
        logger.error(f"No messages found in body: {body}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided",
        )

    # Get user_id from various possible field names
    user_id = (
        body.get("user_id") or
        body.get("userId") or
        body.get("user") or
        "anonymous"
    )

    # Get thread_id from various possible field names
    thread_id = (
        body.get("thread_id") or
        body.get("threadId") or
        body.get("thread") or
        body.get("conversation_id") or
        body.get("conversationId")
    )

    # Extract the last message (find last user message if possible)
    last_msg = None
    for msg in reversed(messages):
        if isinstance(msg, dict):
            role = msg.get("role", "").lower()
            if role in ("user", "human", ""):
                last_msg = msg
                break

    # If no user message found, just use the last message
    if not last_msg and messages:
        last_msg = messages[-1]

    if not last_msg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid message found",
        )

    # Extract content from message
    if isinstance(last_msg, dict):
        content = last_msg.get("content") or last_msg.get("text") or last_msg.get("message") or ""
    elif isinstance(last_msg, str):
        content = last_msg
    else:
        content = str(last_msg)

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content is empty",
        )

    logger.info(f"Processing message for user {user_id}: {content[:100]}...")

    return EventSourceResponse(
        stream_response(
            user_id=user_id,
            message=content,
            thread_id=thread_id,
        ),
    )
