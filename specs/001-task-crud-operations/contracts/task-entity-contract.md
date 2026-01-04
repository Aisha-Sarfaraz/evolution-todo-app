# Task Entity Contract

**Feature**: 001-task-crud-operations
**Date**: 2026-01-03
**Type**: Domain Entity Contract
**Spec**: [../spec.md](../spec.md)
**Data Model**: [../data-model.md](../data-model.md)

---

## Contract Overview

This document defines the public API contract for the `Task` domain entity. All implementations of the Task entity MUST conform to this contract to ensure consistency across layers (domain, storage, CLI).

**Contract Authority**: This contract is derived from the approved specification (spec.md) and is the authoritative definition of Task entity behavior.

**Compliance**: Test Strategy Architect agent validates all Task implementations against this contract.

---

## Entity Signature

```python
from datetime import datetime
from typing import Literal, Optional

class Task:
    """
    Domain entity representing a todo task with title, description, status, and timestamps.

    Invariants (NON-NEGOTIABLE):
    - Title: non-empty after trim, ≤ 200 chars
    - Description: ≤ 2000 chars (auto-truncate)
    - Status: "pending" | "complete" only
    - State transition: pending → complete only (no reverse)
    - Timestamps: created_at immutable, updated_at auto-updated, completed_at immutable after set
    """

    # Attributes (read-only access, modified via methods)
    id: str                                    # UUID4, immutable
    title: str                                 # Required, 1-200 chars, trimmed
    description: str                           # Optional, 0-2000 chars, auto-truncated
    status: Literal["pending", "complete"]     # Enum constraint
    created_at: datetime                       # ISO 8601, immutable
    updated_at: datetime                       # ISO 8601, auto-updated on title/description change
    completed_at: Optional[datetime]           # None when pending, set when complete, immutable after
```

---

## Constructor Contract

### `__init__(title: str, description: str = "") -> None`

**Purpose**: Create new Task entity with validated title and description.

**Preconditions**:
- `title` parameter provided (required)
- `description` parameter optional (defaults to empty string)

**Postconditions**:
- `id`: Auto-generated UUID4 (str format)
- `title`: Trimmed, validated (non-empty, ≤ 200 chars)
- `description`: Auto-truncated if > 2000 chars, warning logged if truncated
- `status`: Set to "pending"
- `created_at`: Set to `datetime.now()`
- `updated_at`: Set to `datetime.now()` (same as created_at initially)
- `completed_at`: Set to `None`

**Exceptions**:
- `DomainValidationError`: Raised if title is empty after trimming whitespace
- `DomainValidationError`: Raised if title exceeds 200 characters

**Examples**:

```python
# Valid creation
task = Task(title="Buy groceries", description="Get milk, eggs")
assert task.id is not None
assert task.title == "Buy groceries"
assert task.status == "pending"
assert task.completed_at is None

# Whitespace trimming
task = Task(title="  Clean room  ", description="")
assert task.title == "Clean room"  # Leading/trailing whitespace trimmed

# Description auto-truncation
long_desc = "x" * 2500
task = Task(title="Long task", description=long_desc)
assert len(task.description) == 2000  # Auto-truncated to 2000 chars

# Validation failures
try:
    task = Task(title="", description="test")
except DomainValidationError as e:
    assert str(e) == "Title cannot be empty"

try:
    task = Task(title="x" * 201, description="test")
except DomainValidationError as e:
    assert str(e) == "Title cannot exceed 200 characters"
```

---

## Method Contracts

### `update_title(new_title: str) -> None`

**Purpose**: Update task title with validation and timestamp update.

**Preconditions**:
- `new_title` parameter provided (required)
- Task exists (can be pending or complete)

**Postconditions**:
- `title`: Updated to `new_title.strip()` after validation
- `updated_at`: Set to `datetime.now()`
- All other attributes unchanged

**Exceptions**:
- `DomainValidationError`: Raised if new_title is empty after trimming
- `DomainValidationError`: Raised if new_title exceeds 200 characters

