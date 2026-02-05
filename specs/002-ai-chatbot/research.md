# Phase 0: Research Findings — AI-Powered Conversational Todo Management

**Feature Branch**: `002-ai-chatbot`
**Created**: 2026-01-31
**Status**: Complete
**Spec**: [spec.md](./spec.md)

---

## 1. OpenAI Agents SDK + OpenRouter Integration

**Decision**: Use OpenAI Agents SDK with `set_default_openai_client()` to route all LLM calls through OpenRouter API.

**Rationale**: The OpenAI Agents SDK supports custom OpenAI-compatible providers via the `set_default_openai_client()` function. OpenRouter exposes an OpenAI-compatible API at `https://openrouter.ai/api/v1`, enabling seamless integration without SDK modifications.

**Implementation Pattern**:

```python
from openai import AsyncOpenAI
from agents import set_default_openai_client, Agent, Runner

# Configure OpenRouter as the LLM provider
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
set_default_openai_client(client)

# Define Agent with model from env
agent = Agent(
    name="TodoAssistant",
    instructions="You are a helpful task management assistant...",
    model=os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
)

# Run agent
result = await Runner.run(agent, messages=conversation_context)
```

**Alternatives Considered**:
- **Direct OpenAI API**: Would lock us to OpenAI models only. Rejected for cost flexibility.
- **LiteLLM proxy**: Additional infrastructure. Rejected — OpenRouter already provides unified gateway.
- **Manual HTTP calls**: No agent orchestration. Rejected — loses SDK benefits (tool calling, structured output).

**Key Findings**:
- `set_default_openai_client()` must be called before any Agent creation
- Model identifier uses OpenRouter format: `provider/model-name` (e.g., `openai/gpt-4o-mini`, `anthropic/claude-3.5-sonnet`)
- OpenRouter supports tool calling for compatible models
- Rate limits managed by OpenRouter per API key

---

## 2. MCP Server (Standalone via FastMCP)

**Decision**: Standalone MCP server using `FastMCP` from the Official MCP SDK, exposing tools over Streamable HTTP transport. Agent connects via `MCPServerStreamableHttp`.

**Rationale**: User selected standalone MCP server for full MCP protocol compliance per spec requirements (FR-011 through FR-020). FastMCP provides a high-level API with `@mcp.tool()` decorators for clean tool definitions.

**Implementation Pattern**:

```python
# mcp_server.py — Standalone MCP server process
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TodoMCP")

@mcp.tool()
async def create_task(title: str, description: str | None = None, priority: str = "medium", user_id: str = "") -> dict:
    """Create a new task for the authenticated user."""
    # Database operations here
    ...

@mcp.tool()
async def list_tasks(user_id: str, status: str | None = None, priority: str | None = None) -> dict:
    """List tasks for the authenticated user with optional filters."""
    ...

# Run as Streamable HTTP server
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)
```

```python
# agent.py — Agent connects to MCP server
from agents.mcp import MCPServerStreamableHttp

async with MCPServerStreamableHttp(url="http://localhost:8001/mcp") as mcp_server:
    agent = Agent(
        name="TodoAssistant",
        instructions="...",
        mcp_servers=[mcp_server],
    )
    result = await Runner.run(agent, messages=context)
```

**Alternatives Considered**:
- **Function tools + MCP schemas**: Simpler but no MCP protocol compliance. Rejected per spec requirement.
- **In-process MCP**: Tighter coupling, harder to test independently. Rejected for separation of concerns.

**Key Findings**:
- FastMCP `@mcp.tool()` automatically generates JSON Schema from Python type hints
- Streamable HTTP transport runs on a configurable port (default: `/mcp` path)
- `MCPServerStreamableHttp` is an async context manager — must be used within `async with`
- User context (`user_id`) must be passed as a tool parameter since MCP tools are stateless
- MCP server needs its own database connection for tool execution

---

## 3. Conversation Context & Memory

**Decision**: Database-backed conversation memory with 7-message sliding window loaded per request.

**Rationale**: Spec FR-004 requires last 7 messages as AI context. Database storage ensures statelessness (FR-007) and persistence across sessions (User Story 2).

**Implementation Pattern**:

```python
# Load context for agent
async def get_conversation_context(conversation_id: str, limit: int = 7) -> list[dict]:
    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = await db.execute(query)
    return [
        {"role": m.role, "content": m.content}
        for m in reversed(messages.scalars().all())
    ]
```

**Key Findings**:
- 7 messages balances context quality vs token cost
- Messages loaded in reverse chronological order, then reversed for correct agent input
- `tool_calls` JSONB column stores structured tool invocation data for frontend display
- Conversation title auto-generated from first user message (truncated to 200 chars)

---

## 4. ChatKit Frontend Integration

**Decision**: OpenAI ChatKit React component with custom API backend pointing to FastAPI `/api/{user_id}/chat`.

**Rationale**: ChatKit provides production-ready chat UI components (message list, input, typing indicators) matching FR-051 through FR-060. Custom backend integration via `backendUrl` prop.

**Implementation Pattern**:

```tsx
// app/page.tsx
import { ChatProvider, ChatMessages, ChatInput } from "@openai/chatkit";

export default function ChatPage() {
  return (
    <ChatProvider
      backendUrl="/api/chat"
      headers={{ Authorization: `Bearer ${token}` }}
    >
      <ChatMessages />
      <ChatInput />
    </ChatProvider>
  );
}
```

