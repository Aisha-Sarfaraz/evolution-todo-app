"""ChatKit-compatible endpoint using the openai-chatkit Python SDK.

Uses ChatKitServer to handle the exact protocol the ChatKit frontend expects.
"""

import logging
import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Request, Response
from chatkit.server import ChatKitServer, StreamingResult, NonStreamingResult
from chatkit.store import Store
from chatkit.types import (
    ThreadMetadata,
    UserMessageItem,
    AssistantMessageItem,
    ThreadItemDoneEvent,
    ThreadItemAddedEvent,
    Page,
)

from src.database import async_session_maker
from src.services.chat_service import ChatService

logger = logging.getLogger("chatkit.route")

router = APIRouter(tags=["chatkit"])


# ============================================================================
# In-memory Store for thread/item persistence
# ============================================================================

class InMemoryStore(Store[dict]):
    """Simple in-memory store for ChatKit threads and items."""

    def __init__(self) -> None:
        self._threads: dict[str, ThreadMetadata] = {}
        self._items: dict[str, list] = {}  # thread_id -> list of items

    def generate_thread_id(self, context: dict) -> str:
        return str(uuid.uuid4())

    def generate_item_id(self, item_type: str, thread: ThreadMetadata, context: dict) -> str:
        return str(uuid.uuid4())

    async def load_thread(self, thread_id: str, context: dict) -> ThreadMetadata:
        if thread_id in self._threads:
            return self._threads[thread_id]
        raise KeyError(f"Thread {thread_id} not found")

    async def load_threads(self, after: str | None, limit: int, order: str, context: dict) -> Page:
        threads = list(self._threads.values())
        return Page(data=threads, has_more=False)

    async def load_thread_items(self, thread_id: str, after: str | None, limit: int, order: str, context: dict) -> Page:
        items = self._items.get(thread_id, [])
        return Page(data=items, has_more=False)

    async def load_item(self, thread_id: str, item_id: str, context: dict):
        for item in self._items.get(thread_id, []):
            if item.id == item_id:
                return item
        raise KeyError(f"Item {item_id} not found")

    async def create_thread(self, thread: ThreadMetadata, context: dict) -> None:
        self._threads[thread.id] = thread
        self._items[thread.id] = []

    async def update_thread(self, thread_id: str, thread: ThreadMetadata, context: dict) -> None:
        self._threads[thread_id] = thread

    async def delete_thread(self, thread_id: str, context: dict) -> None:
        self._threads.pop(thread_id, None)
        self._items.pop(thread_id, None)

    async def add_thread_item(self, thread_id: str, item: Any, context: dict) -> None:
        if thread_id not in self._items:
            self._items[thread_id] = []
        self._items[thread_id].append(item)

    async def update_thread_item(self, thread_id: str, item_id: str, item: Any, context: dict) -> None:
        items = self._items.get(thread_id, [])
        for i, existing in enumerate(items):
            if existing.id == item_id:
                items[i] = item
                return

    async def delete_thread_item(self, thread_id: str, item_id: str, context: dict) -> None:
        items = self._items.get(thread_id, [])
        self._items[thread_id] = [it for it in items if it.id != item_id]

    async def delete_attachment(self, attachment_id: str, context: dict) -> None:
        pass

    async def load_attachment(self, attachment_id: str, context: dict):
        raise KeyError(f"Attachment {attachment_id} not found")

    async def save_thread(self, thread: ThreadMetadata, context: dict) -> None:
        self._threads[thread.id] = thread
        if thread.id not in self._items:
            self._items[thread.id] = []

    async def save_item(self, thread_id: str, item: Any, context: dict) -> None:
        if thread_id not in self._items:
            self._items[thread_id] = []
        # Update existing or append
        items = self._items[thread_id]
        for i, existing in enumerate(items):
            if existing.id == item.id:
                items[i] = item
                return
        items.append(item)

    async def save_attachment(self, attachment: Any, context: dict) -> None:
        pass


# ============================================================================
# ChatKit Server Implementation
# ============================================================================

store = InMemoryStore()


class TodoChatKitServer(ChatKitServer[dict]):
    """ChatKit server that delegates to our ChatService."""

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: dict,
    ) -> AsyncIterator:
        """Process user message and yield ChatKit events."""
        if not input_user_message:
            return

        user_text = ""
        for part in input_user_message.content:
            if hasattr(part, "text"):
                user_text += part.text

        if not user_text:
            return

        user_id = context.get("user_id", "anonymous")

        # Call our existing ChatService
        async with async_session_maker() as session:
            try:
                service = ChatService(session=session)
                result = await service.process_message(
                    user_id=user_id,
                    message=user_text,
                    conversation_id=thread.id,
                )

                now = datetime.now(timezone.utc).isoformat()
                assistant_item = AssistantMessageItem(
                    id=self.store.generate_item_id("message", thread, context),
                    thread_id=thread.id,
                    created_at=now,
                    type="assistant_message",
                    role="assistant",
                    content=[{"type": "output_text", "text": result["response"]}],
                    status="completed",
                )

                yield ThreadItemAddedEvent(type="thread.item.added", item=assistant_item)
                yield ThreadItemDoneEvent(type="thread.item.done", item=assistant_item)

            except Exception as e:
                logger.error("ChatKit respond error: %s", e, exc_info=True)
                await session.rollback()

                now = datetime.now(timezone.utc).isoformat()
                error_item = AssistantMessageItem(
                    id=self.store.generate_item_id("message", thread, context),
                    thread_id=thread.id,
                    created_at=now,
                    type="assistant_message",
                    role="assistant",
                    content=[{"type": "output_text", "text": f"Sorry, I encountered an error: {e}"}],
                    status="completed",
                )
                yield ThreadItemAddedEvent(type="thread.item.added", item=error_item)
                yield ThreadItemDoneEvent(type="thread.item.done", item=error_item)


chatkit_server = TodoChatKitServer(store=store)


# ============================================================================
# FastAPI Endpoint
# ============================================================================

@router.post("/api/chatkit")
async def chatkit_endpoint(request: Request) -> Response:
    """ChatKit-compatible endpoint using the official SDK."""
    raw_body = await request.body()

    # Extract user_id from auth header
    auth_header = request.headers.get("authorization", "")
    user_id = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else "anonymous"

    context = {"user_id": user_id}

    logger.info("ChatKit request from user %s, body: %s", user_id, raw_body[:500])

    result = await chatkit_server.process(raw_body, context)

    if isinstance(result, StreamingResult):
        async def event_stream():
            async for chunk in result:
                yield chunk

        from starlette.responses import StreamingResponse
        return StreamingResponse(
            event_stream(),
            media_type=result.content_type,
            headers=dict(result.headers) if result.headers else {},
        )
    elif isinstance(result, NonStreamingResult):
        return Response(
            content=result.body,
            media_type=result.content_type,
            headers=dict(result.headers) if result.headers else {},
        )
    else:
        return Response(content="Internal error", status_code=500)
