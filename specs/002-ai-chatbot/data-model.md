# Data Model — AI-Powered Conversational Todo Management

**Feature Branch**: `002-ai-chatbot`
**Created**: 2026-01-31
**Spec**: [spec.md](./spec.md)

---

## Overview

Phase III introduces 5 new database tables and extends the existing `tasks` table with a `due_date` column. All new tables follow Phase II conventions: UUID primary keys, UTC timestamps, user isolation via `user_id` foreign keys, and ON DELETE CASCADE for referential integrity.

**Migration Plan**: Alembic migrations 009–014 (one per new table + one for task extension).

---

## Entity Relationship Diagram

```
users (Phase II)
  │
  ├── 1:N ── conversations
  │             │
  │             └── 1:N ── messages
  │
  ├── 1:N ── tasks (Phase II, extended)
  │             │
  │             ├── 1:1 ── recurrence_rules
  │             │
  │             └── 1:1 ── reminder_metadata
  │
  └── 1:N ── push_subscriptions
```

---

## New Tables

### 1. Conversation

Represents a chat session owned by a user.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Unique conversation identifier |
| `user_id` | VARCHAR(64) | NOT NULL, FK→users.id, INDEX | Owning user |
| `title` | VARCHAR(200) | NULLABLE | Auto-generated from first message |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation time |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last activity time |

**Constraints**:
- ON DELETE CASCADE from `users.id` (deleting user removes all conversations)
- INDEX on `user_id` for user isolation queries
- INDEX on `(user_id, updated_at DESC)` for conversation listing sorted by recent activity

**SQLModel Definition**:

```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(foreign_key="users.id", nullable=False, index=True, max_length=64)
    title: str | None = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
```

**Alembic Migration**: `009_create_conversations_table.py`

---

### 2. Message

Represents a single chat message within a conversation.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Unique message identifier |
| `conversation_id` | UUID | NOT NULL, FK→conversations.id, INDEX | Parent conversation |
| `user_id` | VARCHAR(64) | NOT NULL, INDEX | Owning user (denormalized for query efficiency) |
| `role` | VARCHAR(20) | NOT NULL, CHECK (role IN ('user', 'assistant')) | Message author role |
| `content` | TEXT | NOT NULL | Message text content |
| `tool_calls` | JSONB | NULLABLE | Structured tool invocation data |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Message timestamp |

**Constraints**:
- ON DELETE CASCADE from `conversations.id` (deleting conversation removes all messages)
- CHECK constraint on `role`: must be `'user'` or `'assistant'`
- INDEX on `(conversation_id, created_at DESC)` for context window queries (last 7 messages)
- INDEX on `user_id` for user isolation

**`tool_calls` JSONB Structure**:

```json
[
  {
    "tool": "create_task",
    "input": {"title": "buy groceries", "priority": "medium"},
    "output": {"task_id": "uuid-here", "status": "pending"},
    "duration_ms": 150
  }
]
```

**SQLModel Definition**:

```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", nullable=False, index=True)
    user_id: str = Field(nullable=False, index=True, max_length=64)
    role: str = Field(nullable=False, max_length=20)
    content: str = Field(nullable=False)
    tool_calls: dict | None = Field(default=None, sa_column=Column(JSONB, nullable=True))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
```

**Alembic Migration**: `010_create_messages_table.py`

---

### 3. RecurrenceRule

Represents a repeating schedule attached to a task (one-to-one).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Unique rule identifier |
| `task_id` | UUID | NOT NULL, UNIQUE, FK→tasks.id | Parent task (one-to-one) |
| `frequency` | VARCHAR(20) | NOT NULL, CHECK | Recurrence type |
| `interval` | INTEGER | NOT NULL, DEFAULT 1, CHECK (>= 1) | Every N occurrences |
| `days_of_week` | INTEGER[] | NULLABLE | Days for weekly recurrence (0=Mon, 6=Sun) |
| `day_of_month` | INTEGER | NULLABLE, CHECK (1-31) | Day for monthly recurrence |
| `end_date` | DATE | NULLABLE | Optional end date for recurrence |
| `next_occurrence` | TIMESTAMPTZ | NOT NULL, INDEX | Calculated next trigger time |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation time |

**Constraints**:
- ON DELETE CASCADE from `tasks.id` (deleting task removes recurrence rule)
- UNIQUE on `task_id` (one rule per task)
- CHECK on `frequency`: must be IN ('daily', 'weekly', 'monthly', 'yearly')
- CHECK on `interval`: must be >= 1
- CHECK on `day_of_month`: must be between 1 and 31
- INDEX on `next_occurrence` for scheduler queries (find due recurrences)

**SQLModel Definition**:

```python
class RecurrenceRule(SQLModel, table=True):
    __tablename__ = "recurrence_rules"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    task_id: uuid.UUID = Field(foreign_key="tasks.id", nullable=False, unique=True)
    frequency: str = Field(nullable=False, max_length=20)
    interval: int = Field(default=1, nullable=False)
    days_of_week: list[int] | None = Field(default=None, sa_column=Column(ARRAY(Integer), nullable=True))
    day_of_month: int | None = Field(default=None)
    end_date: date | None = Field(default=None)
    next_occurrence: datetime = Field(nullable=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
```

**Alembic Migration**: `011_create_recurrence_rules_table.py`

---

### 4. ReminderMetadata

