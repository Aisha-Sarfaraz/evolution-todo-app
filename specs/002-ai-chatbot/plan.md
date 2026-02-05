# Implementation Plan: AI-Powered Conversational Todo Management

**Branch**: `002-ai-chatbot` | **Date**: 2026-01-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/002-ai-chatbot/spec.md`

---

## Summary

Phase III transforms the Todo application into a natural-language-driven AI system. Users interact exclusively through a chat interface (replacing the Phase II dashboard) to manage tasks conversationally. The system uses a standalone MCP server for tool execution, OpenAI Agents SDK for AI orchestration routed through OpenRouter for model flexibility, and database-backed conversation memory with a 7-message context window. Advanced features include recurring tasks with natural language recurrence parsing, due date reminders with browser push notifications, and batch operations.

Phase III code lives in a new `phase-3/` directory with its own `frontend/` and `backend/` subdirectories, extending and importing from Phase II code where appropriate (database models, auth dependencies, middleware).

---

## Technical Context

**Language/Version**: Python 3.13+ (backend, MCP server, agent) / TypeScript (frontend)
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, MCP SDK (FastMCP), OpenRouter API, OpenAI ChatKit, APScheduler, pywebpush
**Storage**: Neon PostgreSQL (extending Phase II schema with 5 new tables + 1 column)
**Testing**: pytest (unit + integration), Vitest (frontend), Playwright (E2E)
**Target Platform**: Web application (Vercel frontend, Railway/Render backend)
**Project Type**: Web (frontend + backend + MCP server)
**Performance Goals**: Chat response p95 < 3s, conversation history load < 1s, tool execution p95 < 2s
**Constraints**: Stateless backend, 7-message context window, 10 msg/min rate limit, single-process scheduler
**Scale/Scope**: 20 concurrent users, hackathon scope

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | PASS | spec.md approved with 60+ FRs, 15 SCs, 5 user stories |
| II. No Manual Coding | PASS | All code generated via Claude Code + SpecKit Plus |
| III. Test-Driven Development | PASS | TDD mandate enforced — tests before code |
| IV. Clean Separation of Concerns | PASS | MCP server (tools) / Agent (AI) / FastAPI (API) / ChatKit (UI) — clear layer boundaries |
| V. Code Modularity & Reusability | PASS | MCP tools are domain-agnostic, agent is configurable |
| VI. Security, Isolation & Observability | PASS | JWT auth reused, user_id filtering on all queries, structured logging |
| VII. Code Quality | PASS | PEP 8, type hints, docstrings enforced |
| VIII. Performance Standards | PASS | Async patterns, connection pooling, N+1 prevention |

**Post-Design Re-Check**: All gates continue to pass. Standalone MCP server adds a process boundary that strengthens separation of concerns (Principle IV). Stateless architecture ensures scalability alignment with Phase IV/V.

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    Browser                           │
│  ┌────────────────────────────────────────────────┐  │
│  │  Next.js 16 + OpenAI ChatKit                   │  │
│  │  (phase-3/frontend/)                           │  │
│  │  - Chat UI (messages, input, typing indicator) │  │
│  │  - Conversation sidebar                        │  │
│  │  - Service Worker (push notifications)         │  │
│  └──────────────────┬─────────────────────────────┘  │
└─────────────────────┼────────────────────────────────┘
                      │ HTTPS (Bearer JWT)
                      ▼
┌─────────────────────────────────────────────────────┐
│               FastAPI Backend                        │
│               (phase-3/backend/)                     │
│  ┌────────────────────────────────────────────────┐  │
│  │  Chat Router (/api/{user_id}/chat)             │  │
│  │  - Auth validation (ValidatedUser from P2)     │  │
│  │  - Rate limiting (10 msg/min)                  │  │
│  │  - Conversation management                     │  │
│  │  - Context loading (7 messages)                │  │
│  │  - Agent invocation                            │  │
│  │  - Response storage                            │  │
│  ├────────────────────────────────────────────────┤  │
│  │  Conversation Router (list, messages, delete)  │  │
│  ├────────────────────────────────────────────────┤  │
│  │  Push Router (subscribe, unsubscribe)          │  │
│  ├────────────────────────────────────────────────┤  │
│  │  APScheduler (recurrence + reminders)          │  │
│  └──────────────────┬─────────────────────────────┘  │
└─────────────────────┼────────────────────────────────┘
                      │ Agent SDK → MCPServerStreamableHttp
                      ▼
┌─────────────────────────────────────────────────────┐
│         Standalone MCP Server (FastMCP)              │
│         (phase-3/backend/src/mcp/)                   │
│  Port 8001, Streamable HTTP transport               │
│  ┌────────────────────────────────────────────────┐  │
│  │  Tools:                                        │  │
│  │  - create_task, list_tasks, update_task        │  │
│  │  - complete_task, delete_task                  │  │
│  │  - create_recurrence, update_recurrence        │  │
│  │  - remove_recurrence, set_due_date             │  │
│  └──────────────────┬─────────────────────────────┘  │
└─────────────────────┼────────────────────────────────┘
                      │ asyncpg
                      ▼
┌─────────────────────────────────────────────────────┐
│            Neon PostgreSQL                           │
│  Phase II tables + 5 new tables + 1 column          │
│  conversations, messages, recurrence_rules,          │
│  reminder_metadata, push_subscriptions               │
└─────────────────────────────────────────────────────┘
                      ▲
                      │ OpenRouter API (HTTPS)
┌─────────────────────┴───────────────────────────────┐
│              OpenRouter LLM Gateway                  │
│  Configurable model via OPENROUTER_MODEL env var    │
└─────────────────────────────────────────────────────┘
```

