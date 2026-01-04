# Feature Specification: Task CRUD Operations

**Feature Branch**: `001-task-crud-operations`
**Created**: 2026-01-02
**Status**: Draft
**Phase**: I - In-Memory Console Application

---

## Constitutional Alignment

This specification complies with Constitution v1.0.0:
- **Principle I (SDD)**: Specification created before implementation
- **Principle III (TDD)**: All acceptance criteria include test scenarios
- **Principle IV (Separation)**: Domain/CLI/Storage layers clearly defined
- **Principle VI (Observability)**: Structured logging requirements included

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Task (Priority: P1)

User wants to add a new task to track work.

**Why this priority**: Foundation for all other operations - must create before view/update/complete/delete

**Independent Test**: Run app, create 3 tasks with different titles/descriptions, verify tasks exist in memory

**Acceptance Scenarios**:

1. **Given** empty task list, **When** user creates task with title "Buy groceries" and description "Get milk", **Then** task created with unique UUID, status "pending", and current timestamp
2. **Given** user in create menu, **When** user enters empty title, **Then** system rejects with error "Title cannot be empty"
3. **Given** user enters title with 201 characters, **Then** system rejects with error "Title cannot exceed 200 characters"
4. **Given** user enters description with 2001 characters, **Then** system auto-truncates to 2000 chars and shows warning
5. **Given** user enters title with leading/trailing whitespace, **Then** system trims whitespace before validation
6. **Given** user enters title with Unicode characters (café ☕), **Then** system accepts and stores correctly

---

### User Story 2 - View Tasks (Priority: P2)

User wants to see all tasks or view a specific task's details.

**Why this priority**: Required to verify Create (P1) worked, provides visibility into task list

**Independent Test**: Create 3 tasks (P1), view list, verify all 3 displayed with correct status/title

**Acceptance Scenarios**:

1. **Given** 0 tasks exist, **When** user views all tasks, **Then** system displays "No tasks found"
2. **Given** 5 tasks exist, **When** user views all tasks, **Then** system displays compact list (ID, Status, Title, Created) sorted newest first
3. **Given** task list displayed, **When** user enters task ID, **Then** system shows full details (ID, Title, Description, Status, Created, Completed, Updated)
4. **Given** task has description > 100 chars, **When** viewing list, **Then** description truncated to 50 chars with "..."
5. **Given** task has status "complete", **When** viewing list, **Then** task shows [✓] indicator
6. **Given** task has status "pending", **When** viewing list, **Then** task shows [ ] indicator

---

### User Story 3 - Update Task (Priority: P3)

User wants to edit task title or description.

**Why this priority**: Adds flexibility but not critical (user can delete and recreate)

**Independent Test**: Create task (P1), update title from "Old" to "New", view task (P2), verify change persisted

**Acceptance Scenarios**:

1. **Given** task exists, **When** user updates title to "New title", **Then** task.title = "New title" and task.updated_at = current timestamp
2. **Given** task exists, **When** user updates description only, **Then** description changes, title unchanged, updated_at updated
3. **Given** task exists, **When** user updates both title and description, **Then** both fields updated, updated_at updated
4. **Given** task exists, **When** user enters empty title on update, **Then** system rejects with error
5. **Given** task does not exist, **When** user enters invalid task ID, **Then** system returns "Task not found" error
6. **Given** user in update menu, **When** user presses Enter without typing, **Then** field remains unchanged ("keep current value")
7. **Given** task is completed, **When** user updates title, **Then** update allowed (completed tasks are editable)
8. **Given** user starts update, **When** user presses Ctrl+C, **Then** operation cancelled, return to main menu

---

### User Story 4 - Mark Task Complete (Priority: P4)

User wants to mark a task as done.

**Why this priority**: Core value of todo apps - completion tracking

**Independent Test**: Create pending task (P1), mark complete (P4), view task (P2), verify status changed to "complete"

**Acceptance Scenarios**:

1. **Given** task with status "pending", **When** user marks complete, **Then** status = "complete", completed_at = current timestamp
2. **Given** task with status "complete", **When** user tries to mark complete again, **Then** system rejects with error "Task is already complete"
3. **Given** task does not exist, **When** user enters invalid task ID, **Then** system returns "Task not found" error
4. **Given** task marked complete, **When** viewing in list, **Then** task shows [✓] indicator
5. **Given** multiple tasks exist, **When** user marks one complete, **Then** only that task changes, others unchanged

---

### User Story 5 - Delete Task (Priority: P5)

User wants to remove a task permanently.

**Why this priority**: Lowest value - users can ignore unwanted tasks

**Independent Test**: Create 3 tasks (P1), delete middle task (P5), view list (P2), verify only 2 tasks remain

**Acceptance Scenarios**:

1. **Given** task exists, **When** user confirms deletion (y), **Then** task removed from storage, no longer appears in list
2. **Given** task exists, **When** user declines deletion (n), **Then** task remains, return to main menu
3. **Given** task does not exist, **When** user enters invalid task ID, **Then** system returns "Task not found" error
4. **Given** user deletes last task, **When** viewing list, **Then** system displays "No tasks found"
5. **Given** task is completed, **When** user deletes, **Then** deletion allowed (can delete completed tasks)
6. **Given** 3 tasks exist, **When** user deletes task 2, **Then** task 1 and 3 remain with original IDs (no ID reassignment)

---

### Edge Cases

**Input Boundaries:**
- Title exactly 200 chars (accept)
- Title 201 chars (reject)
- Description 2000 chars (accept)
- Description 2001 chars (truncate with warning)
- Whitespace-only title (reject after trim)
- Unicode characters in title/description (accept)

**Empty State:**
- View tasks when empty ("No tasks found")
- Mark complete when empty (error)
- Update when empty (error)
- Delete when empty (error)
- Delete last task (list becomes empty)

**Large Data:**
- Create 1000 tasks rapidly (all unique UUIDs)
- View 1000+ tasks (may be slow, no crash)
- 10,000 tasks memory test (< 100MB)

**Special Characters:**
- Emoji in title/description (accept)
- Newlines in description (preserve)
- Special chars ("#123 (urgent!)") (accept)

**Invalid Input:**
- Non-UUID task ID format (reject)
- Invalid menu option (re-prompt)
- Empty input when required (re-prompt)

**Other:**
- Ctrl+C cancellation (return to menu)
- Simultaneous task creation (all get unique IDs)

---

## Requirements *(mandatory)*

### Functional Requirements

**FR-001**: System MUST allow users to create tasks with title (required, max 200 chars) and description (optional, max 2000 chars)

**FR-002**: System MUST assign unique UUID4 to each task upon creation

**FR-003**: System MUST set task status to "pending" by default

**FR-004**: System MUST record creation timestamp (ISO 8601 format)

**FR-005**: System MUST display all tasks in list view sorted by created_at DESC (newest first)

**FR-006**: System MUST provide compact list view (ID, Status, Title, Created) and detailed view (all fields)

**FR-007**: System MUST allow users to update task title and/or description

**FR-008**: System MUST update "updated_at" timestamp on any field modification

**FR-009**: System MUST allow users to mark pending tasks as complete

**FR-010**: System MUST set "completed_at" timestamp when task marked complete

**FR-011**: System MUST prevent marking already-completed tasks as complete (idempotency)

**FR-012**: System MUST allow users to delete tasks (pending or complete)

**FR-013**: System MUST prompt for confirmation before deletion (y/n)

**FR-014**: System MUST validate all user inputs against domain invariants before persistence

**FR-015**: System MUST display user-friendly error messages (no stack traces)

### Key Entities

**Task Entity:**
- `id`: UUID4 (string, unique, immutable)
- `title`: String (required, 1-200 chars, trimmed)
- `description`: String (optional, 0-2000 chars, auto-truncated)
- `status`: Enum ("pending" | "complete")
- `created_at`: Datetime (ISO 8601, immutable)
- `updated_at`: Datetime (ISO 8601, updated on modifications)
- `completed_at`: Datetime | None (set when status → "complete")

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

