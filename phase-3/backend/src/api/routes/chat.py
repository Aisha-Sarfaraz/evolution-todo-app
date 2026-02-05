"""T037: Chat API route — POST /api/{user_id}/chat.

Handles authenticated chat messages with rate limiting and error handling.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import ValidatedUser, validate_user_id_match
from src.database import get_session

from src.api.schemas.chat import ChatRequest, ChatResponse, ToolCallInfo
from src.middleware.rate_limit import chat_rate_limiter
from src.services.chat_service import ChatService

logger = logging.getLogger("chat.route")

router = APIRouter(prefix="/api/{user_id}", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: ValidatedUser,
    session: AsyncSession = Depends(get_session),
) -> ChatResponse:
    """Process a chat message and return AI response.

    - Validates JWT auth and user_id match.
    - Enforces 10 msg/min rate limit.
    - Invokes ChatService for agent processing.
    - Returns 503 on LLM failure with friendly message.
    """
    # Rate limit check
    if not chat_rate_limiter.is_allowed(current_user.user_id):
        retry_after = chat_rate_limiter.get_retry_after(current_user.user_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error_code": "RATE_LIMITED",
                "detail": "Too many messages. Please wait before sending another.",
            },
            headers={"Retry-After": str(retry_after)},
        )

    try:
        service = ChatService(session=session)
        result = await service.process_message(
            user_id=current_user.user_id,
            message=request.message,
            conversation_id=request.conversation_id,
            timezone_str=request.timezone,
        )

        return ChatResponse(
            conversation_id=result["conversation_id"],
            response=result["response"],
            tool_calls=[
                ToolCallInfo(**tc) for tc in result.get("tool_calls", [])
            ],
        )

    except Exception as e:
        logger.error("Chat processing error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error_code": "LLM_UNAVAILABLE",
                "detail": "I'm having trouble processing your request right now. Please try again in a moment.",
            },
        )