**Key Architectural Decisions**:

1. **Standalone MCP Server**: Separate process for MCP tools, connected via Streamable HTTP. Enables independent scaling, testing, and MCP protocol compliance.
2. **Stateless Backend**: All state in PostgreSQL. No in-memory sessions. Server can restart without data loss.
3. **Chat-Only UI**: ChatKit replaces Phase II dashboard as sole interface. Phase II API routes remain operational (consumed by MCP tools).
4. **Agent as Orchestrator**: OpenAI Agents SDK Agent receives user messages, decides which MCP tools to invoke, and generates natural language responses.
5. **Phase-3 Directory**: New `phase-3/` directory with `frontend/` and `backend/` subdirectories. Extends Phase II by importing shared code (database engine, auth dependencies, Task model) while keeping Phase III code cleanly separated.

---

## 2. Agent Architecture & Skill Composition

### Agent Definition

```python
agent = Agent(
    name="TodoAssistant",
    instructions=SYSTEM_PROMPT,
    model=os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
    mcp_servers=[mcp_server],
)
```

### System Prompt Design

The agent system prompt includes:
- **Role**: Helpful task management assistant
- **Capabilities**: Create, list, update, complete, delete tasks; manage recurrences; set due dates and reminders
- **Behavioral Rules**:
  - Always confirm before destructive operations (delete, remove recurrence)
  - Ask for clarification when task reference is ambiguous
  - Redirect off-topic messages politely
  - Never mutate data without tool invocation
  - Confirm interpreted dates with user before committing
- **Output Format**: Conversational language, not JSON. Action confirmations included naturally.
- **Tool Selection Guidelines**: When to use each tool based on user intent patterns

### MCP Tool Composition

9 tools organized by domain:

| Category | Tools | Priority |
|----------|-------|----------|
| Core CRUD | `create_task`, `list_tasks`, `update_task`, `complete_task`, `delete_task` | P1 |
| Recurrence | `create_recurrence`, `update_recurrence`, `remove_recurrence` | P3 |
| Due Dates | `set_due_date` | P4 |

### Agent Execution Flow

```
1. User sends message
2. FastAPI loads conversation context (last 7 messages)
3. FastAPI creates Agent with MCP server connection
4. Runner.run(agent, messages=context + [new_message])
5. Agent decides tool invocations (0 or more)
6. MCP server executes tools against database
7. Agent generates natural language response
8. FastAPI stores user message + assistant response
9. Response returned to frontend
```

