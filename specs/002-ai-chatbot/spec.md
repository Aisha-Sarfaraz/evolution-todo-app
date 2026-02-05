# Feature Specification: AI-Powered Conversational Todo Management

**Feature Branch**: `002-ai-chatbot`
**Created**: 2026-01-31
**Status**: Draft
**Input**: User description: "Phase III: Todo AI Chatbot - AI-powered conversational Todo system with stateless MCP architecture, OpenAI Agents SDK, OpenRouter API, and advanced features including recurring tasks and due date reminders"

---

## Clarifications

### Session 2026-01-31

- Q: Should the AI chatbot be the only interface or coexist with Phase II traditional dashboard? → A: Chat-only. The chatbot replaces the traditional task UI as the sole interface for Phase III.
- Q: Should task deletion via chat use soft delete or hard delete? → A: Hard delete. Tasks are permanently removed from the database. The AI confirmation step serves as the safety net.
- Q: What rate limit should apply to the chat endpoint? → A: 10 messages per user per minute.
- Q: What should happen when the LLM provider is unavailable? → A: Return a friendly error message ("I'm temporarily unable to respond. Please try again in a moment."). No retry, no fallback.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Task CRUD (Priority: P1)

Authenticated users must be able to create, list, update, complete, and delete tasks through natural language conversation. The chatbot is the sole interface for task management in Phase III, replacing the traditional form-based UI from Phase II. The AI assistant interprets user intent, executes the appropriate action via tool invocation, and confirms the result in conversational language.

**Why this priority**: Core MVP - demonstrates AI chatbot value over traditional CRUD. All advanced features depend on this foundation. A user can accomplish the full task management lifecycle through conversation alone.

**Independent Test**: User opens chat, types "add a task to buy groceries", AI creates task and confirms. User types "show my tasks", AI lists tasks. User types "mark groceries as done", AI completes task. User types "delete the groceries task", AI deletes it. Full CRUD cycle via natural language.

**Acceptance Scenarios**:

1. **Given** authenticated user with no tasks, **When** user sends "add a task to buy groceries", **Then** system creates task with title "buy groceries" under user's account, AI responds with confirmation including task title and status
2. **Given** authenticated user with no tasks, **When** user sends "add a task to buy groceries with description milk, eggs, and bread", **Then** system creates task with title "buy groceries" and description "milk, eggs, and bread", AI confirms creation
3. **Given** user has 5 tasks (3 pending, 2 completed), **When** user sends "show me all my tasks", **Then** AI returns formatted list of all 5 tasks with titles, statuses, and creation dates
4. **Given** user has 5 tasks (3 pending, 2 completed), **When** user sends "what's pending?", **Then** AI returns list of 3 pending tasks only
5. **Given** user has 5 tasks (3 pending, 2 completed), **When** user sends "what have I completed?", **Then** AI returns list of 2 completed tasks only
6. **Given** user has task "Team meeting" with pending status, **When** user sends "mark my team meeting task as complete", **Then** system marks task as complete with completion timestamp, AI confirms "I've marked 'Team meeting' as complete"
7. **Given** user has task "Buy groceries", **When** user sends "change the groceries task title to Buy groceries and fruits", **Then** system updates task title, AI confirms "I've updated the title to 'Buy groceries and fruits'"
8. **Given** user has task "Old task", **When** user sends "delete the old task", **Then** AI asks for confirmation "Are you sure you want to delete 'Old task'?", user confirms, system deletes task, AI confirms deletion
9. **Given** user sends "update the task" with 5 tasks in their list, **When** AI cannot determine which task, **Then** AI asks "Which task would you like to update?" and lists available tasks for selection
10. **Given** user sends ambiguous message like "do the thing", **When** AI cannot determine intent, **Then** AI responds with helpful guidance: "I can help you manage tasks. Try saying 'add a task', 'show my tasks', or 'mark a task as done'"
11. **Given** user sends "I need to remember to pay bills", **When** AI interprets intent, **Then** system creates task with title "pay bills", AI confirms creation
12. **Given** user without valid authentication token sends a message, **When** system processes request, **Then** system returns authentication error, user is redirected to sign in

