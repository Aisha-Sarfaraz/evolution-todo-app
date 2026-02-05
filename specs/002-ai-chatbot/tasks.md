# Tasks: AI-Powered Conversational Todo Management

**Input**: Design documents from `/specs/002-ai-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/chat-api.md

**Tests**: Tests are MANDATORY per Constitution Principle III (TDD NON-NEGOTIABLE). All tasks MUST include test tasks following Red-Green-Refactor cycle. Tests MUST be written FIRST and FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `phase-3/backend/src/`
- **Backend tests**: `phase-3/backend/tests/`
- **Frontend**: `phase-3/frontend/`
- **Frontend tests**: `phase-3/frontend/__tests__/`
- **Alembic migrations**: `phase-2/backend/alembic/versions/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, directory structure, and dependency management for phase-3/

- [x] T001 Create phase-3/ directory structure per plan.md — `phase-3/backend/src/`, `phase-3/backend/tests/`, `phase-3/frontend/` with all subdirectories (api/routes, mcp/tools, models, services, scheduler, agent, components/chat, lib, __tests__)
- [x] T002 Initialize phase-3/backend Python project with pyproject.toml — dependencies: fastapi, openai-agents, mcp, apscheduler, pywebpush, py-vapid, asyncpg, sqlmodel, pydantic in `phase-3/backend/pyproject.toml`
- [x] T003 [P] Initialize phase-3/frontend Next.js 16 project with package.json — dependencies: @openai/chatkit, next, react, better-auth, tailwindcss, vitest, playwright in `phase-3/frontend/package.json`
- [x] T004 [P] Create .env.example files for backend and frontend with all required environment variables in `phase-3/backend/.env.example` and `phase-3/frontend/.env.example`
- [x] T005 [P] Configure Vitest for frontend unit tests in `phase-3/frontend/vitest.config.ts`
- [x] T006 [P] Configure Playwright for frontend E2E tests in `phase-3/frontend/playwright.config.ts`
- [x] T007 [P] Configure pytest with markers (unit, integration, e2e) and conftest in `phase-3/backend/tests/conftest.py`
- [x] T008 [P] Configure ruff, black, and mypy for backend code quality in `phase-3/backend/pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundation (REQUIRED - TDD NON-NEGOTIABLE)

- [x] T009 [P] Write unit test for OpenRouter client configuration (set_default_openai_client) in `phase-3/backend/tests/unit/test_agent_config.py`
- [x] T010 [P] Write unit test for MCP server database session management in `phase-3/backend/tests/unit/test_mcp_database.py`
- [x] T011 [P] Write integration test for Phase II import compatibility (database engine, auth deps, Task model) in `phase-3/backend/tests/integration/test_phase2_imports.py`

### Implementation for Foundation

- [x] T012 Configure Phase II code import strategy — add sys.path or package install for phase-2/backend shared code (database.py, dependencies.py, models/task.py) in `phase-3/backend/src/__init__.py`
- [x] T013 [P] Create MCP server database session management with independent async engine and connection pool in `phase-3/backend/src/mcp/database.py`
- [x] T014 [P] Create Agent + OpenRouter configuration module — set_default_openai_client with AsyncOpenAI(base_url=openrouter), model from OPENROUTER_MODEL env var in `phase-3/backend/src/agent/config.py`
- [x] T015 [P] Create agent system prompt module with TodoAssistant role, capabilities, behavioral rules (confirm destructive ops, disambiguate, redirect off-topic, confirm dates) in `phase-3/backend/src/agent/prompts.py`
- [x] T016 Create Alembic migration 009 — conversations table (id UUID PK, user_id FK, title, created_at, updated_at) with indexes in `phase-2/backend/alembic/versions/009_create_conversations_table.py`
- [x] T017 Create Alembic migration 010 — messages table (id UUID PK, conversation_id FK CASCADE, user_id, role CHECK, content TEXT, tool_calls JSONB, created_at) with composite index in `phase-2/backend/alembic/versions/010_create_messages_table.py`
- [x] T018 [P] Create Conversation SQLModel in `phase-3/backend/src/models/conversation.py`
- [x] T019 [P] Create Message SQLModel in `phase-3/backend/src/models/message.py`
- [x] T020 Create FastAPI application entry point with CORS, lifespan, and Phase II dependency imports in `phase-3/backend/src/main.py`
- [x] T021 [P] Create frontend .gitignore in `phase-3/frontend/.gitignore`

**Checkpoint**: Foundation ready — database tables created, agent configured, Phase II imports working, user story implementation can begin

---

## Phase 3: User Story 1 — Natural Language Task CRUD (Priority: P1) MVP

**Goal**: Authenticated users create, list, update, complete, and delete tasks through natural language conversation via the chat-only interface

**Independent Test**: User opens chat, types "add a task to buy groceries", AI creates task and confirms. User types "show my tasks", AI lists tasks. User types "mark groceries as done", AI completes task. User types "delete the groceries task", AI confirms and deletes. Full CRUD cycle via natural language.

### Tests for User Story 1 (REQUIRED - TDD NON-NEGOTIABLE)

- [x] T022 [P] [US1] Write unit tests for create_task MCP tool (valid input, empty title rejection, user isolation) in `phase-3/backend/tests/unit/test_task_tools.py`
- [x] T023 [P] [US1] Write unit tests for list_tasks MCP tool (status filter, priority filter, user isolation) in `phase-3/backend/tests/unit/test_task_tools.py`
- [x] T024 [P] [US1] Write unit tests for update_task, complete_task, delete_task MCP tools in `phase-3/backend/tests/unit/test_task_tools.py`
- [x] T025 [P] [US1] Write integration test for POST /api/{user_id}/chat endpoint (auth, message storage, response format) in `phase-3/backend/tests/integration/test_chat_api.py`
- [x] T026 [P] [US1] Write integration test for chat rate limiting (10 msg/min, 429 response, Retry-After header) in `phase-3/backend/tests/integration/test_chat_api.py`
- [x] T027 [P] [US1] Write integration test for LLM failure handling (503 response, friendly error message) in `phase-3/backend/tests/integration/test_chat_api.py`
- [x] T028 [P] [US1] Write frontend unit test for ChatContainer component rendering in `phase-3/frontend/__tests__/components/ChatContainer.test.tsx`
- [x] T029 [P] [US1] Write frontend unit test for ToolCallDisplay component in `phase-3/frontend/__tests__/components/ToolCallDisplay.test.tsx`

### Implementation for User Story 1

- [x] T030 [P] [US1] Implement create_task MCP tool with @mcp.tool() decorator, title/description/priority params, user_id isolation, input validation, 10s timeout in `phase-3/backend/src/mcp/tools/task_tools.py`
- [x] T031 [P] [US1] Implement list_tasks MCP tool with status/priority/search filters, user_id isolation in `phase-3/backend/src/mcp/tools/task_tools.py`
- [x] T032 [US1] Implement update_task, complete_task, delete_task (hard delete) MCP tools with user_id isolation, input validation in `phase-3/backend/src/mcp/tools/task_tools.py`
- [x] T033 [US1] Create FastMCP server definition registering all task CRUD tools, configure Streamable HTTP transport on MCP_PORT in `phase-3/backend/src/mcp/server.py`
- [x] T034 [US1] Implement tool invocation logging middleware — user_id, tool name, input, output, duration, success/failure per FR-019 in `phase-3/backend/src/mcp/server.py`
- [x] T035 [US1] Create ChatRequest/ChatResponse Pydantic schemas in `phase-3/backend/src/api/schemas/chat.py`
- [x] T036 [US1] Implement chat_service — conversation load/create, message storage, context window (7 messages), Agent invocation via MCPServerStreamableHttp, response extraction, tool_calls capture in `phase-3/backend/src/services/chat_service.py`
- [x] T037 [US1] Implement POST /api/{user_id}/chat route with ValidatedUser auth, rate limit (10 msg/min), LLM error handling (FR-010b) in `phase-3/backend/src/api/routes/chat.py`
- [x] T038 [US1] Extend Phase II rate limiter with endpoint-specific configuration (chat: 10/min) in `phase-3/backend/src/middleware/rate_limit.py`
- [x] T039 [US1] Register chat router in FastAPI app in `phase-3/backend/src/main.py`
- [x] T040 [P] [US1] Create ChatContainer component wrapping ChatKit ChatProvider with backendUrl and auth headers in `phase-3/frontend/components/chat/ChatContainer.tsx`
- [x] T041 [P] [US1] Create ToolCallDisplay component for visual tool call confirmations (task created, completed, etc.) in `phase-3/frontend/components/chat/ToolCallDisplay.tsx`
- [x] T042 [US1] Create main chat page with ChatContainer in `phase-3/frontend/app/chat/page.tsx`
- [x] T043 [US1] Create Next.js API route proxying to FastAPI backend with auth token forwarding in `phase-3/frontend/app/api/chat/route.ts`
- [x] T044 [US1] Create API client module for backend communication in `phase-3/frontend/lib/api.ts`
- [x] T045 [US1] Create auth session management module (extending Phase II Better Auth) in `phase-3/frontend/lib/auth.ts`

**Checkpoint**: User Story 1 complete — full CRUD via natural language chat. MVP deliverable.

---

## Phase 4: User Story 2 — Conversation Persistence & Context (Priority: P2)

**Goal**: Multi-turn conversations persist across browser sessions. Users resume where they left off. AI uses recent context (7 messages) for coherent interactions.

**Independent Test**: User starts conversation, creates 3 tasks, closes browser, reopens after 1 hour, conversation history visible, user continues with "show the tasks I added earlier", AI responds correctly.

### Tests for User Story 2 (REQUIRED - TDD NON-NEGOTIABLE)

- [x] T046 [P] [US2] Write integration test for GET /api/{user_id}/conversations (list, sort by recent, preview) in `phase-3/backend/tests/integration/test_conversation_api.py`
- [x] T047 [P] [US2] Write integration test for GET /api/{user_id}/conversations/{id}/messages (pagination, cursor, chronological order) in `phase-3/backend/tests/integration/test_conversation_api.py`
- [x] T048 [P] [US2] Write integration test for DELETE /api/{user_id}/conversations/{id} (cascade delete messages) in `phase-3/backend/tests/integration/test_conversation_api.py`
- [x] T049 [P] [US2] Write integration test for user isolation — User A cannot access User B conversations in `phase-3/backend/tests/integration/test_conversation_api.py`
- [x] T050 [P] [US2] Write frontend unit test for ConversationList component (render list, select conversation, new chat button) in `phase-3/frontend/__tests__/components/ConversationList.test.tsx`

### Implementation for User Story 2

- [x] T051 [US2] Implement GET /api/{user_id}/conversations route with user isolation, sorted by updated_at DESC, last_message_preview in `phase-3/backend/src/api/routes/conversations.py`
- [x] T052 [US2] Implement GET /api/{user_id}/conversations/{id}/messages route with cursor-based pagination (limit, before params), user isolation in `phase-3/backend/src/api/routes/conversations.py`
- [x] T053 [US2] Implement DELETE /api/{user_id}/conversations/{id} route with cascade delete, user isolation in `phase-3/backend/src/api/routes/conversations.py`
- [x] T054 [US2] Register conversations router in FastAPI app in `phase-3/backend/src/main.py`
- [x] T055 [US2] Create ConversationList sidebar component with conversation list, last message preview, timestamp, new chat button in `phase-3/frontend/components/chat/ConversationList.tsx`
- [x] T056 [US2] Create chat layout with sidebar and main chat area in `phase-3/frontend/app/chat/layout.tsx`
- [x] T057 [US2] Implement conversation switching — select conversation loads history, new chat creates fresh conversation in `phase-3/frontend/app/chat/page.tsx`
- [x] T058 [US2] Implement lazy loading of older messages on scroll-up in chat page in `phase-3/frontend/app/chat/page.tsx`

**Checkpoint**: User Story 2 complete — conversations persist, context window works, sidebar navigation functional.

---

## Phase 5: User Story 3 — Recurring Tasks (Priority: P3)

**Goal**: Users create recurring tasks using natural language (daily, weekly, monthly, custom intervals). System auto-creates new instances on schedule.

**Independent Test**: User types "remind me to take vitamins every day", AI creates recurring task. Background scheduler creates next daily instance. User types "stop the vitamins reminder", AI removes recurrence.

### Tests for User Story 3 (REQUIRED - TDD NON-NEGOTIABLE)

- [x] T059 [P] [US3] Write unit tests for recurrence calculation — daily, weekly, monthly, yearly, interval, month-end edge cases (Feb 31) in `phase-3/backend/tests/unit/test_recurrence_calc.py`
- [x] T060 [P] [US3] Write unit tests for create_recurrence, update_recurrence, remove_recurrence MCP tools in `phase-3/backend/tests/unit/test_recurrence_tools.py`
- [x] T061 [P] [US3] Write integration test for recurrence scheduler job — creates new task instance, updates next_occurrence in `phase-3/backend/tests/integration/test_scheduler.py`
- [x] T062 [P] [US3] Write unit test for end_date enforcement — stops creating instances after end_date in `phase-3/backend/tests/unit/test_recurrence_calc.py`

### Implementation for User Story 3

- [x] T063 [US3] Create Alembic migration 011 — recurrence_rules table (id, task_id UNIQUE FK CASCADE, frequency CHECK, interval, days_of_week ARRAY, day_of_month, end_date, next_occurrence INDEX) in `phase-2/backend/alembic/versions/011_create_recurrence_rules_table.py`
- [x] T064 [US3] Create RecurrenceRule SQLModel in `phase-3/backend/src/models/recurrence.py`
- [x] T065 [US3] Implement recurrence calculation service — calculate_next_occurrence for daily/weekly/monthly/yearly with month-end clamping in `phase-3/backend/src/services/recurrence_service.py`
- [x] T066 [US3] Implement create_recurrence, update_recurrence, remove_recurrence MCP tools with user_id isolation in `phase-3/backend/src/mcp/tools/recurrence_tools.py`
- [x] T067 [US3] Register recurrence tools in FastMCP server in `phase-3/backend/src/mcp/server.py`
- [x] T068 [US3] Implement APScheduler check_recurrence job — query due rules, create task instances, update next_occurrence in `phase-3/backend/src/scheduler/jobs.py`
- [x] T069 [US3] Configure APScheduler AsyncIOScheduler in FastAPI lifespan (start on startup, shutdown gracefully) in `phase-3/backend/src/main.py`
- [x] T070 [US3] Update agent system prompt with recurrence NL patterns (every day, every other week, on the 1st of every month, until date) in `phase-3/backend/src/agent/prompts.py`

**Checkpoint**: User Story 3 complete — recurring tasks created via NL, scheduler auto-creates instances, recurrence manageable.

---

## Phase 6: User Story 4 — Due Dates & Time Reminders (Priority: P4)

**Goal**: Users set due dates and reminders via natural language. Browser push notifications trigger at reminder time. Overdue tasks visually indicated.

**Independent Test**: User says "remind me tomorrow at 2pm to call the dentist", AI creates task with due date and reminder. Next day at 2pm, browser notification appears.

### Tests for User Story 4 (REQUIRED - TDD NON-NEGOTIABLE)

- [x] T071 [P] [US4] Write unit tests for set_due_date MCP tool (valid date, reminder_time, user isolation) in `phase-3/backend/tests/unit/test_reminder_tools.py`
- [x] T072 [P] [US4] Write unit tests for reminder checker service — finds due reminders, marks notification_sent, skips already-sent in `phase-3/backend/tests/unit/test_reminder_service.py`
- [x] T073 [P] [US4] Write integration test for push notification delivery via pywebpush in `phase-3/backend/tests/integration/test_push_api.py`
- [x] T074 [P] [US4] Write integration test for POST /api/{user_id}/push/subscribe endpoint in `phase-3/backend/tests/integration/test_push_api.py`
- [x] T075 [P] [US4] Write frontend unit test for NotificationBanner component (in-app fallback) in `phase-3/frontend/__tests__/components/NotificationBanner.test.tsx`
- [x] T076 [P] [US4] Write frontend unit test for push subscription logic in `phase-3/frontend/__tests__/lib/push.test.ts`

### Implementation for User Story 4

- [x] T077 [US4] Create Alembic migration 012 — reminder_metadata table (id, task_id UNIQUE FK CASCADE, due_date, reminder_time, notification_sent, snooze_until, CHECK constraint) with indexes in `phase-2/backend/alembic/versions/012_create_reminder_metadata_table.py`
- [x] T078 [US4] Create Alembic migration 013 — push_subscriptions table (id, user_id FK, endpoint UNIQUE, keys JSONB, device_info JSONB) in `phase-2/backend/alembic/versions/013_create_push_subscriptions_table.py`
- [x] T079 [US4] Create Alembic migration 014 — add due_date TIMESTAMPTZ column to tasks table + index on (user_id, due_date) in `phase-2/backend/alembic/versions/014_add_due_date_to_tasks.py`
- [x] T080 [P] [US4] Create ReminderMetadata SQLModel in `phase-3/backend/src/models/reminder.py`
- [x] T081 [P] [US4] Create PushSubscription SQLModel in `phase-3/backend/src/models/push_subscription.py`
- [x] T082 [US4] Implement set_due_date MCP tool with user_id isolation, creates/updates ReminderMetadata in `phase-3/backend/src/mcp/tools/reminder_tools.py`
- [x] T083 [US4] Register set_due_date tool in FastMCP server in `phase-3/backend/src/mcp/server.py`
- [x] T084 [US4] Implement reminder checker service — query due reminders, send push via pywebpush, mark notification_sent, handle 410 Gone in `phase-3/backend/src/services/reminder_service.py`
- [x] T085 [US4] Implement APScheduler check_reminders job (1-min interval) calling reminder_service in `phase-3/backend/src/scheduler/jobs.py`
- [x] T086 [US4] Implement POST /api/{user_id}/push/subscribe and DELETE /api/{user_id}/push/subscribe/{id} routes in `phase-3/backend/src/api/routes/push.py`
- [x] T087 [US4] Register push router in FastAPI app in `phase-3/backend/src/main.py`
- [x] T088 [US4] Create Service Worker for receiving push notifications in `phase-3/frontend/public/sw.js`
- [x] T089 [US4] Create push notification subscription logic (permission prompt, SW registration, subscription POST) in `phase-3/frontend/lib/push.ts`
- [x] T090 [US4] Create NotificationBanner component for in-app fallback when push permission denied in `phase-3/frontend/components/chat/NotificationBanner.tsx`
- [x] T091 [US4] Integrate push permission prompt on first chat page visit in `phase-3/frontend/app/chat/page.tsx`
- [x] T092 [US4] Update agent system prompt with date parsing examples (tomorrow, next Friday, in 2 hours, March 15) and confirmation rule in `phase-3/backend/src/agent/prompts.py`

**Checkpoint**: User Story 4 complete — due dates set via NL, push notifications delivered, overdue indication, in-app fallback.

---

## Phase 7: User Story 5 — Advanced Natural Language Understanding (Priority: P5)

**Goal**: Batch task creation, compound filters, contextual references from conversation history, analytical queries about task completion patterns.

**Independent Test**: User says "add tasks: buy milk, clean kitchen, and do laundry", AI creates 3 tasks. User says "what did I accomplish this week?", AI summarizes completed tasks.

### Tests for User Story 5 (REQUIRED - TDD NON-NEGOTIABLE)

- [x] T093 [P] [US5] Write integration test for batch task creation ("add tasks X, Y, and Z" creates 3 tasks) in `phase-3/backend/tests/integration/test_chat_api.py`
- [x] T094 [P] [US5] Write integration test for compound filter ("high priority pending tasks") in `phase-3/backend/tests/integration/test_chat_api.py`
- [x] T095 [P] [US5] Write integration test for off-topic message redirect in `phase-3/backend/tests/integration/test_chat_api.py`

### Implementation for User Story 5

- [x] T096 [US5] Update agent system prompt with batch creation patterns, compound filter examples, contextual reference resolution, analytical query examples in `phase-3/backend/src/agent/prompts.py`
- [x] T097 [US5] Update agent system prompt with off-topic redirect behavior ("I'm your task assistant...") in `phase-3/backend/src/agent/prompts.py`
- [x] T098 [US5] Enhance list_tasks MCP tool with due_date_from/due_date_to parameters for date range queries in `phase-3/backend/src/mcp/tools/task_tools.py`

**Checkpoint**: User Story 5 complete — batch operations, compound filters, contextual references, off-topic handling all functional.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T099 [P] Add structured JSON logging across all backend components (chat, MCP, scheduler) in `phase-3/backend/src/logging_config.py`
- [x] T100 [P] Add token usage tracking per chat request (FR-049) in `phase-3/backend/src/services/chat_service.py`
- [x] T101 [P] Write E2E test for full chat conversation flow (create task, list, complete, delete via NL) in `phase-3/frontend/__tests__/e2e/chat-flow.spec.ts`
- [x] T102 [P] Write E2E test for conversation CRUD (create, switch, delete, history persistence) in `phase-3/frontend/__tests__/e2e/conversation-crud.spec.ts`
- [x] T103 [P] Write E2E test for push notification flow (permission, subscription, delivery) in `phase-3/frontend/__tests__/e2e/notifications.spec.ts`
- [x] T104 Add APScheduler catch-up logic for missed jobs on server restart in `phase-3/backend/src/main.py`
- [x] T105 Add health check endpoint for Phase III backend in `phase-3/backend/src/main.py`
- [x] T106 [P] Run ruff, black, mypy validation on all backend code
- [x] T107 [P] Run frontend lint and type-check validation
- [x] T108 Validate quickstart.md — verify all setup steps work end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational — BLOCKS US2 (US2 needs chat/conversation infra from US1)
- **User Story 2 (Phase 4)**: Depends on US1 (conversation management built in US1)
- **User Story 3 (Phase 5)**: Depends on Foundational — can run parallel with US1/US2 (independent recurrence domain)
- **User Story 4 (Phase 6)**: Depends on Foundational — can run parallel with US1/US2/US3 (independent reminder domain), but scheduler integration benefits from US3
- **User Story 5 (Phase 7)**: Depends on US1 (advanced NL builds on basic CRUD agent)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

```
Setup (Phase 1)
    ↓