**Invariants Enforced**:
- Invariant 1 (Title Non-Emptiness)
- Invariant 2 (Title Length)
- Invariant 8 (Updated Timestamp)

**Examples**:

```python
task = Task(title="Original", description="test")
original_updated_at = task.updated_at

task.update_title("Updated Title")
assert task.title == "Updated Title"
assert task.updated_at > original_updated_at

# Validation failure
try:
    task.update_title("   ")  # Whitespace-only
except DomainValidationError as e:
    assert str(e) == "Title cannot be empty"
```

---

### `update_description(new_description: str) -> None`

**Purpose**: Update task description with auto-truncation and timestamp update.

**Preconditions**:
- `new_description` parameter provided (required, can be empty string)
- Task exists (can be pending or complete)

**Postconditions**:
- `description`: Updated to `new_description[:2000]` (auto-truncated if > 2000 chars)
- `updated_at`: Set to `datetime.now()`
- Warning logged if description truncated
- All other attributes unchanged

**Exceptions**: None (auto-truncates instead of raising exception)

**Invariants Enforced**:
- Invariant 3 (Description Length)
- Invariant 8 (Updated Timestamp)

**Examples**:

```python
task = Task(title="Test", description="Original")
original_updated_at = task.updated_at

task.update_description("Updated description")
assert task.description == "Updated description"
assert task.updated_at > original_updated_at

# Auto-truncation
long_desc = "y" * 2500
task.update_description(long_desc)
assert len(task.description) == 2000  # Truncated, no exception
```

---

### `mark_complete() -> None`

**Purpose**: Transition task from pending to complete state.

**Preconditions**:
- `status` is "pending" (raises exception if already complete)

**Postconditions**:
- `status`: Set to "complete"
- `completed_at`: Set to `datetime.now()`
- `updated_at`: Unchanged (completion is status change, not field modification)
- All other attributes unchanged

**Exceptions**:
- `DomainStateError`: Raised if task already has `status = "complete"`

**Invariants Enforced**:
- Invariant 5 (State Transition)
- Invariant 9 (Completed Timestamp)

**Examples**:

```python
task = Task(title="Pending task", description="test")
assert task.status == "pending"
assert task.completed_at is None

task.mark_complete()
assert task.status == "complete"
assert task.completed_at is not None

# Idempotency violation
try:
    task.mark_complete()  # Already complete
except DomainStateError as e:
    assert str(e) == "Task is already complete"
```

---

### `to_dict() -> dict`

**Purpose**: Serialize task to dictionary format for storage/display.

**Preconditions**: None

**Postconditions**:
- Returns dictionary with all 7 attributes
- `datetime` objects converted to ISO 8601 strings
- `completed_at` is None if task is pending

**Exceptions**: None

**Return Type**:
```python
{
    "id": str,
    "title": str,
    "description": str,
    "status": str,  # "pending" or "complete"
    "created_at": str,  # ISO 8601 format
    "updated_at": str,  # ISO 8601 format
    "completed_at": str | None  # ISO 8601 or None
}
```

**Examples**:

```python
task = Task(title="Test task", description="Test")
task_dict = task.to_dict()

assert task_dict["id"] == task.id
assert task_dict["title"] == "Test task"
assert task_dict["status"] == "pending"
assert task_dict["completed_at"] is None
assert isinstance(task_dict["created_at"], str)  # ISO 8601 string

task.mark_complete()
task_dict = task.to_dict()
assert task_dict["status"] == "complete"
assert task_dict["completed_at"] is not None  # ISO 8601 string
```

---

## Attribute Access Contract

### Read-Only Attributes

**Contract**: All attributes are read-only from external code. Modification MUST occur via entity methods only.

**Allowed**:
```python
task = Task(title="Test", description="desc")

# Reading attributes (ALLOWED)
task_id = task.id
task_title = task.title
task_status = task.status
task_created = task.created_at
```

**Prohibited**:
```python
# Direct attribute modification (PROHIBITED)
task.title = "New title"  # Use update_title() instead
task.status = "complete"  # Use mark_complete() instead
task.updated_at = datetime.now()  # Auto-updated by methods
```

