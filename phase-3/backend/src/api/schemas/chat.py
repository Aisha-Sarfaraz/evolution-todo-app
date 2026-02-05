"""T035: Chat request/response Pydantic schemas."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for POST /api/{user_id}/chat."""

    conversation_id: Optional[str] = Field(
        default=None,
        description="Existing conversation ID to continue. Omit to start a new conversation.",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User message text.",
    )
    timezone: Optional[str] = Field(
        default=None,
        description="User's timezone (e.g., 'America/New_York') for date parsing.",
    )


class ToolCallInfo(BaseModel):
    """Details of a single tool invocation."""

    tool: str
    input: dict[str, Any]
    output: dict[str, Any]


class ChatResponse(BaseModel):
    """Response schema for POST /api/{user_id}/chat."""

    conversation_id: str
    response: str
    tool_calls: list[ToolCallInfo] = Field(default_factory=list)