---

## 3. MCP Server Plan

### Server Structure

```
phase-3/backend/src/mcp/
├── __init__.py
├── server.py          # FastMCP server definition and tool registrations
├── tools/
│   ├── __init__.py
│   ├── task_tools.py  # create, list, update, complete, delete
│   ├── recurrence_tools.py  # create, update, remove recurrence
│   └── reminder_tools.py    # set_due_date
└── database.py        # MCP server's own database session management
```

### Tool Design Principles

1. **Stateless**: Each tool receives all required context as parameters (including `user_id`)
2. **User-Isolated**: All database queries filter by `user_id`
3. **Validated**: Input validation via Python type hints (FastMCP generates JSON Schema)
4. **Logged**: Every tool invocation logged with user_id, tool name, input, output, duration (FR-019)
5. **Timeout**: 10-second timeout per tool invocation (FR-020)

### MCP Server Configuration

```python
mcp = FastMCP(
    "TodoMCP",
    host="0.0.0.0",
    port=int(os.environ.get("MCP_PORT", "8001")),
)
```

**Environment Variables**:
- `MCP_PORT`: Server port (default: 8001)
- `DATABASE_URL`: PostgreSQL connection string (shared with backend)

### Tool-to-FR Traceability

| Tool | Functional Requirements |
|------|------------------------|
| `create_task` | FR-011, FR-016, FR-017, FR-018 |
| `list_tasks` | FR-012, FR-016, FR-029, FR-039 |
| `update_task` | FR-013, FR-016, FR-017 |
| `complete_task` | FR-014, FR-016 |
| `delete_task` | FR-015, FR-016, FR-017 |
| `create_recurrence` | FR-021, FR-022, FR-026 |
| `update_recurrence` | FR-023, FR-026 |
| `remove_recurrence` | FR-024 |
| `set_due_date` | FR-031, FR-032, FR-040 |

---

## 4. Backend (FastAPI) Plan

### Phase II Code Reuse Strategy

Phase III backend (`phase-3/backend/`) extends Phase II by:
- **Importing** Phase II database engine, connection pool, and session factory
- **Importing** Phase II auth dependencies (`ValidatedUser`, `get_current_user`)
- **Importing** Phase II Task model (and extending it with `due_date` via migration)
- **Importing** Phase II rate limiter middleware (extending with chat-specific limits)
- **New routers** for chat, conversations, and push subscriptions

```python
# phase-3/backend/src/main.py
import sys
sys.path.insert(0, "../../phase-2/backend")  # Or use package install

from phase2.database import get_db, engine  # Reuse database
from phase2.api.dependencies import ValidatedUser  # Reuse auth
from phase2.models.task import Task  # Reuse Task model
```

### New Routers

```
phase-3/backend/src/api/routes/
├── chat.py              # POST /api/{user_id}/chat
├── conversations.py     # GET list, GET messages, DELETE
└── push.py              # POST subscribe, DELETE unsubscribe
```

### Chat Router (`chat.py`)

**POST /api/{user_id}/chat** — Core chat endpoint:

```python
@router.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    request: ChatRequest,
    user: ValidatedUser,
    db: AsyncSession = Depends(get_db),
):
    # 1. Load or create conversation
    # 2. Store user message
    # 3. Load context (last 7 messages)
    # 4. Connect to MCP server
    # 5. Create Agent + Runner.run()
    # 6. Extract response + tool_calls
    # 7. Store assistant message
    # 8. Update conversation.updated_at
    # 9. Return ChatResponse
```

### Request/Response Schemas (Pydantic)

```python
class ChatRequest(BaseModel):
    conversation_id: uuid.UUID | None = None
    message: str = Field(min_length=1, max_length=5000)
    timezone: str | None = None

class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    response: str
    tool_calls: list[ToolCallInfo]

class ToolCallInfo(BaseModel):
    tool: str
    input: dict
    output: dict
    duration_ms: int | None = None
```

### Rate Limiting