Represents due date and notification tracking for a task (one-to-one).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Unique reminder identifier |
| `task_id` | UUID | NOT NULL, UNIQUE, FK→tasks.id | Parent task (one-to-one) |
| `due_date` | TIMESTAMPTZ | NULLABLE | Task deadline |
| `reminder_time` | TIMESTAMPTZ | NULLABLE | When to send notification |
| `notification_sent` | BOOLEAN | NOT NULL, DEFAULT FALSE | Prevents duplicate notifications |
| `snooze_until` | TIMESTAMPTZ | NULLABLE | Snoozed reminder time |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation time |

**Constraints**:
- ON DELETE CASCADE from `tasks.id` (deleting task removes reminder)
- UNIQUE on `task_id` (one reminder per task)
- CHECK: at least one of `due_date` or `reminder_time` must be NOT NULL
- INDEX on `(reminder_time, notification_sent)` for scheduler queries (find unsent reminders)
- INDEX on `due_date` for date range queries (FR-039)

**SQLModel Definition**:

```python
class ReminderMetadata(SQLModel, table=True):
    __tablename__ = "reminder_metadata"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    task_id: uuid.UUID = Field(foreign_key="tasks.id", nullable=False, unique=True)
    due_date: datetime | None = Field(default=None)
    reminder_time: datetime | None = Field(default=None)
    notification_sent: bool = Field(default=False, nullable=False)
    snooze_until: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
```

**Alembic Migration**: `012_create_reminder_metadata_table.py`

---

### 5. PushSubscription

Represents a browser push notification subscription per user per device.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Unique subscription identifier |
| `user_id` | VARCHAR(64) | NOT NULL, FK→users.id, INDEX | Owning user |
| `endpoint` | VARCHAR(500) | NOT NULL, UNIQUE | Push service endpoint URL |
| `keys` | JSONB | NOT NULL | Encryption keys (p256dh, auth) |
| `device_info` | JSONB | NULLABLE | Optional device/browser metadata |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Subscription time |

**Constraints**:
- ON DELETE CASCADE from `users.id` (deleting user removes subscriptions)
- UNIQUE on `endpoint` (one subscription per push endpoint)
- INDEX on `user_id` for finding user's subscriptions

**`keys` JSONB Structure**:

```json
{
  "p256dh": "base64-encoded-public-key",
  "auth": "base64-encoded-auth-secret"
}
```

**SQLModel Definition**:

```python
class PushSubscription(SQLModel, table=True):
    __tablename__ = "push_subscriptions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(foreign_key="users.id", nullable=False, index=True, max_length=64)
    endpoint: str = Field(nullable=False, unique=True, max_length=500)
    keys: dict = Field(sa_column=Column(JSONB, nullable=False))
    device_info: dict | None = Field(default=None, sa_column=Column(JSONB, nullable=True))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
```

**Alembic Migration**: `013_create_push_subscriptions_table.py`

---

## Existing Table Extension

### Task Table (ALTER)

Add `due_date` column to the existing `tasks` table from Phase II.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `due_date` | TIMESTAMPTZ | NULLABLE | Task deadline (optional) |

**New Index**: `(user_id, due_date)` for date range queries per user.

**Alembic Migration**: `014_add_due_date_to_tasks.py`

```sql
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMPTZ;
CREATE INDEX ix_tasks_user_id_due_date ON tasks (user_id, due_date);
```

---

## Migration Summary

| Migration | Table | Action |
|-----------|-------|--------|
| 009 | conversations | CREATE TABLE |
| 010 | messages | CREATE TABLE |
| 011 | recurrence_rules | CREATE TABLE |
| 012 | reminder_metadata | CREATE TABLE |
| 013 | push_subscriptions | CREATE TABLE |
| 014 | tasks | ALTER TABLE (add due_date + index) |

**Rollback Strategy**: Each migration has a corresponding `downgrade()` that drops the table/column. Migrations are independent and can be rolled back individually in reverse order.

---

## Query Patterns

### Context Window (7 messages)

```sql
SELECT role, content, tool_calls, created_at
FROM messages
WHERE conversation_id = :conv_id
ORDER BY created_at DESC
LIMIT 7;
-- Results reversed in application code for chronological order
```

### Conversation Listing

```sql
SELECT c.id, c.title, c.updated_at,
       (SELECT content FROM messages m
        WHERE m.conversation_id = c.id
        ORDER BY m.created_at DESC LIMIT 1) AS last_message
FROM conversations c
WHERE c.user_id = :user_id
ORDER BY c.updated_at DESC;
```

### Due Recurrences

```sql
SELECT r.*, t.title, t.user_id
FROM recurrence_rules r
JOIN tasks t ON r.task_id = t.id
WHERE r.next_occurrence <= NOW()
  AND (r.end_date IS NULL OR r.end_date >= CURRENT_DATE);
```

### Pending Reminders

```sql
SELECT rm.*, t.title, t.user_id
FROM reminder_metadata rm
JOIN tasks t ON rm.task_id = t.id
WHERE rm.reminder_time <= NOW()
  AND rm.notification_sent = FALSE
  AND (rm.snooze_until IS NULL OR rm.snooze_until <= NOW());
```

### Overdue Tasks

```sql
SELECT t.*
FROM tasks t
JOIN reminder_metadata rm ON t.id = rm.task_id
WHERE rm.due_date < NOW()
  AND t.status = 'PENDING'
  AND t.user_id = :user_id;
```