Foundational (Phase 2)
    ↓
    ├── US1: NL Task CRUD (Phase 3) ──→ US2: Conversation Persistence (Phase 4)
    │                                          ↓
    │                                   US5: Advanced NL (Phase 7)
    ├── US3: Recurring Tasks (Phase 5) ─┐
    │                                    ├──→ Polish (Phase 8)
    └── US4: Due Dates & Reminders (Phase 6) ─┘
```

### Within Each User Story

1. Tests MUST be written and FAIL before implementation (TDD)
2. Models/migrations before services
3. Services before API routes/MCP tools
4. Backend before frontend (API must exist for frontend to consume)
5. Story complete before moving to next priority

### Parallel Opportunities

**Phase 1** (all [P] tasks): T002 || T003 || T004 || T005 || T006 || T007 || T008

**Phase 2** (after T012): T013 || T014 || T015 || T018 || T019

**Phase 3 tests**: T022 || T023 || T024 || T025 || T026 || T027 || T028 || T029

**Phase 3 impl**: T030 || T031 (then T032 after both); T040 || T041 (frontend parallel)

**Phase 5 + Phase 6 can run in parallel** (independent domains after foundational)

---

## Parallel Example: User Story 1

```bash
# Launch all US1 tests in parallel:
T022: "Unit tests for create_task MCP tool"
T023: "Unit tests for list_tasks MCP tool"
T024: "Unit tests for update_task/complete_task/delete_task"
T025: "Integration test for POST /api/{user_id}/chat"
T028: "Frontend unit test for ChatContainer"
T029: "Frontend unit test for ToolCallDisplay"