---

### User Story 2 - Conversation Persistence & Context (Priority: P2)

Users must be able to have multi-turn conversations that persist across browser sessions. The system maintains conversation history in the database so users can resume where they left off. The AI uses recent conversation context (last 7 messages) to provide coherent multi-turn interactions.

**Why this priority**: Essential for production usability. Without persistence, users lose all conversation context on page reload. Depends on P1 basic CRUD working first.

**Independent Test**: User starts conversation, creates 3 tasks over multiple messages, closes browser, reopens after 1 hour, conversation history is visible, user continues with "show the tasks I added earlier", AI responds correctly with context.

**Acceptance Scenarios**:

1. **Given** user opens chat for the first time, **When** user sends first message, **Then** system creates a new conversation record and stores the message, assigns conversation identifier
2. **Given** user has existing conversation with 10 messages, **When** user returns to chat after closing browser, **Then** system loads conversation history and displays previous messages in chronological order
3. **Given** conversation has 20 messages, **When** user sends new message, **Then** AI receives last 7 messages as context for generating response, older messages are available for display but not sent to AI
4. **Given** conversation has 50+ messages, **When** user scrolls up in chat UI, **Then** system lazy-loads older messages in batches (oldest messages loaded on demand)
5. **Given** user sends "like I mentioned about the groceries" referencing a message within the 7-message context window, **When** AI processes message, **Then** AI correctly references the earlier groceries discussion
6. **Given** user has 3 separate conversations, **When** user views conversation list, **Then** system displays all conversations sorted by most recently active, with preview of last message
7. **Given** user selects a previous conversation from the list, **When** conversation loads, **Then** system displays full message history for that conversation and subsequent messages continue in that conversation
8. **Given** user wants a fresh conversation, **When** user starts a new chat, **Then** system creates a new conversation record with no prior context

---

### User Story 3 - Recurring Tasks (Priority: P3)

Users must be able to create recurring tasks using natural language patterns (daily, weekly, monthly, custom intervals). The system automatically creates new task instances based on the recurrence schedule. Users can modify or cancel recurrence rules.

**Why this priority**: Key advanced productivity feature. Requires recurrence rule storage and scheduling infrastructure. Builds on P1 task creation and P2 conversation context.

**Independent Test**: User types "remind me to take vitamins every day", AI creates recurring task, system creates next daily instance automatically. User types "stop the vitamins reminder", AI removes recurrence rule.

**Acceptance Scenarios**:

1. **Given** user sends "add a task to take vitamins every day", **When** AI parses daily recurrence, **Then** system creates task with daily recurrence rule (frequency=daily, interval=1), AI confirms "I've added 'take vitamins' as a daily recurring task"
2. **Given** user sends "remind me to pay rent on the 1st of every month", **When** AI parses monthly recurrence, **Then** system creates task with monthly recurrence (day_of_month=1), AI confirms with next occurrence date
3. **Given** user sends "team standup every Monday, Wednesday, and Friday", **When** AI parses multi-day weekly recurrence, **Then** system creates weekly recurrence with specified days, AI confirms schedule
4. **Given** user sends "submit report every other week", **When** AI parses bi-weekly recurrence, **Then** system creates weekly recurrence with interval=2, AI confirms "every 2 weeks"
5. **Given** recurring task reaches its next occurrence time, **When** background scheduler runs, **Then** system creates a new task instance, updates recurrence rule with next occurrence date
6. **Given** user sends "stop the daily vitamins reminder", **When** AI identifies the recurring task, **Then** system removes recurrence rule, existing task instances remain, AI confirms "I've stopped the recurring reminders for 'take vitamins'"
7. **Given** user sends "change my weekly standup to Tuesdays and Thursdays", **When** AI identifies existing recurrence, **Then** system updates recurrence days, AI confirms updated schedule
8. **Given** user sends "show me my recurring tasks", **When** AI queries tasks with recurrence rules, **Then** AI returns list with recurrence frequency indicators (e.g., "take vitamins - daily", "pay rent - monthly on the 1st")
9. **Given** monthly recurrence set for 31st of month, **When** February arrives (28/29 days), **Then** system handles gracefully by scheduling for last day of month or skipping
10. **Given** user sends "remind me to water plants every 3 days until March 15", **When** AI parses recurrence with end date, **Then** system creates recurrence with interval=3 and end_date, AI confirms schedule and end date

