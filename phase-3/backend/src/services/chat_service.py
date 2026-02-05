"""Chat service - orchestrates conversation and agent invocation.

Uses LiteLLM with function calling to invoke task tools directly.
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.conversation import Conversation
from src.models.message import Message

logger = logging.getLogger("chat_service")

CONTEXT_WINDOW_SIZE = 7

# Tool definitions for function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task for the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title (1-200 characters)"},
                    "description": {"type": "string", "description": "Optional task description"},
                    "priority": {"type": "string", "enum": ["Low", "Medium", "High", "Urgent"], "description": "Task priority, defaults to Medium"},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List user's tasks with optional filters",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["pending", "complete"], "description": "Filter by status"},
                    "priority": {"type": "string", "enum": ["Low", "Medium", "High", "Urgent"], "description": "Filter by priority"},
                    "search": {"type": "string", "description": "Search keyword in title and description"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as complete",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "UUID of the task to complete"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Permanently delete a task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "UUID of the task to delete"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task's title, description, or priority",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "UUID of the task to update"},
                    "title": {"type": "string", "description": "New title (optional)"},
                    "description": {"type": "string", "description": "New description (optional)"},
                    "priority": {"type": "string", "enum": ["Low", "Medium", "High", "Urgent"], "description": "New priority (optional)"},
                },
                "required": ["task_id"],
            },
        },
    },
]

SYSTEM_PROMPT = """You are a helpful task management assistant. Help users manage their tasks by creating, listing, updating, completing, and deleting tasks.

When the user asks you to:
- Create a task: Use the create_task function
- Show/list tasks: Use the list_tasks function
- Complete a task: Use the complete_task function with the task ID
- Delete a task: Use the delete_task function with the task ID
- Update a task: Use the update_task function with the task ID and new values

Always be helpful and confirm actions after completing them. When listing tasks, summarize them clearly."""


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
        """Process a user message and return AI response."""
        start_time = time.monotonic()

        # 1. Load or create conversation
        conversation = await self._get_or_create_conversation(user_id, conversation_id)

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

        # 4. Invoke LLM with tools
        try:
            agent_result = await self._invoke_llm(user_id=user_id, context=context)
        except Exception as e:
            logger.error("LLM invocation failed: %s", e, exc_info=True)
            agent_result = {
                "response": "I'm having trouble processing your request right now. Please try again in a moment.",
                "tool_calls": [],
            }

        duration_ms = int((time.monotonic() - start_time) * 1000)
        logger.info(
            "Chat request processed",
            extra={
                "user_id": user_id,
                "conversation_id": str(conversation.id),
                "duration_ms": duration_ms,
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

        # Update conversation
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
                result = await self.session.execute(
                    select(Conversation).where(
                        Conversation.id == conv_uuid,
                        Conversation.user_id == user_id,
                    )
                )
                existing = result.scalar_one_or_none()
                if existing:
                    return existing
            except ValueError:
                pass

        conversation = Conversation(id=uuid4(), user_id=user_id)
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
        return [{"role": msg.role, "content": msg.content} for msg in reversed(messages)]

    async def _invoke_llm(
        self,
        user_id: str,
        context: list[dict[str, str]],
    ) -> dict[str, Any]:
        """Invoke LLM with function calling."""
        import litellm

        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + context

        # First LLM call
        response = await litellm.acompletion(
            model=f"openrouter/{model}",
            messages=messages,
            tools=TOOLS,
            api_key=openrouter_key,
        )

        assistant_message = response.choices[0].message
        tool_calls_made = []

        # Handle tool calls
        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                func_name = tool_call.function.name
                try:
                    func_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    func_args = {}

                # Execute tool
                tool_result = await self._execute_tool(func_name, func_args, user_id)
                tool_calls_made.append({
                    "tool": func_name,
                    "input": func_args,
                    "output": tool_result,
                })

                # Add tool result to messages
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call.model_dump()],
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                })

            # Get final response after tool execution
            final_response = await litellm.acompletion(
                model=f"openrouter/{model}",
                messages=messages,
                api_key=openrouter_key,
            )
            final_text = final_response.choices[0].message.content or ""
        else:
            final_text = assistant_message.content or ""

        return {
            "response": final_text,
            "tool_calls": tool_calls_made,
        }

    async def _execute_tool(self, func_name: str, args: dict, user_id: str) -> str:
        """Execute a tool function."""
        from src.mcp_tools.tools.task_tools import (
            create_task,
            list_tasks,
            complete_task,
            delete_task,
            update_task,
        )

        try:
            if func_name == "create_task":
                return await create_task(
                    title=args.get("title", ""),
                    user_id=user_id,
                    description=args.get("description"),
                    priority=args.get("priority", "Medium"),
                )
            elif func_name == "list_tasks":
                return await list_tasks(
                    user_id=user_id,
                    status=args.get("status"),
                    priority=args.get("priority"),
                    search=args.get("search"),
                )
            elif func_name == "complete_task":
                return await complete_task(
                    task_id=args.get("task_id", ""),
                    user_id=user_id,
                )
            elif func_name == "delete_task":
                return await delete_task(
                    task_id=args.get("task_id", ""),
                    user_id=user_id,
                )
            elif func_name == "update_task":
                return await update_task(
                    task_id=args.get("task_id", ""),
                    user_id=user_id,
                    title=args.get("title"),
                    description=args.get("description"),
                    priority=args.get("priority"),
                )
            else:
                return f"Unknown function: {func_name}"
        except Exception as e:
            logger.error("Tool execution error: %s", e, exc_info=True)
            return f"Error executing {func_name}: {e}"