**Rationale**: Encapsulation ensures invariants are always enforced. Direct attribute modification bypasses validation.

---

## Invariant Enforcement Matrix

| Invariant | Enforced By | Violation Behavior |
|-----------|-------------|-------------------|
| 1. Title Non-Emptiness | `__init__`, `update_title()` | Raises `DomainValidationError` |
| 2. Title Length | `__init__`, `update_title()` | Raises `DomainValidationError` |
| 3. Description Length | `__init__`, `update_description()` | Auto-truncate to 2000 chars, log warning |
| 4. Status Constraint | Type hint `Literal["pending", "complete"]` | Type checker catches at development time |
| 5. State Transition | `mark_complete()` | Raises `DomainStateError` if already complete |
| 6. ID Uniqueness | UUID4 generation | Collision probability negligible (2^-122) |
| 7. Created Immutability | No setter method | Attribute is read-only |
| 8. Updated Timestamp | `update_title()`, `update_description()` | Auto-set to `datetime.now()` |
| 9. Completed Timestamp | `mark_complete()` | Set once, no setter method afterward |
| 10. Deletion Integrity | Storage layer (repository) | Task object unchanged, only storage affected |

---

## Exception Contracts

### DomainValidationError

**When Raised**:
- Empty title after trimming (`__init__`, `update_title()`)
- Title exceeds 200 characters (`__init__`, `update_title()`)

**Message Format**: User-friendly string (e.g., "Title cannot be empty")

**Handling**: CLI layer catches and displays with `✗` prefix

---

### DomainStateError

**When Raised**:
- Attempting `mark_complete()` on task with `status = "complete"`

**Message Format**: User-friendly string (e.g., "Task is already complete")

**Handling**: CLI layer catches and displays with `✗` prefix

---

### TaskNotFoundError

**When Raised**:
- Storage layer operation fails (task ID not found)
- Not raised by Task entity directly (raised by repository)

**Message Format**: User-friendly string (e.g., "Task not found")

**Handling**: CLI layer catches and displays with `✗` prefix

---

## Type Hints Contract

**Contract**: All public methods MUST have type hints for all parameters and return values.

**Required Type Hints**:
- `__init__(title: str, description: str = "") -> None`
- `update_title(new_title: str) -> None`
- `update_description(new_description: str) -> None`
- `mark_complete() -> None`
- `to_dict() -> dict`

**Validation**: `mypy` type checker validates all type hints in strict mode.

---

## Logging Contract

**Contract**: Task entity MUST log warnings when auto-truncating descriptions.

**Log Format**:
```python
{
    "timestamp": "2026-01-03T10:30:00Z",
    "level": "WARNING",
    "service": "todo-cli",
    "message": "Description truncated to 2000 characters",
    "context": {
        "task_id": "550e8400",
        "original_length": 2500,
        "truncated_length": 2000
    }
}
```

**Trigger**: Description length > 2000 chars in `__init__()` or `update_description()`

---

## Testing Contract

**Contract**: Task entity MUST be tested with 35-40 unit tests covering all invariants and edge cases.

**Required Test Coverage**:
- `test_task_entity.py`: 12 tests (creation, validation, timestamps)
- `test_task_lifecycle.py`: 15 tests (updates, completion, timestamps)
- `test_task_validation.py`: 10 tests (Unicode, special chars, edge cases)

**Minimum Coverage**: 80% code coverage (enforced by pytest-cov)

**Test Framework**: pytest with type validation (mypy)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-03 | Initial contract based on approved specification |

---

## Contract Compliance

**Validation Method**: Test Strategy Architect agent validates all Task implementations against this contract during `/sp.implement` workflow.

**Non-Compliance**: Blocks merge if implementation violates any contract requirement.

**Amendment Process**: Contract changes require specification update (sp.specify → sp.clarify → sp.plan workflow) and version increment.

---

**Contract Status**: Approved and ready for implementation via `/sp.tasks` → `/sp.implement`
