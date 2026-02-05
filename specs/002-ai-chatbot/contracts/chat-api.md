# API Contracts — AI-Powered Conversational Todo Management

**Feature Branch**: `002-ai-chatbot`
**Created**: 2026-01-31
**Spec**: [../spec.md](../spec.md)

---

## Base URL

```
/api/{user_id}
```

All endpoints require Bearer JWT authentication. The `user_id` path parameter must match the authenticated user's ID (enforced by `ValidatedUser` dependency from Phase II).

---

## Endpoints

### 1. POST /api/{user_id}/chat

**Purpose**: Send a message and receive AI response (FR-001, FR-002, FR-003, FR-004)

**Authentication**: Bearer JWT (reuse Phase II `ValidatedUser` dependency)

**Rate Limit**: 10 messages per user per minute (FR-010a)

**Request Body**:

```json
{
  "conversation_id": "uuid | null",
  "message": "string (required, 1-5000 chars)",
  "timezone": "string | null (e.g., 'America/New_York')"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `conversation_id` | UUID | No | Existing conversation to continue. If null, creates new conversation. |
| `message` | string | Yes | User's chat message. Min 1 char, max 5000 chars. |
| `timezone` | string | No | User's IANA timezone for date parsing. Defaults to UTC. |

**Response (200 OK)**:

```json
{
  "conversation_id": "uuid",
  "response": "string (AI-generated response text)",
  "tool_calls": [
    {
      "tool": "create_task",
      "input": {"title": "buy groceries", "priority": "medium"},
      "output": {"task_id": "uuid", "status": "pending"},
      "duration_ms": 150
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `conversation_id` | UUID | Conversation ID (new or existing) |
| `response` | string | AI assistant's response text |
| `tool_calls` | array | List of tool invocations performed (may be empty) |

**Error Responses**:

| Status | Code | Description |
|--------|------|-------------|
| 400 | `INVALID_MESSAGE` | Empty message or exceeds 5000 chars |
| 401 | `UNAUTHENTICATED` | Missing or invalid JWT token |
| 403 | `FORBIDDEN` | user_id mismatch with JWT |
| 404 | `CONVERSATION_NOT_FOUND` | Invalid conversation_id |
| 429 | `RATE_LIMIT_EXCEEDED` | Over 10 msg/min. Headers: `Retry-After: <seconds>` |
| 503 | `LLM_UNAVAILABLE` | LLM provider error. Body: `{"detail": "I'm temporarily unable to respond. Please try again in a moment."}` |

---

### 2. GET /api/{user_id}/conversations

**Purpose**: List all conversations for user (FR-010)

**Authentication**: Bearer JWT

**Query Parameters**: None

**Response (200 OK)**:

```json
{
  "conversations": [
    {
      "id": "uuid",
      "title": "Task management discussion",
      "last_message_preview": "I've added 'buy groceries' to your...",
      "updated_at": "2026-01-31T15:30:00Z"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `conversations` | array | Conversations sorted by `updated_at` DESC |
| `conversations[].id` | UUID | Conversation identifier |
| `conversations[].title` | string | Auto-generated title (may be null) |
| `conversations[].last_message_preview` | string | Truncated last message (100 chars max) |
| `conversations[].updated_at` | ISO 8601 | Last activity timestamp |

**Error Responses**:

| Status | Code | Description |
|--------|------|-------------|
| 401 | `UNAUTHENTICATED` | Missing or invalid JWT token |
| 403 | `FORBIDDEN` | user_id mismatch |

---

### 3. GET /api/{user_id}/conversations/{conversation_id}/messages

**Purpose**: Load message history for a conversation (FR-055, FR-056)

**Authentication**: Bearer JWT

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Messages per page (max 100) |
| `before` | UUID | null | Cursor: return messages created before this message ID |

**Response (200 OK)**:

```json
{
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "add a task to buy groceries",
      "tool_calls": null,
      "created_at": "2026-01-31T15:30:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "I've added 'buy groceries' to your task list.",
      "tool_calls": [
        {
          "tool": "create_task",
          "input": {"title": "buy groceries"},
          "output": {"task_id": "uuid", "status": "pending"}
        }
      ],
      "created_at": "2026-01-31T15:30:02Z"
    }
  ],
  "has_more": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| `messages` | array | Messages in chronological order |
| `has_more` | boolean | Whether more messages exist before the oldest returned |

**Error Responses**:

| Status | Code | Description |
|--------|------|-------------|
| 401 | `UNAUTHENTICATED` | Missing or invalid JWT |
| 403 | `FORBIDDEN` | user_id mismatch or conversation not owned by user |
| 404 | `CONVERSATION_NOT_FOUND` | Invalid conversation_id |

---

### 4. DELETE /api/{user_id}/conversations/{conversation_id}

**Purpose**: Delete a conversation and all its messages (FR-009)

**Authentication**: Bearer JWT

**Response (200 OK)**:

```json
{
  "deleted": true
}
```

**Error Responses**:

| Status | Code | Description |
|--------|------|-------------|
| 401 | `UNAUTHENTICATED` | Missing or invalid JWT |
| 403 | `FORBIDDEN` | user_id mismatch or conversation not owned by user |
| 404 | `CONVERSATION_NOT_FOUND` | Invalid conversation_id |

---

### 5. POST /api/{user_id}/push/subscribe

**Purpose**: Register browser push notification subscription (FR-036)

**Authentication**: Bearer JWT

**Request Body**:

```json
{
  "endpoint": "https://fcm.googleapis.com/fcm/send/...",
  "keys": {
    "p256dh": "base64-encoded-public-key",
    "auth": "base64-encoded-auth-secret"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `endpoint` | string | Yes | Push service endpoint URL (max 500 chars) |
| `keys.p256dh` | string | Yes | Client public key (base64) |
| `keys.auth` | string | Yes | Auth secret (base64) |

**Response (201 Created)**:

```json
{
  "subscription_id": "uuid"
}
```

**Error Responses**:

| Status | Code | Description |
|--------|------|-------------|
| 400 | `INVALID_SUBSCRIPTION` | Missing endpoint or keys |
| 401 | `UNAUTHENTICATED` | Missing or invalid JWT |
| 403 | `FORBIDDEN` | user_id mismatch |
| 409 | `DUPLICATE_ENDPOINT` | Endpoint already registered |

---

### 6. DELETE /api/{user_id}/push/subscribe/{subscription_id}

**Purpose**: Unsubscribe from push notifications

**Authentication**: Bearer JWT

**Response (200 OK)**:

```json
{
  "deleted": true
}
```

**Error Responses**:

| Status | Code | Description |
|--------|------|-------------|
| 401 | `UNAUTHENTICATED` | Missing or invalid JWT |
| 403 | `FORBIDDEN` | Subscription not owned by user |
| 404 | `SUBSCRIPTION_NOT_FOUND` | Invalid subscription_id |

---

## MCP Tool Contracts

The MCP server exposes the following tools via Streamable HTTP at `http://localhost:8001/mcp`. All tools receive `user_id` as a parameter for user isolation.

### create_task

```json
{
  "name": "create_task",
  "description": "Create a new task for the authenticated user",
  "parameters": {
    "user_id": {"type": "string", "required": true},
    "title": {"type": "string", "required": true, "maxLength": 200},
    "description": {"type": "string", "required": false, "maxLength": 2000},
    "priority": {"type": "string", "required": false, "enum": ["LOW", "MEDIUM", "HIGH", "URGENT"], "default": "MEDIUM"},
    "category_id": {"type": "string", "required": false}
  },
  "returns": {
    "task_id": "string (UUID)",
    "title": "string",
    "status": "string",
    "created_at": "string (ISO 8601)"
  }
}
```

### list_tasks

```json
{
  "name": "list_tasks",
  "description": "List tasks for the authenticated user with optional filters",
  "parameters": {
    "user_id": {"type": "string", "required": true},
    "status": {"type": "string", "required": false, "enum": ["PENDING", "COMPLETE", null]},
    "priority": {"type": "string", "required": false, "enum": ["LOW", "MEDIUM", "HIGH", "URGENT"]},
    "due_date_from": {"type": "string", "required": false, "format": "date"},
    "due_date_to": {"type": "string", "required": false, "format": "date"},
    "search": {"type": "string", "required": false}
  },
  "returns": {
    "tasks": "array of task objects",
    "total_count": "integer"
  }
}
```

### update_task

```json
{
  "name": "update_task",
  "description": "Update a task's title, description, or priority",
  "parameters": {
    "user_id": {"type": "string", "required": true},
    "task_id": {"type": "string", "required": true},
    "title": {"type": "string", "required": false, "maxLength": 200},
    "description": {"type": "string", "required": false, "maxLength": 2000},
    "priority": {"type": "string", "required": false, "enum": ["LOW", "MEDIUM", "HIGH", "URGENT"]}
  },
  "returns": {
    "task_id": "string",
    "updated_fields": "array of string",
    "updated_at": "string (ISO 8601)"
  }
}
```

### complete_task

```json
{
  "name": "complete_task",
  "description": "Mark a task as complete",
  "parameters": {
    "user_id": {"type": "string", "required": true},
    "task_id": {"type": "string", "required": true}
  },
  "returns": {
    "task_id": "string",
    "status": "COMPLETE",
    "completed_at": "string (ISO 8601)"
  }
}
```

### delete_task

```json
{
  "name": "delete_task",
  "description": "Permanently delete a task (hard delete)",
  "parameters": {
    "user_id": {"type": "string", "required": true},
    "task_id": {"type": "string", "required": true}
  },
  "returns": {
    "deleted": "boolean",
    "task_id": "string"
  }
}
```

### create_recurrence

```json
{
  "name": "create_recurrence",
  "description": "Create a recurrence rule for a task",
  "parameters": {
    "user_id": {"type": "string", "required": true},
    "task_id": {"type": "string", "required": true},
    "frequency": {"type": "string", "required": true, "enum": ["daily", "weekly", "monthly", "yearly"]},
    "interval": {"type": "integer", "required": false, "default": 1, "minimum": 1},
    "days_of_week": {"type": "array", "items": {"type": "integer"}, "required": false},
    "day_of_month": {"type": "integer", "required": false, "minimum": 1, "maximum": 31},
    "end_date": {"type": "string", "required": false, "format": "date"}
  },
  "returns": {
    "recurrence_id": "string",
    "next_occurrence": "string (ISO 8601)"
  }
}
```

### update_recurrence

```json
{
  "name": "update_recurrence",
  "description": "Update an existing recurrence rule",
  "parameters": {
    "user_id": {"type": "string", "required": true},
    "task_id": {"type": "string", "required": true},
    "frequency": {"type": "string", "required": false},
    "interval": {"type": "integer", "required": false},
    "days_of_week": {"type": "array", "required": false},
    "day_of_month": {"type": "integer", "required": false},
    "end_date": {"type": "string", "required": false}
  },
  "returns": {
    "recurrence_id": "string",
    "next_occurrence": "string (ISO 8601)"
  }
}
```

### remove_recurrence

```json
{
  "name": "remove_recurrence",
  "description": "Remove recurrence rule from a task (task remains)",
  "parameters": {
    "user_id": {"type": "string", "required": true},
    "task_id": {"type": "string", "required": true}
  },
  "returns": {
    "removed": "boolean"
  }
}
```

### set_due_date

```json
{
  "name": "set_due_date",
  "description": "Set or update due date and optional reminder for a task",
  "parameters": {
    "user_id": {"type": "string", "required": true},
    "task_id": {"type": "string", "required": true},
    "due_date": {"type": "string", "required": true, "format": "date-time"},
    "reminder_time": {"type": "string", "required": false, "format": "date-time"}
  },
  "returns": {
    "task_id": "string",
    "due_date": "string (ISO 8601)",
    "reminder_time": "string (ISO 8601) | null"
  }
}
```