---

### User Story 4 - Due Dates & Time Reminders (Priority: P4)

Users must be able to set due dates and reminder times on tasks using natural language. The system parses relative and absolute date/time expressions. Users receive browser notifications when reminders trigger. Overdue tasks are visually indicated.

**Why this priority**: Time-sensitive task management is critical for productivity. Builds on P3 date parsing patterns. Requires browser notification infrastructure.

**Independent Test**: User says "remind me tomorrow at 2pm to call the dentist", AI creates task with due date and reminder time. Next day at 2pm, browser notification appears. User sees overdue indicator if task not completed by deadline.

**Acceptance Scenarios**:

1. **Given** user sends "add task submit proposal by Friday 5pm", **When** AI parses due date, **Then** system creates task with due_date set to next Friday 17:00, AI confirms "I've added 'submit proposal' due Friday at 5:00 PM"
2. **Given** user sends "remind me in 2 hours to check email", **When** AI parses relative time, **Then** system creates task with due_date = current time + 2 hours, AI confirms with absolute time
3. **Given** user sends "remind me tomorrow at 9am to call the doctor", **When** AI parses relative+absolute time, **Then** system creates task with due_date = tomorrow 09:00, reminder_time set accordingly
4. **Given** AI interprets date from user message, **When** date interpretation could be ambiguous (e.g., "next Friday" when today is Friday), **Then** AI confirms interpreted date with user: "I'll set that for Friday, February 6th. Is that correct?"
5. **Given** task has reminder_time reaching current time, **When** reminder checker runs, **Then** system sends browser notification with task title and brief description
6. **Given** user has granted browser notification permission, **When** notification is sent, **Then** notification appears even if app tab is not focused, clicking notification opens the app to the relevant conversation
7. **Given** user has denied browser notification permission, **When** reminder triggers, **Then** system stores notification as pending, displays in-app notification banner when user next opens chat
8. **Given** task due_date has passed and task status is still pending, **When** user views tasks, **Then** overdue tasks display with visual overdue indicator and "Overdue by X days" label
9. **Given** user sends "show me tasks due this week", **When** AI processes date range query, **Then** AI returns tasks with due dates between today and end of current week, sorted by due date
10. **Given** multiple reminders trigger within the same minute, **When** system processes notifications, **Then** notifications are batched to avoid overwhelming the user (maximum 3 individual notifications, remainder collapsed into summary)

---

### User Story 5 - Advanced Natural Language Understanding (Priority: P5)

The AI must understand complex operations including batch task creation, compound filters, contextual references from conversation history, and analytical queries about task completion patterns.

**Why this priority**: Enhances user experience beyond basic commands. Requires sophisticated prompt engineering and conversation context management. Builds on all previous stories.

**Independent Test**: User says "add tasks: buy milk, clean kitchen, and do laundry", AI creates 3 separate tasks. User says "mark all my shopping tasks as done", AI identifies and completes relevant tasks. User says "what did I accomplish this week?", AI summarizes.

**Acceptance Scenarios**:

1. **Given** user sends "add tasks to buy milk, eggs, and bread", **When** AI parses batch creation, **Then** system creates 3 separate tasks, AI confirms "I've added 3 tasks: buy milk, buy eggs, buy bread"
2. **Given** user sends "show me high priority pending tasks", **When** AI parses compound filter, **Then** AI queries tasks with priority=High AND status=pending, returns filtered list
3. **Given** user says "what did I accomplish this week?", **When** AI processes analytical query, **Then** AI retrieves tasks completed in last 7 days, summarizes with count and titles
4. **Given** user says "the task I created yesterday", **When** AI processes temporal reference, **Then** AI queries tasks created within yesterday's date range, uses result in response
5. **Given** user says "mark all of those as done" after AI listed 3 pending tasks, **When** AI uses conversation context, **Then** AI completes all 3 tasks from the previous listing, confirms batch completion
6. **Given** user sends a message completely unrelated to task management (e.g., "what's the weather?"), **When** AI processes off-topic message, **Then** AI politely redirects: "I'm your task assistant - I can help you add, view, update, or complete tasks. What would you like to do?"

---

### Edge Cases

- **Empty message**: User sends empty or whitespace-only message; system rejects with "Please type a message"
- **Very long message**: User sends message exceeding 5000 characters; system truncates or rejects with length error
- **Rapid-fire messages**: User sends multiple messages before first response returns; system queues and processes sequentially
- **Concurrent sessions**: User has chat open on two devices; both sessions see the same conversation after refresh
- **Task title from NL**: AI extracts very long task title from natural language; title truncation rules from Phase II apply (max 200 chars)
- **SQL injection via NL**: User sends "add task '; DROP TABLE tasks;--"; system treats entire string as literal task title, no injection possible
- **Token expiration mid-conversation**: JWT expires while user is chatting; frontend refreshes token transparently, retries failed request
- **AI tool failure**: Tool invocation fails (e.g., database timeout); AI returns friendly error "I had trouble completing that action. Please try again."
- **Recurrence on invalid dates**: Monthly recurrence set for Feb 31st; system skips invalid dates or uses last valid day of month
- **Notification permission revoked after granting**: System falls back to in-app notifications
- **Timezone handling**: Dates stored in UTC; frontend converts to user's local timezone for display
- **Context window boundary**: User references message outside the 7-message context window; AI gracefully indicates it doesn't have that context and suggests rephrasing
- **Rate limit exceeded**: User sends 11th message within a minute; system returns "You're sending messages too quickly. Please wait a moment and try again." with retry-after indicator
- **LLM provider outage**: OpenRouter API returns 500/503; system returns friendly error without exposing technical details, no automatic retry

---

## Requirements *(mandatory)*

### Functional Requirements

**Conversation Management**

- **FR-001**: System MUST provide a single chat endpoint accepting a user message and optional conversation identifier, returning the AI-generated response with any tool invocations performed
- **FR-002**: System MUST create a new conversation record when no conversation identifier is provided, and resume an existing conversation when a valid identifier is supplied
- **FR-003**: System MUST store every user message and AI response as separate records in the database, associated with the conversation and the authenticated user
- **FR-004**: System MUST load the last 7 messages from the conversation to provide as context for AI response generation
- **FR-005**: System MUST enforce user isolation: a user can only access their own conversations and messages; cross-user access returns an authorization error
- **FR-006**: System MUST validate user authentication on every chat request, rejecting unauthenticated requests with a clear error
- **FR-007**: System MUST remain stateless between requests: all conversation state persists in the database, no in-memory session state on the server
- **FR-008**: System MUST include tool invocation details (tool name, result summary) in the response so the frontend can display action confirmations
- **FR-009**: System MUST support conversation deletion, removing the conversation and all associated messages
- **FR-010**: System MUST support listing all conversations for a user, sorted by most recent activity, with a preview of the last message
- **FR-010a**: System MUST enforce a rate limit of 10 messages per user per minute on the chat endpoint, returning a clear "rate limit exceeded" error with retry-after guidance when exceeded
- **FR-010b**: System MUST return a friendly error message ("I'm temporarily unable to respond. Please try again in a moment.") when the LLM provider is unavailable or returns an error, without retrying or falling back to alternative processing

