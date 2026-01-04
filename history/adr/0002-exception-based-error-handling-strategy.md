# ADR-0002: Exception-Based Error Handling Strategy

> **Scope**: Error propagation and handling strategy across all application layers (domain, storage, CLI).

- **Status:** Accepted
- **Date:** 2026-01-03
- **Feature:** 001-task-crud-operations
- **Context:** Application needs consistent error handling across three layers (domain, storage, CLI). Errors include validation failures (empty title), state violations (marking complete task complete), and operational failures (task not found). Need clear error semantics that align with Python idioms and provide user-friendly messages without exposing stack traces.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term ✅ - Affects all error handling across all layers throughout project lifetime
     2) Alternatives: ✅ - Exceptions, Result[T, E] types, error codes, Go-style (value, error) returns
     3) Scope: Cross-cutting ✅ - Affects domain, CLI, storage layers and all future features
-->

## Decision

**Error Handling Strategy:**
- **Pattern:** Exception-based error propagation with typed exception hierarchy
- **Exception Hierarchy:** 3 domain-specific exception classes inheriting from base `Exception`
- **Propagation:** Exceptions raised in domain → caught in CLI → displayed with user-friendly messages
- **User Experience:** CLI layer catches all domain exceptions, displays formatted messages prefixed with `✗`, no stack traces exposed

**Exception Taxonomy:**

1. **DomainValidationError** (inherits from `Exception`)
   - **Purpose:** Input validation failures
   - **Trigger Scenarios:**
     - Empty title after trimming whitespace
     - Title exceeds 200 characters
   - **Message Format:** User-friendly strings (e.g., "Title cannot be empty")
   - **Handling:** CLI catches and displays with `✗` prefix

2. **DomainStateError** (inherits from `Exception`)
   - **Purpose:** Invalid state transitions
   - **Trigger Scenarios:**
     - Calling `mark_complete()` on task with `status = "complete"`
   - **Message Format:** User-friendly strings (e.g., "Task is already complete")
   - **Handling:** CLI catches and displays with `✗` prefix