**SC-001**: Users can create, view, update, complete, and delete tasks via console menu in < 2 minutes (usability test)

**SC-002**: All 5 CRUD operations complete within 100ms for task lists < 1000 items (performance benchmark)

**SC-003**: System achieves ≥80% unit test coverage across domain layer (pytest-cov report)

**SC-004**: Zero unhandled exceptions during normal operations (integration test suite)

**SC-005**: Application starts within 1 second on standard hardware (startup time test)

**SC-006**: All operations maintain data integrity (no ID collisions, no orphaned references) (stress test: 10,000 operations)

**SC-007**: Code passes ruff linting with zero errors (CI validation)

**SC-008**: All public methods have type hints and pass mypy validation (type check)

---

## Domain Model

### NON-NEGOTIABLE Domain Invariants

1. **Title Non-Emptiness**: `Task.title` must be non-empty after trimming whitespace (raises `DomainValidationError`)

2. **Title Length**: `Task.title` ≤ 200 characters (raises `DomainValidationError`)

3. **Description Length**: `Task.description` ≤ 2000 characters (auto-truncate if exceeded, log warning)

4. **Status Constraint**: `Task.status` ∈ {"pending", "complete"} only (enforced by enum/validation)

5. **State Transition**: Only `pending → complete` allowed, no reverse (raises `DomainStateError` if violated)

6. **ID Uniqueness**: Every `Task.id` globally unique via UUID4 (collision probability negligible)

7. **Created Timestamp Immutability**: `Task.created_at` set once at creation, never modified

8. **Updated Timestamp**: `Task.updated_at` updated on title/description changes

9. **Completed Timestamp**: `Task.completed_at` = None when pending, set when complete, immutable after

10. **Deletion Integrity**: Deletion removes from storage but doesn't mutate task object

### Domain Exceptions

- `DomainValidationError`: Input validation failures (empty title, length violations)
- `DomainStateError`: Invalid state transitions (marking complete task complete)
- `TaskNotFoundError`: Task ID not found in storage

---

## CLI Interaction Specification

### Main Menu Structure

```
=================================
    TODO APP - MAIN MENU
=================================
1. Create Task
2. View All Tasks
3. Update Task
4. Mark Task as Complete
5. Delete Task
6. Exit
=================================
Select an option (1-6): _
```

### Create Task Flow

```
Enter task title (max 200 chars): Buy groceries
Enter task description (optional, max 2000 chars): Get milk, eggs

✓ Task created successfully!
ID: 550e8400
Title: Buy groceries
Status: Pending
Created: 2026-01-02 10:30:00
```

### View All Tasks Flow

```
Total: 5 tasks (3 pending, 2 complete)

ID       Status   Title                    Created
-------- -------- ----------------------- -------------------
550e8400 [ ]      Team meeting            2026-01-02 11:00
a3b4c5d6 [✓]      Buy groceries           2026-01-02 10:45

Legend: [ ] = Pending  [✓] = Complete

Enter task ID to view details (or press Enter): _
```

### View Task Details Flow

```
ID: 550e8400
Title: Buy groceries
Description: Get milk, eggs, bread
Status: Pending [ ]
Created: 2026-01-02 10:45:33
Completed: N/A
Last Updated: 2026-01-02 10:45:33
```

### Update Task Flow

```
Enter task ID: 550e8400

Current Task:
  Title: Buy groceries
  Description: Get milk

Enter new title (or press Enter to keep): Buy organic groceries
Enter new description (or press Enter to keep): [Enter]

✓ Task updated successfully!
```

### Mark Complete Flow

```
Enter task ID: 550e8400

✓ Task "Buy groceries" marked as complete!
Completed at: 2026-01-02 14:22:18
```

### Delete Task Flow

```
Enter task ID: 550e8400

Task Details:
  ID: 550e8400
  Title: Buy groceries
  Status: Complete

⚠ Are you sure you want to delete this task? (y/n): y

✓ Task "Buy groceries" deleted successfully!
```

