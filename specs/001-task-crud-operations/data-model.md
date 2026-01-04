# Data Model: Task CRUD Operations - Phase I

**Feature**: 001-task-crud-operations
**Date**: 2026-01-03
**Spec**: [spec.md](./spec.md)
**Plan**: [plan.md](./plan.md)

---

## Overview

Phase I implements a single domain entity (`Task`) with a simple state machine (`pending → complete`) and no relationships to other entities. The data model is designed for in-memory storage with future database migration in mind (Phase II).

**Key Characteristics**:
- **Entities**: 1 (Task)
- **Relationships**: None (single entity)
- **State Transitions**: `pending → complete` (one-way)
- **Persistence**: In-memory dictionary (`Dict[str, Task]`)
- **ID Strategy**: UUID4 (globally unique, future-proof)

---

## Entities

### Task Entity

**Purpose**: Represents a single todo item with title, description, status, and timestamps.

**Source**: Spec Domain Model section (spec.md lines 225-254)

#### Attributes

| Attribute | Type | Constraints | Default | Mutability | Description |
|-----------|------|-------------|---------|------------|-------------|
| `id` | str (UUID4) | Required, unique, format: UUID4 | Auto-generated | Immutable | Globally unique task identifier |
| `title` | str | Required, 1-200 chars, trimmed | User-provided | Mutable | Task title (primary label) |
| `description` | str | Optional, 0-2000 chars, auto-truncated | "" (empty string) | Mutable | Detailed task description |
| `status` | Literal["pending", "complete"] | Required, enum constraint | "pending" | Mutable (one-way) | Task completion status |
| `created_at` | datetime | Required, ISO 8601 | `datetime.now()` | Immutable | Task creation timestamp |
| `updated_at` | datetime | Required, ISO 8601 | `datetime.now()` | Mutable (auto-updated) | Last modification timestamp |
| `completed_at` | Optional[datetime] | Optional, ISO 8601 | None | Immutable after set | Task completion timestamp |

#### Validation Rules

**Title Validation (Invariants 1-2)**:
- **Non-Emptiness**: Title must be non-empty after trimming whitespace
  - **Rule**: `title.strip() != ""`
  - **Violation**: Raises `DomainValidationError("Title cannot be empty")`
- **Length**: Title must not exceed 200 characters
  - **Rule**: `len(title) ≤ 200`
  - **Violation**: Raises `DomainValidationError("Title cannot exceed 200 characters")`
- **Trimming**: Leading/trailing whitespace automatically trimmed before validation

**Description Validation (Invariant 3)**:
- **Length**: Description must not exceed 2000 characters
  - **Rule**: `len(description) ≤ 2000`
  - **Behavior**: Auto-truncate to 2000 chars if exceeded
  - **Warning**: Log warning message if truncation occurs

**Status Validation (Invariant 4)**:
- **Constraint**: Status must be either "pending" or "complete"
  - **Rule**: `status ∈ {"pending", "complete"}`
  - **Enforcement**: Type hint `Literal["pending", "complete"]` + runtime validation

**State Transition Validation (Invariant 5)**:
- **One-Way Transition**: Only `pending → complete` allowed (no reverse)
  - **Rule**: If `status == "complete"`, cannot call `mark_complete()` again
  - **Violation**: Raises `DomainStateError("Task is already complete")`

#### Timestamp Rules

**Created Timestamp (Invariant 7)**:
- Set once at task creation: `created_at = datetime.now()`
- **Immutability**: No setter method, never modified after creation

**Updated Timestamp (Invariant 8)**:
- Set at creation: `updated_at = datetime.now()`
- **Auto-Update**: Updated automatically when `title` or `description` changes
- **Methods**: `update_title()`, `update_description()` set `updated_at = datetime.now()`

**Completed Timestamp (Invariant 9)**:
- Default: `completed_at = None` (pending tasks)
- **Set Once**: Set to `datetime.now()` when `mark_complete()` called
- **Immutability**: Never modified after being set

#### Methods

**Constructor**:
```python
__init__(title: str, description: str = "") -> None
```
- Validates title (non-empty, ≤ 200 chars)
- Auto-truncates description if > 2000 chars
- Generates UUID4 for `id`
- Sets `status = "pending"`
- Sets `created_at = updated_at = datetime.now()`
- Sets `completed_at = None`

**Title Update**:
```python
update_title(new_title: str) -> None
```
- Validates new title (non-empty, ≤ 200 chars)
- Trims whitespace from new title
- Updates `title = new_title.strip()`
- Updates `updated_at = datetime.now()`

**Description Update**:
```python
update_description(new_description: str) -> None
```
- Auto-truncates if > 2000 chars
- Logs warning if truncation occurs
- Updates `description = new_description[:2000]`
- Updates `updated_at = datetime.now()`

**Mark Complete**:
```python
mark_complete() -> None
```
- Validates current status is "pending"
- Sets `status = "complete"`
- Sets `completed_at = datetime.now()`
- Does NOT update `updated_at` (completion is a status change, not a field modification)

**Serialization**:
```python
to_dict() -> dict
```
- Returns dictionary representation for storage/display
- Converts datetime objects to ISO 8601 strings

---

## State Machine

### Task Lifecycle

```
┌─────────┐
│ Created │
└────┬────┘
     │
     v
┌─────────────┐  mark_complete()  ┌───────────┐
│   pending   │ ─────────────────> │ complete  │
│ [ ] status  │                    │ [✓] status│
└─────────────┘                    └───────────┘
     ^                                    │
     │                                    │
     └────────────────────────────────────┘
           NO REVERSE TRANSITION
           (Invariant 5 violation)
```