Extend Phase II `rate_limit.py` middleware:
- Add endpoint-specific rate limit configuration
- Chat endpoint: 10 msg/min (FR-010a)
- General API: 100 req/min (existing)

### LLM Error Handling (FR-010b)

```python
try:
    result = await Runner.run(agent, messages=context)
except Exception as e:
    logger.error(f"LLM error for user {user_id}: {e}")
    return ChatResponse(
        conversation_id=conv_id,
        response="I'm temporarily unable to respond. Please try again in a moment.",
        tool_calls=[],
    )
```

### Dependencies Reused from Phase II

- `ValidatedUser`: JWT validation + user_id match
- `get_db`: Async database session
- `get_current_user`: JWT token parsing
- Rate limiter middleware
- CORS configuration

---

## 5. Database & Persistence Strategy

### Schema Summary

See [data-model.md](./data-model.md) for complete entity definitions.

**New Tables** (6 Alembic migrations):

| # | Migration | Description |
|---|-----------|-------------|
| 009 | `create_conversations_table` | Conversations with user ownership |
| 010 | `create_messages_table` | Messages with role, content, tool_calls |
| 011 | `create_recurrence_rules_table` | Recurrence rules with frequency, interval, next_occurrence |
| 012 | `create_reminder_metadata_table` | Due dates, reminder times, notification tracking |
| 013 | `create_push_subscriptions_table` | Browser push subscription storage |
| 014 | `add_due_date_to_tasks` | Add due_date column + index to tasks |

### Database Access Patterns

| Pattern | Query | Index Used |
|---------|-------|-----------|
| Context window | 7 most recent messages by conversation | `(conversation_id, created_at DESC)` |
| User conversations | All conversations sorted by activity | `(user_id, updated_at DESC)` |
| Due recurrences | Rules where next_occurrence <= NOW() | `next_occurrence` |
| Pending reminders | Unsent reminders where time arrived | `(reminder_time, notification_sent)` |
| Overdue tasks | Tasks with past due_date, still pending | `(user_id, due_date)` |
| User isolation | All queries filter by user_id | `user_id` on all tables |

### Connection Management

- **FastAPI backend**: Reuse Phase II async engine + connection pool (5-20 connections)
- **MCP server**: Separate async engine + pool (MCP runs as independent process)
- **APScheduler jobs**: Create dedicated sessions per job execution (avoid connection leaks)

### Alembic Migration Strategy

Alembic migrations live in `phase-2/backend/alembic/versions/` (single migration history for the shared database). Phase III migrations extend the existing chain.

---

## 6. Frontend (ChatKit) Plan

### Page Structure

```
phase-3/frontend/
├── app/
│   ├── page.tsx              # Redirect to /chat
│   ├── chat/
│   │   ├── page.tsx          # Main chat page (ChatKit)
│   │   └── layout.tsx        # Chat layout with sidebar
│   ├── api/
│   │   └── chat/
│   │       └── route.ts      # Proxy to FastAPI backend
│   └── (auth pages — reuse or redirect to Phase II)
├── components/
│   ├── chat/
│   │   ├── ChatContainer.tsx     # ChatKit provider wrapper
│   │   ├── ConversationList.tsx  # Sidebar conversation list
│   │   ├── ToolCallDisplay.tsx   # Visual tool call confirmations
│   │   └── NotificationBanner.tsx # In-app notification fallback
│   └── ui/                       # Shared UI components
├── lib/
│   ├── push.ts               # Push notification subscription logic
│   ├── api.ts                # API client for backend
│   └── auth.ts               # Auth session management (extends Phase II)
├── public/
│   └── sw.js                  # Service Worker for push notifications
├── __tests__/
│   ├── components/
│   │   ├── ChatContainer.test.tsx
│   │   ├── ConversationList.test.tsx
│   │   ├── ToolCallDisplay.test.tsx
│   │   └── NotificationBanner.test.tsx
│   ├── lib/
│   │   ├── push.test.ts
│   │   └── api.test.ts
│   └── e2e/
│       ├── chat-flow.spec.ts         # Full conversation E2E
│       ├── conversation-crud.spec.ts  # Conversation list CRUD E2E
│       └── notifications.spec.ts      # Push notification E2E
├── package.json
├── tsconfig.json
├── vitest.config.ts           # Vitest configuration for unit tests
├── playwright.config.ts       # Playwright configuration for E2E tests
└── .gitignore
```

