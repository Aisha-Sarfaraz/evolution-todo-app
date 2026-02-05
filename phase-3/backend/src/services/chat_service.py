"""T036/T100: Chat service — orchestrates conversation, context, and agent invocation.

Manages conversation lifecycle, message storage, 7-message context window,
Agent invocation via MCPServerStreamableHttp, and response extraction.
Includes token usage tracking per request.
"""

import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.conversation import Conversation
from src.models.message import Message

logger = logging.getLogger("chat_service")

CONTEXT_WINDOW_SIZE = 7


class ChatService:
    """Orchestrates chat interactions between user and AI agent."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        timezone_str: Optional[str] = None,
    ) -> dict[str, Any]:
        """Process a user message and return AI response.

        1. Load or create conversation.
        2. Store user message.
        3. Load context (last 7 messages).
        4. Invoke Agent via MCPServerStreamableHttp.
        5. Extract response and tool_calls.
        6. Store assistant message.

        Args:
            user_id: Authenticated user ID.
            message: User's message text.
            conversation_id: Optional existing conversation to continue.
            timezone_str: User's timezone for date parsing.

        Returns:
            Dict with conversation_id, response, and tool_calls.
        """
        # 1. Load or create conversation
        conversation = await self._get_or_create_conversation(
            user_id, conversation_id
        )

        # 2. Store user message
        user_msg = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            user_id=user_id,
            role="user",
            content=message,
        )
        self.session.add(user_msg)
        await self.session.flush()

        # 3. Load context window
        context = await self._load_context(conversation.id)

        # 4. Invoke agent with timing
        start_time = time.monotonic()
        try:
            agent_result = await self._invoke_agent(
                user_id=user_id,
                context=context,
                timezone_str=timezone_str,
            )
        except Exception as e:
            logger.error("Agent invocation failed: %s", e)
            agent_result = {
                "response": "I'm having trouble processing your request right now. Please try again in a moment.",
                "tool_calls": [],
                "usage": None,
            }
        duration_ms = int((time.monotonic() - start_time) * 1000)

        # T100: Log token usage
        usage = agent_result.get("usage")
        logger.info(
            "Chat request processed",
            extra={
                "user_id": user_id,
                "conversation_id": str(conversation.id),
                "duration_ms": duration_ms,
                "tokens_used": usage,
            },
        )

        # 5. Store assistant message
        assistant_msg = Message(
            id=uuid4(),
            conversation_id=conversation.id,
            user_id=user_id,
            role="assistant",
            content=agent_result["response"],
            tool_calls=agent_result.get("tool_calls"),
        )
        self.session.add(assistant_msg)

        # Update conversation title from first message
        if conversation.title is None:
            conversation.title = message[:100]

        conversation.updated_at = datetime.utcnow()
        await self.session.commit()

        return {
            "conversation_id": str(conversation.id),
            "response": agent_result["response"],
            "tool_calls": agent_result.get("tool_calls", []),
        }

    async def _get_or_create_conversation(
        self, user_id: str, conversation_id: Optional[str]
    ) -> Conversation:
        """Load existing conversation or create a new one."""
        if conversation_id:
            try:
                conv_uuid = UUID(conversation_id)
            except ValueError:
                pass
            else:
                result = await self.session.execute(
                    select(Conversation).where(
                        Conversation.id == conv_uuid,
                        Conversation.user_id == user_id,
                    )
                )
                existing = result.scalar_one_or_none()
                if existing:
                    return existing

        # Create new conversation
        conversation = Conversation(
            id=uuid4(),
            user_id=user_id,
        )
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    async def _load_context(self, conversation_id: UUID) -> list[dict[str, str]]:
        """Load the last CONTEXT_WINDOW_SIZE messages for context."""
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(CONTEXT_WINDOW_SIZE)
        )
        messages = result.scalars().all()

        # Reverse to chronological order
        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]

    async def _invoke_agent(
        self,
        user_id: str,
        context: list[dict[str, str]],
        timezone_str: Optional[str] = None,
    ) -> dict[str, Any]:
        """Invoke the AI agent with MCP tools.

        Uses OpenAI Agents SDK with MCPServerStreamableHttp to connect
        to the standalone MCP server.
        """
        from agents import Agent, Runner, set_tracing_disabled, ModelSettings
        from agents.mcp import MCPServerStreamableHttp
        from agents.extensions.models.litellm_model import LitellmModel

        from src.agent.config import get_model_name
        from src.agent.prompts import SYSTEM_PROMPT

        # Disable tracing to avoid OpenAI API key issues with OpenRouter
        set_tracing_disabled(True)

        # MCP URL - use embedded server by default (same app at /mcp)
        # For Hugging Face Spaces, the app runs on port 7860
        # For local dev with separate MCP server, set MCP_PORT and MCP_HOST
        mcp_url = os.getenv("MCP_URL")
        if not mcp_url:
            mcp_port = os.getenv("MCP_PORT") or os.getenv("PORT", "7860")
            mcp_host = os.getenv("MCP_HOST", "localhost")
            mcp_url = f"http://{mcp_host}:{mcp_port}/mcp"

        # Build system prompt with user context
        system_prompt = SYSTEM_PROMPT
        if timezone_str:
            system_prompt += f"\n\nUser's timezone: {timezone_str}"
        system_prompt += f"\n\nUser ID (for tool calls): {user_id}"

        # Use LitellmModel for OpenRouter
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        model_name = get_model_name()
        # LiteLLM uses openrouter/ prefix for OpenRouter models
        litellm_model = LitellmModel(
            model=f"openrouter/{model_name}",
            api_key=openrouter_key,
        )

        async with MCPServerStreamableHttp(
            name="TodoMCP",
            params={"url": mcp_url},
        ) as mcp_server:
            agent = Agent(
                name="TodoAssistant",
                instructions=system_prompt,
                model=litellm_model,
                mcp_servers=[mcp_server],
            )

            result = await Runner.run(
                agent,
                input=context,
            )

            # Extract tool calls from result
            tool_calls = []
            if hasattr(result, "raw_responses"):
                for raw in result.raw_responses:
                    if hasattr(raw, "output") and isinstance(raw.output, list):
                        for item in raw.output:
                            if hasattr(item, "type") and item.type == "function_call":
                                tool_calls.append({
                                    "tool": item.name,
                                    "input": item.arguments if hasattr(item, "arguments") else {},
                                    "output": {},
                                })

            # Extract token usage from raw responses
            usage = None
            if hasattr(result, "raw_responses"):
                total_input = 0
                total_output = 0
                for raw in result.raw_responses:
                    if hasattr(raw, "usage") and raw.usage:
                        total_input += getattr(raw.usage, "input_tokens", 0) or 0
                        total_output += getattr(raw.usage, "output_tokens", 0) or 0
                if total_input or total_output:
                    usage = {
                        "input_tokens": total_input,
                        "output_tokens": total_output,
                        "total_tokens": total_input + total_output,
                    }

            return {
                "response": result.final_output if hasattr(result, "final_output") else str(result),
                "tool_calls": tool_calls,
                "usage": usage,
            }