**States**:
1. **pending**: Task created but not completed
   - `status = "pending"`
   - `completed_at = None`
   - Can transition to `complete`

2. **complete**: Task marked as done
   - `status = "complete"`
   - `completed_at = <timestamp>`
   - **Terminal state**: No transitions allowed

**State Transition Rules**:
- **Allowed**: `pending → complete` via `mark_complete()`
- **Prohibited**: `complete → pending` (no uncomplete operation)
- **Idempotency**: Calling `mark_complete()` on complete task raises `DomainStateError`

---

## Domain Exceptions

### Exception Hierarchy

```
Exception (Python built-in)
├── DomainValidationError       # Input validation failures
│   ├── Empty title
│   ├── Title > 200 chars
│   └── (Description auto-truncates, no exception)
├── DomainStateError            # Invalid state transitions
│   └── Marking complete task complete
└── TaskNotFoundError           # Task ID not found in storage
```

### Exception Details

**DomainValidationError**:
- **Purpose**: Raised when user input violates domain invariants
- **Trigger Scenarios**:
  - Title is empty after trimming whitespace
  - Title exceeds 200 characters
  - (Note: Description does NOT raise exception, auto-truncates instead)
- **Message Format**: User-friendly (e.g., "Title cannot be empty")

**DomainStateError**:
- **Purpose**: Raised when attempting invalid state transition
- **Trigger Scenarios**:
  - Calling `mark_complete()` on task with `status = "complete"`
- **Message Format**: User-friendly (e.g., "Task is already complete")

**TaskNotFoundError**:
- **Purpose**: Raised when task ID not found in storage
- **Trigger Scenarios**:
  - `repository.get(invalid_id)` returns None, operations fail
  - User attempts to view/update/complete/delete non-existent task
- **Message Format**: User-friendly (e.g., "Task not found")

---

## Relationships

**Phase I**: No relationships (single entity)

**Phase II Future Relationships** (not implemented in Phase I):
- User ↔ Task (one-to-many): One user owns many tasks
- Category ↔ Task (one-to-many): One category contains many tasks
- Tag ↔ Task (many-to-many): Tasks can have multiple tags

**Phase I Constraint**: All tasks belong to single implicit user (no user_id field)

---

## Storage Strategy

### In-Memory Storage (Phase I)

**Data Structure**: `Dict[str, Task]`
- **Key**: `task.id` (UUID4 string)
- **Value**: `Task` object (full entity)

**Operations**:
- `add(task)`: `storage[task.id] = task`
- `get(task_id)`: `storage.get(task_id)` (returns None if not found)
- `get_all()`: `sorted(storage.values(), key=lambda t: t.created_at, reverse=True)`
- `update(task)`: `storage[task.id] = task` (replace entire object)
- `delete(task_id)`: `del storage[task_id]`
- `exists(task_id)`: `task_id in storage`

**Sorting**: Tasks sorted by `created_at` DESC (newest first) in `get_all()`

### Future Database Storage (Phase II)

**Target**: PostgreSQL via Neon DB (serverless)

**Migration Strategy**:
1. Create `tasks` table with 7 columns matching Task attributes
2. Add `user_id` column for multi-user support
3. Implement `PostgresRepository` class implementing same `RepositoryInterface`
4. Swap `MemoryRepository` → `PostgresRepository` in `main.py` (one-line change)

**Schema Preview (Phase II)**:
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'complete')),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

---

## Invariant Summary

**10 NON-NEGOTIABLE Domain Invariants** (spec.md lines 227-248):

1. **Title Non-Emptiness**: `Task.title` must be non-empty after trimming
2. **Title Length**: `Task.title` ≤ 200 characters
3. **Description Length**: `Task.description` ≤ 2000 characters (auto-truncate)
4. **Status Constraint**: `Task.status` ∈ {"pending", "complete"}
5. **State Transition**: Only `pending → complete` allowed (no reverse)
6. **ID Uniqueness**: Every `Task.id` globally unique via UUID4
7. **Created Timestamp Immutability**: `Task.created_at` set once, never modified
8. **Updated Timestamp**: `Task.updated_at` updated on title/description changes
9. **Completed Timestamp**: `Task.completed_at` = None when pending, set when complete
10. **Deletion Integrity**: Deletion removes from storage, Task object unchanged

---

## Design Rationale

### Why UUID4 for IDs?
- **User-Approved**: Selected during specification creation
- **Global Uniqueness**: No collisions across distributed systems (Phase II+)
- **Future-Proof**: Enables offline task creation (Phase III AI agents)
- **No Coordination**: No need for centralized ID generation

### Why Auto-Truncate Descriptions?
- **User-Friendly**: No hard rejection, better UX
- **Observability**: Log warning when truncation occurs
- **Data Integrity**: Prevents database constraint violations (Phase II)

### Why One-Way State Transition?
- **Simplicity**: Todo apps rarely need "uncomplete" operation
- **Audit Trail**: Phase II will add history tracking, one-way preserves intent
- **Spec Requirement**: Out of Scope explicitly excludes audit log/history (spec.md line 414)

### Why Separate updated_at and completed_at?
- **Clarity**: Distinguish "when modified" from "when completed"
- **Query Optimization**: Phase II can query recently completed tasks separately
- **Analytics**: Phase II can analyze completion time vs. modification time

---

**Data Model Status**: Approved and ready for implementation via `/sp.tasks` → `/sp.implement`