### ChatKit Integration

```tsx
// app/chat/page.tsx
import { ChatProvider, ChatMessages, ChatInput } from "@openai/chatkit";

export default function ChatPage() {
  const { session } = useSession();

  return (
    <div className="flex h-screen">
      <ConversationList />
      <div className="flex-1 flex flex-col">
        <ChatProvider
          backendUrl="/api/chat"
          headers={{
            Authorization: `Bearer ${session.token}`,
          }}
        >
          <ChatMessages />
          <ChatInput placeholder="Tell me what you'd like to do..." />
        </ChatProvider>
      </div>
    </div>
  );
}
```

### Next.js API Route (Proxy)

```typescript
// app/api/chat/route.ts
export async function POST(request: Request) {
  const token = request.headers.get("Authorization");
  const body = await request.json();

  const response = await fetch(`${BACKEND_URL}/api/${userId}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: token,
    },
    body: JSON.stringify(body),
  });

  return new Response(response.body, {
    headers: response.headers,
  });
}
```

### Frontend Testing Strategy

**Unit Tests (Vitest)**:
- Component rendering and interaction tests
- API client function tests
- Push notification subscription logic tests
- Mock ChatKit provider for isolated testing

**E2E Tests (Playwright)**:
- Full chat conversation flow (send message, receive response)
- Conversation CRUD (create, list, switch, delete)
- Push notification permission flow
- Authentication and session persistence

### Push Notification Flow

1. User visits chat page → prompt for notification permission (FR-058)
2. If granted → register Service Worker, get PushSubscription
3. Send subscription to `POST /api/{user_id}/push/subscribe`
4. When reminder triggers → server sends push via `pywebpush`
5. Service Worker receives push event → displays browser notification
6. If permission denied → in-app banner fallback (FR-037)

---

## 7. Advanced Intelligent Features Plan

### Recurring Tasks (P3)

**Natural Language Parsing**:
The agent system prompt includes examples for recurrence pattern recognition:
- "every day" → frequency=daily, interval=1
- "every other week" → frequency=weekly, interval=2
- "every Monday and Friday" → frequency=weekly, days_of_week=[0, 4]
- "on the 1st of every month" → frequency=monthly, day_of_month=1
- "every 3 days until March 15" → frequency=daily, interval=3, end_date=2026-03-15

**Background Scheduler**:
- APScheduler `check_recurrence` job runs every 1 minute
- Queries `recurrence_rules` where `next_occurrence <= NOW()`
- For each due rule: creates new task instance, calculates next occurrence
- Handles month-end edge cases (FR-027): clamp day_of_month to last day of month

**Next Occurrence Calculation**:

```python
def calculate_next_occurrence(rule: RecurrenceRule, from_date: datetime) -> datetime:
    match rule.frequency:
        case "daily":
            return from_date + timedelta(days=rule.interval)
        case "weekly":
            # Find next matching day_of_week
            ...
        case "monthly":
            # Add months, handle day_of_month clamping
            ...
        case "yearly":
            return from_date.replace(year=from_date.year + rule.interval)