3. **TaskNotFoundError** (inherits from `Exception`)
   - **Purpose:** Task ID not found in storage
   - **Trigger Scenarios:**
     - Storage layer operation fails (task ID doesn't exist)
     - User attempts to view/update/complete/delete non-existent task
   - **Message Format:** User-friendly strings (e.g., "Task not found")
   - **Handling:** CLI catches and displays with `✗` prefix

**Error Propagation Flow:**
```
Domain Layer (raises) → Storage Layer (propagates) → CLI Layer (catches & displays)
```

**CLI Error Handling Contract:**
- Catch all domain exceptions in CLI operation handlers
- Display user-friendly error messages (no stack traces)
- Application never crashes on user errors (NFR-012)
- Global exception handler in `main.py` catches unexpected errors, logs with stack trace, displays generic message

## Consequences

### Positive

- **Python Idiomatic:** Exceptions are standard Python pattern, familiar to all Python developers
- **Clear Error Semantics:** Explicit exception types make error handling intention clear
- **Stack Traces for Debugging:** Exceptions provide full stack traces in logs (JSON structured logging)
- **User-Friendly:** CLI layer translates technical exceptions to plain language messages
- **Type Safety:** Explicit exception types enable IDE autocomplete and type checking
- **Specification Alignment:** Spec defines 3 exception types explicitly (spec.md lines 249-254)
- **Constitutional Compliance:** Meets NFR-012 to NFR-014 (user-friendly errors, no crashes)
- **Maintainability:** Easy to add new exception types without changing error handling infrastructure
- **Separation of Concerns:** Domain raises errors, CLI handles presentation

### Negative

- **Control Flow:** Exceptions as control flow can obscure normal execution paths
- **Performance Overhead:** Exception creation/catching has runtime cost (negligible for console app)
- **Implicit Propagation:** Exceptions propagate automatically, can be caught at unexpected locations
- **Try-Catch Boilerplate:** CLI operations require try-catch blocks (Python idiomatic but verbose)
- **Testing Complexity:** Tests must verify exception raising and catching (requires `pytest.raises`)
- **No Compile-Time Guarantees:** Unlike Result types, exceptions are runtime-only (but Python is runtime-typed)

## Alternatives Considered

### Alternative A: Result Types (Rust-style `Result[T, E]`)
- **Approach:** Functions return `Result[Task, Error]` instead of raising exceptions
- **Example:**
  ```python
  def create_task(title: str) -> Result[Task, DomainValidationError]:
      if not title.strip():
          return Err(DomainValidationError("Title cannot be empty"))
      return Ok(Task(title))
  ```
- **Pros:** Explicit error handling in type signatures, forces callers to handle errors, no control flow via exceptions
- **Cons:** Not Python idiomatic, requires third-party library (`returns` or `result`), verbose unwrapping (`match`/`if is_ok`), unfamiliar to most Python developers
- **Rejected Because:** Violates Phase I "no external dependencies" constraint. Adds complexity without benefit in Python ecosystem. Python community prefers exceptions (EAFP: "Easier to Ask for Forgiveness than Permission").

### Alternative B: Error Codes (C-style integer codes)
- **Approach:** Functions return tuple `(Task | None, int)` where int is error code (0 = success, 1+ = error)
- **Example:**
  ```python
  def create_task(title: str) -> tuple[Task | None, int]:
      if not title.strip():
          return None, 1  # Error code 1: Empty title
      return Task(title), 0
  ```
- **Pros:** Explicit error returns, no exceptions, simple implementation
- **Cons:** Loses error context (int codes require lookup table), error-prone (callers can ignore error code), no stack traces, not Python idiomatic
- **Rejected Because:** Loses type safety (what does error code 3 mean?), no stack traces for debugging, requires global error code registry, not Python idiomatic.

### Alternative C: Go-Style (value, error) Returns
- **Approach:** Functions return tuple `(Task | None, Exception | None)`
- **Example:**
  ```python
  def create_task(title: str) -> tuple[Task | None, Exception | None]:
      if not title.strip():
          return None, DomainValidationError("Title cannot be empty")
      return Task(title), None
  ```
- **Pros:** Explicit error handling, preserves error context, no control flow via exceptions
- **Cons:** Verbose unpacking (`task, err = create_task(...); if err: handle(err)`), callers can ignore error, not Python idiomatic
- **Rejected Because:** Python convention is exceptions, not error returns. Verbose boilerplate. No enforcement that callers check error.

### Alternative D: Option/Maybe Types (Haskell-style)
- **Approach:** Functions return `Option[Task]` (Some(Task) or Nothing)
- **Example:**
  ```python
  def create_task(title: str) -> Option[Task]:
      if not title.strip():
          return Nothing
      return Some(Task(title))
  ```
- **Pros:** Explicit optionality, forces callers to handle None case
- **Cons:** Loses error context (why did it fail?), requires third-party library, unfamiliar pattern in Python
- **Rejected Because:** Loses error messages (no way to communicate "Title cannot be empty"). Requires external library. Not Python idiomatic.

## References

- Feature Spec: [specs/001-task-crud-operations/spec.md](../../specs/001-task-crud-operations/spec.md) (Domain Exceptions lines 249-254)
- Implementation Plan: [specs/001-task-crud-operations/plan.md](../../specs/001-task-crud-operations/plan.md) (Section 4: ADR Candidates, lines 381-387)
- NFR Error Handling: [specs/001-task-crud-operations/spec.md](../../specs/001-task-crud-operations/spec.md) (NFR-012 to NFR-014, lines 387-392)
- Exception Contract: [specs/001-task-crud-operations/contracts/task-entity-contract.md](../../specs/001-task-crud-operations/contracts/task-entity-contract.md) (Exception Contracts section)
- Related ADRs: None
- Python EAFP Philosophy: [Python Glossary - EAFP](https://docs.python.org/3/glossary.html#term-EAFP)
