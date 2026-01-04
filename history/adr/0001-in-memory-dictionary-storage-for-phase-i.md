# ADR-0001: In-Memory Dictionary Storage for Phase I

> **Scope**: Persistence strategy for Phase I console application, establishing foundation for Phase II database migration.

- **Status:** Accepted
- **Date:** 2026-01-03
- **Feature:** 001-task-crud-operations
- **Context:** Phase I requires task storage for console application. Specification explicitly excludes file and database persistence (Out of Scope). Need simple, testable solution that meets Phase I requirements while enabling clean migration to PostgreSQL in Phase II.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term ✅ - Affects Phase II migration path to Neon DB PostgreSQL
     2) Alternatives: ✅ - Dictionary, JSON file, SQLite, pickle considered
     3) Scope: Cross-cutting ✅ - Affects persistence layer, testing strategy, Phase II architecture
-->

## Decision

**Phase I Persistence Strategy:**
- **Storage Implementation:** In-memory Python dictionary (`Dict[str, Task]`)
- **Key Strategy:** UUID4 strings as dictionary keys (globally unique)
- **Value Strategy:** Full Task entity objects as dictionary values
- **Interface Pattern:** Abstract `RepositoryInterface` with concrete `MemoryRepository` implementation
- **Migration Path:** Phase II swap: `MemoryRepository` → `PostgresRepository` via dependency injection in `main.py` (one-line change)

**Core Operations:**
- `add(task)`: `storage[task.id] = task`
- `get(task_id)`: `storage.get(task_id)` (returns None if not found)
- `get_all()`: `sorted(storage.values(), key=lambda t: t.created_at, reverse=True)`
- `update(task)`: `storage[task.id] = task` (replace entire object)
- `delete(task_id)`: `del storage[task_id]`
- `exists(task_id)`: `task_id in storage`

## Consequences

### Positive

- **Simplicity:** Zero configuration, no external dependencies, no file I/O complexity
- **Performance:** O(1) lookups, deletes, existence checks; O(n log n) sorting (acceptable for < 1000 tasks per spec)
- **Testability:** Fast test execution (no database setup/teardown), deterministic state, easy mocking
- **Development Speed:** Immediate implementation, no migration scripts, no schema management for Phase I
- **Clean Migration Path:** Repository interface pattern enables future database swap without changing domain or CLI layers
- **Memory Efficiency:** No serialization overhead, direct object access
- **Constitutional Compliance:** Meets Principle IV (Separation of Concerns) - storage abstracted behind interface

### Negative

- **No Persistence:** Data lost on application exit (acceptable per Phase I spec, Out of Scope line 405)
- **Single-User Only:** No concurrent access support (acceptable per Phase I spec, single-user constraint)
- **Memory Constraints:** 100MB limit for 10,000 tasks (acceptable per NFR-002, validated by performance tests)
- **No Audit Trail:** No historical data (deferred to Phase II per spec Out of Scope line 414)
- **Testing Limitation:** Cannot test database-specific issues (migrations, indexes, constraints) until Phase II
- **Manual Data Entry:** No data import/export in Phase I (users recreate tasks on each run)

## Alternatives Considered

### Alternative A: JSON File Persistence
- **Approach:** Serialize tasks to `tasks.json` on every change
- **Pros:** Data persists across runs, human-readable format, easy debugging
- **Cons:** File I/O adds complexity, error handling for corrupt files, atomic writes needed, slower tests
- **Rejected Because:** Phase I spec explicitly excludes file persistence (Out of Scope). Adds unnecessary complexity for temporary solution.

### Alternative B: SQLite Database
- **Approach:** Embedded SQLite database with Alembic migrations
- **Pros:** Real database, SQL queries, ACID guarantees, closer to Phase II architecture
- **Cons:** External dependency (violates Phase I stdlib-only constraint), migration complexity, schema management overhead
- **Rejected Because:** Violates Phase I "no external dependencies" constraint (Constitution lines 189-222). Over-engineered for Phase I simplicity goal.

### Alternative C: Python Pickle Serialization
- **Approach:** Pickle dictionary to file on exit, unpickle on startup
- **Pros:** Simple serialization, preserves Python object structure
- **Cons:** Security risks (untrusted pickle data), Python version compatibility issues, file I/O complexity
- **Rejected Because:** Security concerns (pickle is unsafe for untrusted data), adds file I/O without Phase I benefit. Not production-ready pattern.

### Alternative D: CSV File Storage
- **Approach:** Write tasks to CSV file, load on startup
- **Pros:** Human-readable, Excel-compatible, simple format
- **Cons:** Complex datetime serialization, escaping issues (quotes in descriptions), no relational integrity
- **Rejected Because:** Phase I spec excludes file persistence. CSV format doesn't preserve datetime objects cleanly. Phase II needs relational database, not flat file.

## References

- Feature Spec: [specs/001-task-crud-operations/spec.md](../../specs/001-task-crud-operations/spec.md) (Out of Scope line 405)
- Implementation Plan: [specs/001-task-crud-operations/plan.md](../../specs/001-task-crud-operations/plan.md) (Section 4: ADR Candidates, lines 373-379)
- Data Model: [specs/001-task-crud-operations/data-model.md](../../specs/001-task-crud-operations/data-model.md) (Storage Strategy section)
- Repository Contract: [specs/001-task-crud-operations/plan.md](../../specs/001-task-crud-operations/plan.md) (Section 2.1: Domain → Storage Contract)
- Related ADRs: None (first ADR for this feature)
- Phase II Migration: [specs/001-task-crud-operations/plan.md](../../specs/001-task-crud-operations/plan.md) (Migration & Rollback Strategy section)