```

### Due Dates & Reminders (P4)

**Date Parsing Strategy**:
The agent interprets natural language dates via its LLM capability. The system prompt includes:
- Relative references: "tomorrow", "in 2 hours", "next Friday"
- Absolute references: "March 15", "Friday at 5pm", "end of month"
- Confirmation rule: Agent must confirm ambiguous dates before committing

**Reminder Delivery**:
- APScheduler `check_reminders` job runs every 1 minute
- Queries `reminder_metadata` where `reminder_time <= NOW() AND notification_sent = FALSE`
- For each due reminder: sends push notification, marks `notification_sent = TRUE`
- Notification batching: max 3 individual notifications per minute per user

### Advanced NL Understanding (P5)

**Batch Operations**: Agent system prompt includes patterns for:
- "add tasks X, Y, and Z" → multiple `create_task` calls
- "mark all of those as done" → reference previous listing context
- "show high priority pending tasks" → compound filters

**Contextual References**: Agent uses 7-message context window to resolve:
- "the task I mentioned" → scan recent messages for task references
- "like I said about groceries" → find groceries mention in context
- "mark all of those as done" → reference last list_tasks result

**Off-Topic Handling**: Agent system prompt includes redirect behavior:
- Non-task messages → "I'm your task assistant. I can help you add, view, update, or complete tasks."

---

## 8. Testing & Quality Strategy

### Test Structure

```
phase-3/backend/tests/
├── conftest.py                    # Shared fixtures
├── unit/
│   ├── test_chat_service.py       # Chat orchestration logic
│   ├── test_recurrence_calc.py    # Next occurrence calculations
│   └── test_reminder_service.py   # Reminder checking logic
├── integration/
│   ├── test_chat_api.py           # Chat endpoint integration
│   ├── test_conversation_api.py   # Conversation CRUD
│   ├── test_push_api.py           # Push subscription
│   └── test_mcp_tools.py         # MCP tool execution against DB
└── e2e/
    └── test_chat_flow.py          # Full conversation flows

phase-3/frontend/__tests__/
├── components/
│   ├── ChatContainer.test.tsx     # ChatKit wrapper rendering
│   ├── ConversationList.test.tsx  # Sidebar component tests
│   ├── ToolCallDisplay.test.tsx   # Tool call visual display
│   └── NotificationBanner.test.tsx # In-app notification fallback
├── lib/
│   ├── push.test.ts               # Push subscription logic
│   └── api.test.ts                # API client functions
└── e2e/
    ├── chat-flow.spec.ts          # Full conversation E2E (Playwright)
    ├── conversation-crud.spec.ts  # Conversation list CRUD E2E
    └── notifications.spec.ts      # Push notification flow E2E