**Task Management Tools**

- **FR-011**: System MUST expose a tool for creating tasks, accepting title (required), description (optional), priority (optional), and category (optional), returning the created task identifier and confirmation
- **FR-012**: System MUST expose a tool for listing tasks, accepting optional filters for status (all, pending, completed), priority, and category, returning an array of matching tasks
- **FR-013**: System MUST expose a tool for updating tasks, accepting task identifier (required) and optional new values for title, description, and priority, returning confirmation of updated fields
- **FR-014**: System MUST expose a tool for completing tasks, accepting task identifier (required), setting status to complete with completion timestamp, returning confirmation
- **FR-015**: System MUST expose a tool for deleting tasks, accepting task identifier (required), permanently removing the task from the database (hard delete), returning confirmation
- **FR-016**: All task management tools MUST enforce user isolation by filtering operations to the authenticated user's tasks only
- **FR-017**: All task management tools MUST validate inputs (e.g., non-empty title, valid task identifier) and return structured error messages for invalid inputs
- **FR-018**: All task management tools MUST be stateless: they receive all required context as parameters, perform the operation against the database, and return results
- **FR-019**: System MUST log all tool invocations with user identifier, tool name, input parameters, success/failure status, and execution duration for auditing
- **FR-020**: System MUST enforce a timeout on individual tool invocations (maximum 10 seconds), returning a timeout error if exceeded

**Recurring Tasks**

- **FR-021**: System MUST expose a tool for creating a recurrence rule on a task, accepting frequency (daily, weekly, monthly, yearly), interval (default 1), optional days of week, optional day of month, and optional end date
- **FR-022**: System MUST store recurrence rules with calculated next occurrence date, linked to the parent task
- **FR-023**: System MUST expose a tool for updating an existing recurrence rule, allowing modification of frequency, interval, days, or end date, recalculating next occurrence
- **FR-024**: System MUST expose a tool for removing a recurrence rule from a task, preserving the existing task instance
- **FR-025**: System MUST implement a background scheduler that checks for recurrence rules where next occurrence has passed, creates new task instances, and updates the next occurrence date
- **FR-026**: System MUST correctly calculate next occurrence for all frequency types: daily (add interval days), weekly (next matching day of week), monthly (next matching day of month), yearly (same date next year)
- **FR-027**: System MUST handle month-end edge cases: if recurrence is set for day 31 and the month has fewer days, schedule for the last day of the month
- **FR-028**: System MUST stop creating instances when a recurrence rule's end date has passed
- **FR-029**: System MUST include recurrence metadata in task listings so users can distinguish recurring from one-time tasks
- **FR-030**: System MUST support canceling a single recurrence instance without affecting the recurrence rule itself

**Due Dates & Reminders**

- **FR-031**: System MUST allow tasks to have an optional due date (date and time) set via the task creation or update tools
- **FR-032**: System MUST store reminder metadata (due date, reminder time, notification sent status) linked to the task
- **FR-033**: System MUST implement a background reminder checker that identifies tasks where reminder time has arrived and notification has not yet been sent
- **FR-034**: System MUST send browser push notifications when reminders trigger, including the task title and a brief description
- **FR-035**: System MUST mark notifications as sent after delivery to prevent duplicate notifications
- **FR-036**: System MUST support user subscription to push notifications, storing subscription details per user per device
- **FR-037**: System MUST fall back to in-app notification display when browser push permission is not granted
- **FR-038**: System MUST calculate and display overdue status for tasks where due date has passed and status is still pending
- **FR-039**: System MUST support querying tasks by due date range (e.g., "due this week", "due today", "overdue")
- **FR-040**: System MUST handle natural language date/time expressions including: "tomorrow", "next Friday", "in 2 hours", "March 15", "end of month", and confirm the interpreted date with the user before committing