# Launch US1 model-level tasks in parallel:
T030: "Implement create_task MCP tool"
T031: "Implement list_tasks MCP tool"

# Launch US1 frontend tasks in parallel:
T040: "Create ChatContainer component"
T041: "Create ToolCallDisplay component"
```

---

## Parallel Example: User Story 3 + User Story 4 (cross-story parallelism)

```bash
# After Foundational phase, US3 and US4 can start simultaneously:

# Developer A: User Story 3
T059-T062: Recurrence tests
T063-T070: Recurrence implementation

# Developer B: User Story 4
T071-T076: Reminder tests
T077-T092: Reminder implementation
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test US1 independently — full CRUD via chat
5. Deploy/demo if ready — MVP deliverable

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (**MVP!**)
3. Add User Story 2 → Test independently → Deploy/Demo (persistence)
4. Add User Story 3 → Test independently → Deploy/Demo (recurrence)
5. Add User Story 4 → Test independently → Deploy/Demo (reminders)
6. Add User Story 5 → Test independently → Deploy/Demo (advanced NL)
7. Polish → Final validation → Release

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 → User Story 2 → User Story 5
   - Developer B: User Story 3 → User Story 4
3. Stories complete and integrate independently
4. Polish phase as a team

---

## Summary

| Metric | Count |
|--------|-------|
| **Total tasks** | 108 |
| **Setup (Phase 1)** | 8 tasks (T001–T008) |
| **Foundational (Phase 2)** | 13 tasks (T009–T021) |
| **US1: NL Task CRUD (Phase 3)** | 24 tasks (T022–T045) |
| **US2: Conversation Persistence (Phase 4)** | 13 tasks (T046–T058) |
| **US3: Recurring Tasks (Phase 5)** | 12 tasks (T059–T070) |
| **US4: Due Dates & Reminders (Phase 6)** | 22 tasks (T071–T092) |
| **US5: Advanced NL (Phase 7)** | 6 tasks (T093–T098) |
| **Polish (Phase 8)** | 10 tasks (T099–T108) |
| **Parallel opportunities** | 60+ tasks marked [P] |
| **MVP scope** | Phase 1 + 2 + 3 = 45 tasks |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Verify tests fail before implementing (TDD Red-Green-Refactor)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Alembic migrations live in phase-2/backend/alembic/ (shared database, single migration history)
- MCP server runs as separate process (port 8001) from FastAPI backend (port 8002)