```

### Coverage Requirements

| Layer | Target | Focus |
|-------|--------|-------|
| MCP Tools (unit) | 80% | Input validation, user isolation, error handling |
| Chat Service (unit) | 80% | Context loading, agent invocation, response storage |
| Recurrence Calc (unit) | 90% | All frequency types, edge cases (month-end, Feb 29) |
| API Integration | 70% | Auth, rate limiting, error responses, CRUD flows |
| MCP Integration | 70% | Tool execution against real database |
| Frontend Components | 80% | Rendering, user interactions, state management |
| Frontend E2E | Critical paths | Chat flow, conversation CRUD, notifications |

### TDD Workflow per Feature

1. **Red**: Write failing test defining expected behavior
2. **Green**: Implement minimal code to pass
3. **Refactor**: Improve while tests stay green

Example sequence for `create_task` MCP tool:
1. Test: `test_create_task_returns_task_with_id` → RED
2. Implement tool → GREEN
3. Test: `test_create_task_validates_empty_title` → RED
4. Add validation → GREEN
5. Test: `test_create_task_filters_by_user_id` → RED
6. Add user isolation → GREEN

Example sequence for `ChatContainer` frontend component:
1. Test: `renders_chat_messages_in_order` → RED
2. Implement ChatContainer → GREEN
3. Test: `displays_typing_indicator_while_loading` → RED
4. Add loading state → GREEN
5. Test: `shows_tool_call_confirmation` → RED
6. Add ToolCallDisplay → GREEN

### Key Test Scenarios

| Scenario | Type | Layer | FR Coverage |
|----------|------|-------|-------------|
| Chat creates task from NL | Integration | Backend | FR-001, FR-011, FR-041 |
| Rate limit blocks 11th message | Integration | Backend | FR-010a |
| LLM failure returns friendly error | Integration | Backend | FR-010b |
| Context window loads 7 messages | Unit | Backend | FR-004 |
| User A cannot see User B conversations | Integration | Backend | FR-005 |
| Recurrence creates next instance | Unit | Backend | FR-025, FR-026 |
| Monthly recurrence handles Feb 31 | Unit | Backend | FR-027 |
| Push notification sent on reminder | Integration | Backend | FR-034 |
| Delete task requires confirmation | E2E | Frontend | FR-046 |
| Batch task creation | E2E | Frontend | FR-043 |
| Chat messages render chronologically | Unit | Frontend | FR-051 |
| Typing indicator shows during response | Unit | Frontend | FR-053 |
| Conversation list shows recent activity | Unit | Frontend | FR-060 |
| Auto-scroll on new message | Unit | Frontend | FR-054 |
| Service worker receives push | E2E | Frontend | FR-059 |

---

## 9. Non-Functional Requirements

### Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Chat response time | p95 < 3s | FastAPI middleware timing |
| Conversation history load | < 1s for 500 messages | Frontend performance test |
| MCP tool execution | p95 < 2s | Tool invocation logging |
| Context window query | < 100ms | Database query monitoring |
| Concurrent users | 20 without degradation | Load test (Locust) |

### Security

| Requirement | Implementation |
|-------------|---------------|
| Authentication | JWT validation on every request (Phase II `ValidatedUser`) |
| User isolation | `user_id` filter on all database queries + MCP tool parameters |
| Input validation | Pydantic models for API, type hints for MCP tools |
| Rate limiting | 10 msg/min chat, 100 req/min general API |
| Secret management | All keys in env vars, never in code |
| SQL injection prevention | SQLModel ORM, parameterized queries |
| No data exposure | LLM errors return generic message, no stack traces |

### Reliability

| Requirement | Implementation |
|-------------|---------------|
| Stateless backend | All state in PostgreSQL, server restartable |
| Conversation persistence | Messages stored before response returned |
| Duplicate notification prevention | `notification_sent` boolean flag |
| Graceful LLM failure | Friendly error message, no retry (FR-010b) |
| Scheduler resilience | APScheduler with missed job handling |

### Observability

| Component | Logging |
|-----------|---------|
| Chat endpoint | Request/response timing, user_id, conversation_id |
| MCP tools | Tool name, input, output, duration, success/failure (FR-019) |
| Agent | Token usage per request (FR-049) |
| Scheduler | Job execution time, tasks created, reminders sent |
| Errors | Structured JSON logs with context |

---

## 10. Risk & Mitigation Plan

| # | Risk | Impact | Probability | Mitigation |
|---|------|--------|-------------|------------|
| 1 | OpenRouter API latency spikes | Chat response exceeds 3s SLA | Medium | Configurable model selection (switch to faster model), timeout with friendly error |
| 2 | MCP server process crashes | All tool invocations fail | Low | Health check monitoring, FastAPI error handling returns friendly message, process supervisor (systemd/pm2) |
| 3 | ChatKit API changes or deprecation | Frontend breaks | Low | Pin ChatKit version, abstract ChatKit usage behind wrapper component |
| 4 | Token cost exceeds budget | Unsustainable operation cost | Medium | Token usage logging (FR-049), configurable model via env var, rate limiting |
| 5 | APScheduler misses jobs during restart | Recurrence/reminder delays | Medium | Scheduler checks for overdue rules on startup (catch-up logic) |
| 6 | Browser push subscription expires | Missed notifications | Low | Handle 410 Gone, clean up stale subscriptions, in-app fallback |
| 7 | Context window too small for complex conversations | AI loses context, poor UX | Low | 7 messages is configurable; increase if needed post-launch |
| 8 | Phase II import compatibility | Module import issues between phase-2/ and phase-3/ | Medium | Shared pyproject.toml dependency management, integration tests for cross-phase imports |

---

## Project Structure

### Documentation (this feature)

```text
specs/002-ai-chatbot/
├── spec.md              # Feature specification (approved)
├── plan.md              # This file
├── research.md          # Phase 0 technology research
├── data-model.md        # Entity schemas and relationships
├── quickstart.md        # Developer setup guide
├── contracts/
│   └── chat-api.md      # API endpoint contracts
├── checklists/
│   └── requirements.md  # Specification quality checklist
└── tasks.md             # (future: /sp.tasks output)
```

### Source Code (repository root)

```text
phase-3/
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPI app (imports Phase II deps)
│   │   ├── api/routes/
│   │   │   ├── chat.py          # Chat endpoint
│   │   │   ├── conversations.py # Conversation CRUD
│   │   │   └── push.py          # Push subscription
│   │   ├── mcp/
│   │   │   ├── server.py        # FastMCP standalone server
│   │   │   ├── tools/
│   │   │   │   ├── task_tools.py
│   │   │   │   ├── recurrence_tools.py
│   │   │   │   └── reminder_tools.py
│   │   │   └── database.py      # MCP database sessions
│   │   ├── models/
│   │   │   ├── conversation.py  # Conversation + Message models
│   │   │   ├── recurrence.py    # RecurrenceRule model
│   │   │   ├── reminder.py      # ReminderMetadata model
│   │   │   └── push_subscription.py
│   │   ├── services/
│   │   │   ├── chat_service.py  # Chat orchestration
│   │   │   ├── recurrence_service.py
│   │   │   └── reminder_service.py
│   │   ├── scheduler/
│   │   │   └── jobs.py          # APScheduler job definitions
│   │   └── agent/
│   │       ├── config.py        # Agent + OpenRouter config
│   │       └── prompts.py       # System prompt definitions
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   └── pyproject.toml           # Dependencies (extends Phase II)
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── chat/
│   │   │   ├── page.tsx
│   │   │   └── layout.tsx
│   │   └── api/chat/route.ts
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatContainer.tsx
│   │   │   ├── ConversationList.tsx
│   │   │   ├── ToolCallDisplay.tsx
│   │   │   └── NotificationBanner.tsx
│   │   └── ui/
│   ├── lib/
│   │   ├── push.ts
│   │   ├── api.ts
│   │   └── auth.ts
│   ├── public/sw.js
│   ├── __tests__/
│   │   ├── components/
│   │   │   ├── ChatContainer.test.tsx
│   │   │   ├── ConversationList.test.tsx
│   │   │   ├── ToolCallDisplay.test.tsx
│   │   │   └── NotificationBanner.test.tsx
│   │   ├── lib/
│   │   │   ├── push.test.ts
│   │   │   └── api.test.ts
│   │   └── e2e/
│   │       ├── chat-flow.spec.ts
│   │       ├── conversation-crud.spec.ts
│   │       └── notifications.spec.ts
│   ├── package.json
│   ├── vitest.config.ts
│   ├── playwright.config.ts
│   └── .gitignore
│
└── README.md                    # Phase III setup instructions