**Natural Language Processing**

- **FR-041**: System MUST use an AI agent with a defined system prompt that instructs it to act as a helpful task management assistant
- **FR-042**: System MUST provide tool descriptions and usage examples to the AI agent so it can select the appropriate tool for each user request
- **FR-043**: System MUST support batch task creation when user mentions multiple tasks in one message (e.g., "add tasks X, Y, and Z")
- **FR-044**: System MUST disambiguate task references when multiple tasks could match (e.g., "the meeting task" with multiple meeting-related tasks), asking the user to clarify
- **FR-045**: System MUST extract filter criteria from natural language (e.g., "high priority tasks" maps to priority filter, "tasks due this week" maps to date range filter)
- **FR-046**: System MUST ask for confirmation before executing destructive operations (delete task, remove recurrence) and wait for user's affirmative response
- **FR-047**: System MUST provide helpful fallback responses for messages it cannot interpret, suggesting available actions
- **FR-048**: System MUST use a configurable LLM model via environment variable, enabling model switching without code changes
- **FR-049**: System MUST track token usage per request for cost monitoring and logging
- **FR-050**: System MUST NOT mutate any data without invoking a defined tool; the AI response text alone must never cause database changes

**Frontend Chat Interface**

- **FR-051**: System MUST provide a chat UI displaying messages in chronological order with visual distinction between user and AI messages
- **FR-052**: System MUST provide a message input field where Enter sends the message and Shift+Enter inserts a line break
- **FR-053**: System MUST display a typing/thinking indicator while waiting for AI response
- **FR-054**: System MUST auto-scroll to the latest message when a new message arrives, unless the user has scrolled up to view history
- **FR-055**: System MUST load and display conversation history on page load for returning users
- **FR-056**: System MUST implement lazy loading of older messages when user scrolls to the top of the conversation
- **FR-057**: System MUST display action confirmations visually (e.g., "Task created", "Task completed") distinct from regular chat messages
- **FR-058**: System MUST prompt user for browser notification permission on first visit and store the permission state
- **FR-059**: System MUST register a service worker for receiving push notifications when the app is not in focus
- **FR-060**: System MUST provide a conversation list sidebar showing all conversations with last message preview and timestamp

### Key Entities

- **Conversation**: Represents a chat session. Contains user ownership, optional title (auto-generated from first message), creation and last-activity timestamps. One user can have many conversations. Deleting a conversation cascades to all its messages.

- **Message**: Represents a single chat message within a conversation. Contains the conversation it belongs to, the user who owns it, the role (user or assistant), the message text content, and optional structured data about tool invocations made by the AI. Messages are ordered by creation timestamp. Content has no length limit for AI responses. User isolation enforced (message user_id must match conversation user_id).

- **RecurrenceRule**: Represents a repeating schedule attached to a task. Contains frequency type (daily, weekly, monthly, yearly), interval (every N occurrences), optional specific days of week (for weekly), optional day of month (for monthly), optional end date, and the calculated next occurrence timestamp. One-to-one relationship with task. Deleting the parent task cascades to the recurrence rule. Interval must be at least 1.

- **ReminderMetadata**: Represents due date and notification tracking for a task. Contains optional due date (deadline), optional reminder time (when to notify), notification sent flag (prevents duplicates), and optional snooze time. One-to-one relationship with task. At least one of due date or reminder time must be set. Deleting the parent task cascades to the reminder.