**Backend Requirements**:
- FastAPI endpoint must return Server-Sent Events (SSE) or JSON response matching ChatKit expected format
- Custom API route proxies to FastAPI backend with auth token forwarded
- Next.js API route at `/api/chat` handles frontend-to-backend communication

**Alternatives Considered**:
- **Custom chat UI**: Full control but significant development effort. Rejected for hackathon timeline.
- **Vercel AI SDK UI**: Good but opinionated about provider. Rejected — we use OpenRouter, not direct OpenAI.

**Key Findings**:
- ChatKit requires domain allowlist configuration in OpenAI platform for production use
- Custom backend mode uses `backendUrl` prop instead of default OpenAI endpoint
- Supports conversation history display, typing indicators, and message threading
- SSE streaming format recommended for real-time response display

---

## 5. Background Scheduler (Recurrence & Reminders)

**Decision**: APScheduler `AsyncIOScheduler` running within FastAPI lifespan for recurrence checks and reminder notifications.

**Rationale**: Hackathon simplicity — single process, no external scheduler infrastructure. APScheduler integrates natively with asyncio and FastAPI's lifespan context.

**Implementation Pattern**:

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job("interval", minutes=1, id="check_recurrence")
async def check_recurrence():
    """Create new task instances for due recurrence rules."""
    ...

@scheduler.scheduled_job("interval", minutes=1, id="check_reminders")
async def check_reminders():
    """Send push notifications for due reminders."""
    ...

# FastAPI lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()
```

**Alternatives Considered**:
- **Celery + Redis**: Production-grade but heavy infrastructure for hackathon. Rejected.
- **OS cron jobs**: No async support, separate process management. Rejected.
- **FastAPI BackgroundTasks**: Per-request only, not scheduled. Rejected for periodic checks.

**Key Findings**:
- AsyncIOScheduler shares FastAPI's event loop — no thread-safety issues
- 1-minute interval balances responsiveness (SC-006: within 1 hour) vs resource usage
- Scheduler must handle database connections independently (own session per job)
- Graceful shutdown via lifespan ensures in-flight jobs complete

---

## 6. Web Push Notifications

**Decision**: `pywebpush` for server-side push delivery, Service Worker + Push API for browser-side subscription and reception.

**Rationale**: Web Push is the standard browser notification mechanism (FR-034 through FR-037). `pywebpush` is the established Python library for VAPID-based push.

**Implementation Pattern**:

```python
# Server-side push
from pywebpush import webpush

def send_push_notification(subscription: dict, title: str, body: str):
    webpush(
        subscription_info=subscription,
        data=json.dumps({"title": title, "body": body}),
        vapid_private_key=os.environ["VAPID_PRIVATE_KEY"],
        vapid_claims={"sub": "mailto:admin@example.com"},
    )
```

```javascript
// service-worker.js
self.addEventListener("push", (event) => {
  const data = event.data.json();
  event.waitUntil(
    self.registration.showNotification(data.title, { body: data.body })
  );
});
```

**Key Findings**:
- VAPID keys (public + private) generated once, stored as env vars
- PushSubscription stored per user per device (endpoint is unique)
- Subscription can expire — handle `410 Gone` responses by removing stale subscriptions
- Fallback to in-app notifications when push permission denied (FR-037)

---

## 7. Rate Limiting for Chat Endpoint

**Decision**: Extend Phase II's existing in-memory sliding window rate limiter to support 10 msg/min for the chat endpoint.

**Rationale**: Phase II already has a rate limiter at 100 req/min per user. FR-010a requires 10 msg/min specifically for chat. Reuse existing infrastructure with endpoint-specific configuration.

**Implementation Pattern**:

```python
# Extend existing rate_limit.py
CHAT_RATE_LIMIT = 10  # messages per minute
CHAT_RATE_WINDOW = 60  # seconds

# Apply to chat endpoint specifically
@app.post("/api/{user_id}/chat")
@rate_limit(limit=CHAT_RATE_LIMIT, window=CHAT_RATE_WINDOW)
async def chat(user_id: str, request: ChatRequest, user: ValidatedUser):
    ...
```

**Key Findings**:
- Existing `rate_limit.py` uses in-memory sliding window — sufficient for hackathon
- Chat-specific limit (10/min) is stricter than general API limit (100/min)
- Rate limit response includes `Retry-After` header per FR-010a
- Per-user tracking via JWT user_id, not IP address

---

## Summary of Technology Decisions

| Decision | Choice | Key Rationale |
|----------|--------|---------------|
| LLM Gateway | OpenRouter via `set_default_openai_client()` | Model flexibility, OpenAI-compatible API |
| Agent Framework | OpenAI Agents SDK | Official SDK, tool calling, MCP integration |
| MCP Server | Standalone FastMCP over Streamable HTTP | Full protocol compliance, separation of concerns |
| Frontend Chat | OpenAI ChatKit with custom backend | Production-ready UI, hackathon speed |
| Background Jobs | APScheduler AsyncIOScheduler | Single-process, asyncio-native |
| Push Notifications | pywebpush + Service Worker | Standard Web Push, VAPID-based |
| Rate Limiting | Extended Phase II sliding window | Reuse existing infrastructure |
| Context Window | 7 messages from DB | Balance cost vs context quality |
| Delete Semantics | Hard delete | User-confirmed, spec clarification |
| LLM Failure | Friendly error, no retry | Spec clarification |