phase-2/backend/alembic/versions/
├── (existing migrations 001-008)
├── 009_create_conversations_table.py
├── 010_create_messages_table.py
├── 011_create_recurrence_rules_table.py
├── 012_create_reminder_metadata_table.py
├── 013_create_push_subscriptions_table.py
└── 014_add_due_date_to_tasks.py
```

**Structure Decision**: New `phase-3/` directory with `frontend/` and `backend/` subdirectories. Phase III backend imports Phase II shared code (database, auth, Task model). Alembic migrations remain in `phase-2/backend/alembic/` for single migration history against the shared database.

---

## Complexity Tracking

| Complexity | Why Needed | Simpler Alternative Rejected Because |
|------------|------------|-------------------------------------|
| Standalone MCP server (separate process) | Full MCP protocol compliance per spec, enables independent testing and scaling | In-process function tools would be simpler but violate spec MCP requirements |
| APScheduler in-process | Recurrence/reminder scheduling required by FR-025, FR-033 | No scheduler = no automatic recurrence/reminders. Celery too heavy for hackathon. |
| Push notifications (Service Worker + pywebpush) | FR-034 requires browser notifications | In-app only would miss notifications when tab not focused |
| Separate phase-3/ directory | Clean separation between phases, independent frontend/backend | Extending phase-2/ in-place would mix Phase II and III code, complicating maintenance |