- **PushSubscription**: Represents a browser push notification subscription. Contains the user who owns it, the push endpoint URL, encryption keys, and optional device metadata. One user can have multiple subscriptions (one per device/browser). Endpoint must be unique. Used by the notification system to deliver reminders.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 90% of basic task CRUD operations (add, list, update, complete, delete) are successfully completed via natural language on the first attempt, measured across a test suite of 50 representative user commands
- **SC-002**: Users receive AI responses within 3 seconds of sending a message for 95% of requests, measured via frontend response time monitoring
- **SC-003**: 100% of task operations are isolated to the authenticated user, with zero cross-user data access, verified via integration tests simulating concurrent multi-user sessions
- **SC-004**: Conversation history loads within 1 second for conversations up to 500 messages, measured at the frontend display level
- **SC-005**: 95% of natural language date/time references (e.g., "tomorrow", "next Friday", "in 2 hours") are correctly interpreted, validated against a test suite of 100 date phrases
- **SC-006**: Recurring task instances are automatically created within 1 hour of their scheduled next occurrence time, 99% of the time, measured via scheduler monitoring
- **SC-007**: Browser notifications are delivered within 2 minutes of the scheduled reminder time for users with granted notification permissions
- **SC-008**: Zero unhandled errors in the chat conversation flow over a 7-day testing period, measured via error monitoring
- **SC-009**: Users can create a recurring task using natural language in a single message exchange (one user message, one AI confirmation), for 85% of common recurrence patterns
- **SC-010**: The chat interface achieves a usability score where 80% of first-time users can complete basic task operations without external instruction
- **SC-011**: 80% of ambiguous user intents are successfully clarified by the AI within 1 follow-up message, measured via conversation flow analysis
- **SC-012**: The system handles 20 concurrent chat users performing mixed operations without observable performance degradation
- **SC-013**: Average cost per 10-message conversation exchange remains within acceptable bounds for the configured LLM model, tracked via usage logs
- **SC-014**: All destructive operations (delete, remove recurrence) require explicit user confirmation, with 100% enforcement verified via integration tests
- **SC-015**: The system correctly resumes conversations after server restart with no data loss, verified by restart testing

---

## Assumptions & Constraints

### Technology Constraints (Fixed for Hackathon)

- AI agent framework: OpenAI Agents SDK
- LLM gateway: OpenRouter API with configurable model
- Tool protocol: Model Context Protocol (MCP) with Official MCP SDK
- Frontend chat component: OpenAI ChatKit
- Backend: Python FastAPI (extending Phase II backend)
- Database: Neon PostgreSQL (extending Phase II schema)
- Authentication: Better Auth JWT (reusing Phase II auth infrastructure)

### Assumptions

- Phase II backend and frontend are operational and deployed
- Better Auth JWT tokens from Phase II are reusable for Phase III endpoints
- The existing Task model from Phase II is extended (not replaced) with new fields for due dates and recurrence
- OpenRouter API provides access to the configured LLM model with tool-calling support
- Browser Push API (Web Push) is supported by target browsers (Chrome, Firefox, Edge)
- Background scheduler (for recurrence and reminders) runs as a separate process or cron job alongside the main server
- Domain allowlist is configured in OpenAI platform for ChatKit deployment
- User timezone is detected from browser and sent with requests; dates stored in UTC

### Non-Goals

- This specification does NOT cover Phase I or Phase II features (read-only forward extension)
- No traditional form-based task management UI (Phase II dashboard is replaced by the chatbot interface)
- No real-time collaborative editing of tasks between users
- No voice input/output for the chatbot
- No mobile native app (web-only)
- No AI-powered task prioritization or suggestion (AI executes user commands, does not proactively suggest)
- No file attachments in chat messages
- No integration with external calendars (Google Calendar, Outlook, etc.)

---

## Dependencies

- **Phase II Task Model**: Phase III extends the existing Task entity with due_date and recurrence fields
- **Phase II Authentication**: Phase III reuses Better Auth JWT validation for chat endpoints
- **Phase II Database**: Phase III adds new tables (Conversation, Message, RecurrenceRule, ReminderMetadata, PushSubscription) to the existing Neon PostgreSQL database
- **Phase II User Model**: Phase III uses existing user_id for conversation and message ownership