### Formatting Standards

- Datetime: `YYYY-MM-DD HH:MM:SS` (ISO 8601)
- Task ID Display: First 8 characters of UUID (e.g., `550e8400`)
- Status Indicators: `[ ]` pending, `[✓]` complete
- Success Messages: Prefix with `✓`
- Error Messages: Prefix with `✗`
- Warning Messages: Prefix with `⚠`

---

## Non-Functional Requirements

### Performance (NFR-001 to NFR-003)

- Operations complete within 100ms for lists < 1000 tasks
- Handle up to 10,000 tasks without exceeding 100MB RAM
- Application starts within 1 second

### Code Quality (NFR-004 to NFR-008)

- 80% minimum test coverage (pytest-cov)
- Type hints throughout (mypy validation)
- Zero ruff linting errors
- Black formatting (100 char line length)
- Google-style docstrings for all public methods

### Logging (NFR-009 to NFR-011)

- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Truncate descriptions in logs to 50 chars (privacy)

### Error Handling (NFR-012 to NFR-014)

- User-friendly error messages (no stack traces)
- Application never crashes on user errors
- Exception hierarchy: DomainValidationError, DomainStateError, TaskNotFoundError

### Architecture (NFR-015 to NFR-017)

- Layer separation: `src/domain/`, `src/storage/`, `src/cli/`
- Dependency inversion: CLI/Storage depend on Domain
- Single Responsibility Principle throughout

---

## Out of Scope

**Explicitly EXCLUDED from Phase I:**

❌ No file/database persistence (in-memory only)
❌ No multi-user support (single logical user)
❌ No authentication/authorization
❌ No advanced task attributes (priority, tags, due dates, categories)
❌ No search/filter beyond basic list view
❌ No command-line arguments (menu-driven only)
❌ No AI integration
❌ No notifications (email, push)
❌ No recurring tasks
❌ No audit log/history
❌ No export/import (JSON, CSV)
❌ No task collaboration (sharing, assignments, comments)
❌ No web/mobile UI (REST API deferred to Phase II)

---

## Testability Guidelines

### Test Distribution (Target: 60-70 tests)

**Unit Tests (Domain Layer): ~35-40 tests**
- `tests/unit/domain/test_task_entity.py`: Task creation, validation (12 tests)
- `tests/unit/domain/test_task_lifecycle.py`: Completion, updates, timestamps (15 tests)
- `tests/unit/domain/test_task_validation.py`: Edge cases, Unicode, special chars (10 tests)

**Integration Tests (CLI + Storage): ~25-30 tests**
- `tests/integration/test_create_workflow.py`: P1 scenarios (6 tests)
- `tests/integration/test_view_workflow.py`: P2 scenarios (6 tests)
- `tests/integration/test_update_workflow.py`: P3 scenarios (8 tests)
- `tests/integration/test_complete_workflow.py`: P4 scenarios (5 tests)
- `tests/integration/test_delete_workflow.py`: P5 scenarios (5 tests)

### Example Test Case (Unit Test)

```python
def test_create_task_with_empty_title_raises_error():
    """
    Given: User provides empty title (whitespace only)
    When: Task creation attempted
    Then: DomainValidationError raised with message "Title cannot be empty"
    """
    with pytest.raises(DomainValidationError, match="Title cannot be empty"):
        Task(title="   ", description="test")
```

### Example Test Case (Integration Test)

```python
def test_create_and_view_workflow(empty_storage):
    """
    Given: Empty task list
    When: User creates task "Buy groceries"
    And: User views all tasks
    Then: Task appears in list with correct title and pending status
    """
    # Create task via CLI operation
    task = create_task_operation(storage, "Buy groceries", "Get milk")

    # View all tasks via CLI operation
    tasks = view_all_tasks_operation(storage)

    assert len(tasks) == 1
    assert tasks[0].title == "Buy groceries"
    assert tasks[0].status == "pending"
```

---

**End of Specification**
