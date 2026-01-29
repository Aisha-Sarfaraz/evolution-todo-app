<!--
SYNC IMPACT REPORT - Constitution Update
Version Change: Template (unfilled) → 1.0.0 (ratified)
Date: 2025-01-02
Change Type: MAJOR (Initial ratification with comprehensive governance)

Modified/Added Principles:
- Added: I. Spec-Driven Development (NON-NEGOTIABLE)
- Added: II. No Manual Coding (NON-NEGOTIABLE)
- Added: III. Test-Driven Development (NON-NEGOTIABLE)
- Added: IV. Clean Separation of Concerns
- Added: V. Code Modularity & Reusability
- Added: VI. Security, Isolation & Observability

Added Sections:
- Project Identity & Vision
- Phase-Specific Governance (Phases I-V)
- Technology Stack Standards
- Spec Governance & Workflow
- Agent & Multi-Agent Governance
- AI Agent Behavior Governance (Phase III+)
- Deployment & Infrastructure Governance
- Quality, Security & Testing Standards

Templates Requiring Updates:
✅ Constitution template (this file) - updated
⚠ .specify/templates/plan-template.md - review Constitution Check section
⚠ .specify/templates/spec-template.md - ensure alignment with Principle I (SDD)
⚠ .specify/templates/tasks-template.md - verify task categorization reflects principles

Follow-up TODOs:
- None (all placeholders filled)

Integration Status:
✅ Consistent with AGENTS.md (10-agent architecture referenced)
✅ Consistent with CLAUDE.md (SDD and TDD mandates aligned)
✅ Consistent with AGENT_OWNERSHIP_MATRIX.md (blocking authority referenced)
✅ Consistent with AGENT_INVOCATION_PROTOCOL.md (execution flow referenced)
-->

<!--
SYNC IMPACT REPORT - Constitution Amendment v1.1.0
Version Change: 1.0.0 → 1.1.0 (MINOR - Additive Amendments)
Date: 2026-01-10
Change Type: MINOR (Non-breaking additions to strengthen existing principles)

Added Sections:
- ADDENDUM I: VII. Code Quality & AI-Readability Standards (new principle)
- ADDENDUM II: Testing Discipline & Organization (extends Principle III)
- ADDENDUM III: VIII. Performance Standards & Efficiency (new principle)
- ADDENDUM IV: Dependency Inversion & Error Handling (extends Principle IV)

Rationale:
Gap analysis identified 4 critical areas missing from v1.0.0 that are essential for Phase II+ (Web Application onward):
1. Code quality standards (PEP 8, type hints, docstrings, complexity limits) - CRITICAL
2. Test organization (isolation, fixtures, parametrization, markers) - HIGH
3. Performance standards (async patterns, N+1 prevention, resource cleanup) - MODERATE
4. Error handling patterns (taxonomy, propagation, dependency inversion) - MODERATE

Validation Authority:
- Context7 MCP: Python 3.15 (/websites/python_3_15)
- Context7 MCP: pytest (/pytest-dev/pytest)
- Context7 MCP: Clean Code (/ryanmcdermott/clean-code-javascript)

Templates Requiring Updates:
⚠ .specify/templates/plan-template.md - Add performance expectations section
⚠ .specify/templates/tasks-template.md - Add test organization validation checklist
⚠ Backend CLAUDE.md (Phase II+) - Reference new async patterns and error handling

Follow-up Actions:
- Update Phase II backend templates with FastAPI async patterns
- Add code quality pre-commit hooks (ruff + black + mypy strict mode)
- Add performance testing checklist for Phase IV/V deployments

Integration Status:
✅ Consistent with AGENTS.md (no agent authority changes)
✅ Consistent with CLAUDE.md (strengthens existing SDD/TDD rules)
⚠ Requires CLAUDE.md updates for Phase II+ implementation guidance

Authoritative Sources (Context7 MCP):
- PEP 8 Style Guide (/websites/python_3_15)
- pytest Documentation (/pytest-dev/pytest)
- Clean Code JavaScript (/ryanmcdermott/clean-code-javascript)
- FastAPI async best practices (to be consulted for Phase II)
-->

<!--
SYNC IMPACT REPORT - Constitution Amendment v1.1.1
Version Change: 1.1.0 → 1.1.1 (PATCH - Synchronization Fix)
Date: 2026-01-10
Change Type: PATCH (Consistency fix, no new principles or breaking changes)

Modified Sections:
- Agent & Multi-Agent Governance (lines 1187-1290)

Changes Made:
1. Added cross-reference to AGENTS.md as authoritative source for detailed agent specifications
2. Expanded blocking conditions for all agents to match AGENTS.md specifications
3. Corrected Better Auth Guardian classification (removed from Design/Guidance, properly listed under Operational)
4. Added skill ownership to all agent definitions (inline with each agent)
5. Updated skill count: Integration Orchestrator from 4 to 6 skills (added validate-error-propagation, validate-test-coverage)
6. Added missing agent skills:
   - Better Auth Guardian: 1 skill (validate-better-auth-security)
   - Python Backend Architect: 3 skills (validate-api-contracts, generate-api-documentation, check-authorization-coverage)
   - Next.js Frontend Architect: 1 skill (verify-nextjs-16-patterns)
7. Updated total skill count from 8 to 15 across 5 operational agents

Rationale:
Constitution's Agent & Multi-Agent Governance section was out of sync with AGENTS.md (authoritative multi-agent architecture specification). This caused:
- Skill undercounting (8 vs 15 actual skills)
- Missing blocking conditions for governance enforcement
- Better Auth Guardian misclassified
- Integration Orchestrator missing 2 critical skills (error propagation validation, test coverage validation)

Validation Authority:
- AGENTS.md v1.0 (lines 1-697) - Authoritative multi-agent architecture specification

Follow-up Actions:
- None (Constitution now aligned with AGENTS.md)

Integration Status:
✅ Fully consistent with AGENTS.md (all 10 agents, blocking conditions, 15 skills)
✅ No changes required to CLAUDE.md (references Constitution for agent governance)
✅ No impact on existing specs (consistency fix only)
-->

# Evolution of Todo - Hackathon II Constitution

## Project Identity & Vision

**Project Name:** Evolution of Todo - Hackathon II

**Purpose:** A multi-phase todo application demonstrating spec-driven development, cloud-native architecture, and AI integration. This project evolves from a simple console application to a production-grade, cloud-native, AI-powered task management system.

**Evolution Path:**
- **Phase I:** Console Application (Python, in-memory storage)
- **Phase II:** Full-Stack Web Application (FastAPI + Next.js + PostgreSQL)
- **Phase III:** AI Chatbot Interface (OpenAI Agents SDK + MCP tools)
- **Phase IV:** Local Kubernetes Deployment (Minikube + Helm charts)
- **Phase V:** Cloud-Native Event-Driven Architecture (AKS/GKE + Kafka/Dapr)

**Core Objectives:**
1. **Spec-Driven Development:** Every feature must have an approved markdown specification before implementation
2. **Reusable Intelligence:** Agent skills, MCP tools, and subagent patterns that work across domains
3. **Cloud-Native AI:** Stateless, scalable, event-driven architecture with conversational interfaces
4. **Multi-Agent Governance:** 10 specialist agents enforcing quality and architectural standards

---

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

Every feature **MUST** have an approved specification before any implementation begins.

**Requirements:**
- **Workflow:** sp.specify → sp.clarify → sp.plan → sp.tasks → sp.implement
- **Structure:** Each feature requires spec.md (requirements), plan.md (architecture), tasks.md (task breakdown)
- **Storage:** All specifications stored in `specs/<feature>/` with version history
- **Enforcement:** Spec Governance Enforcer agent blocks all work without approved specifications
- **No Exceptions:** Manual coding without spec requires emergency justification documented in PHR

**Rationale:** Specifications ensure clarity, reduce rework, enable multi-agent coordination, and create traceable requirements for testing and validation.

### II. No Manual Coding (NON-NEGOTIABLE)

All code **MUST** be generated via Claude Code using the Spec-Kit Plus workflow.

**Human Responsibilities:**
- Write feature specifications in natural language
- Review generated plans and provide feedback
- Approve test suites before implementation
- Validate implementations against specifications

**AI Responsibilities:**
- Generate implementation plans from specifications
- Create dependency-ordered task breakdowns
- Implement code following approved plans
- Run tests and validate compliance

**Exception Process:**
- Manual coding permitted ONLY for emergency fixes
- Emergency fixes require justification documented in Prompt History Record (PHR)
- Emergency code must be retroactively spec'd and regenerated via Claude Code

**Rationale:** AI-generated code ensures consistency, follows architectural patterns, maintains test coverage, and enables rapid iteration without human coding errors.

### III. Test-Driven Development (NON-NEGOTIABLE)

All implementation **MUST** follow the Red-Green-Refactor cycle.

**Red-Green-Refactor Cycle:**
1. **Red:** Write failing tests that define desired behavior (user approval required)
2. **Green:** Implement minimal code to make tests pass
3. **Refactor:** Improve code quality while keeping tests green

**Coverage Requirements:**
- **Unit Tests:** 80% minimum coverage for domain logic
- **Integration Tests:** 70% minimum coverage for API endpoints and database operations
- **E2E Tests:** Critical user flows must have end-to-end test coverage

**Enforcement:**
- Test Strategy Architect agent blocks implementation if tests not written first
- Test Strategy Architect agent blocks merges if coverage below minimums
- Integration Orchestrator agent blocks deployment if E2E tests fail

**Testing Frameworks:**
- Python: pytest (unit + integration)
- TypeScript/JavaScript: Jest / Vitest (unit), Playwright / Cypress (E2E)

**Rationale:** TDD catches bugs early, ensures testable design, provides regression safety, and creates living documentation of system behavior.

#### Test Organization & Structure (ADDENDUM II - v1.1.0)

**Directory Structure:**
```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── unit/                          # Unit tests (domain + application logic)
│   ├── domain/
│   │   └── test_task.py          # Domain entity tests
│   └── services/
│       └── test_task_service.py  # Service layer tests
├── integration/                   # Integration tests (database, API)
│   ├── test_api_endpoints.py
│   └── test_database.py
└── e2e/                          # End-to-end tests (Phase II+)
    └── test_user_flows.py
```

**Test Naming Conventions:**
- Test files: `test_<module_name>.py`
- Test functions: `test_<functionality>_<scenario>_<expected_outcome>`
- Example: `test_create_task_with_valid_data_returns_task_id()`
- Descriptive names over short names (AI agents benefit from clarity)

**Test Isolation (CRITICAL):**
- **No shared state between tests** (each test MUST be independent)
- Tests MUST be runnable in any order (no dependencies between tests)
- Use fixtures for setup/teardown (no manual state management)
- Database tests MUST use transactions with rollback (no persistent state)

```python
# ✅ CORRECT - Isolated test with fixture
def test_create_task(db_session):
    """Test task creation with isolated database session."""
    task = create_task(db_session, title="Test Task")
    assert task.id is not None
    # db_session automatically rolls back after test

# ❌ INCORRECT - Shared state
tasks = []  # Global state - PROHIBITED

def test_create_task():
    task = Task(title="Test Task")
    tasks.append(task)  # Modifies global state
    assert len(tasks) == 1
```

#### Fixture Management

**conftest.py Usage:**
- Shared fixtures defined in `tests/conftest.py` (visible to all tests)
- Domain-specific fixtures in subdirectory conftest.py (e.g., `tests/integration/conftest.py`)
- Fixture scope: `function` (default), `class`, `module`, `session` (use broader scope only when safe)

**Fixture Best Practices:**
- Use `yield` for fixtures requiring cleanup (e.g., database connections, file handles)
- Document fixture purpose and scope in docstring
- Parameterized fixtures for testing multiple scenarios

```python
# conftest.py
import pytest
import sqlite3
from pathlib import Path

@pytest.fixture(scope="function")
def db_session():
    """Provide isolated database session with automatic rollback.

    Scope: function (new session per test)
    Cleanup: Automatic transaction rollback after test completes
    """
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session  # Test runs here

    session.rollback()  # Rollback changes
    session.close()
```

#### Parametrization Standards

**When to Use Parametrization:**
- Testing same logic with multiple input variations
- Testing boundary conditions (empty, minimum, maximum values)
- Testing error cases (invalid inputs)

**Parametrization Pattern:**
```python
import pytest

@pytest.mark.parametrize("title,expected_valid", [
    ("Valid Task", True),           # Normal case
    ("", False),                     # Empty title
    ("a" * 200, True),               # Maximum length
    ("a" * 201, False),              # Exceeds maximum
    ("  Whitespace  ", True),        # Trimmed
])
def test_task_title_validation(title: str, expected_valid: bool):
    """Test task title validation with various inputs."""
    if expected_valid:
        task = Task(title=title)
        assert task.title.strip() == title.strip()
    else:
        with pytest.raises(ValidationError):
            Task(title=title)
```

**Enforcement:**
- Test Strategy Architect reviews tests for proper isolation
- Blocks PRs with tests that fail when run in random order (`pytest --random-order`)
- Blocks PRs with duplicate test logic (should use parametrization)

#### Test Markers

**Standard Markers:**
- `@pytest.mark.unit` - Unit tests (fast, no I/O)
- `@pytest.mark.integration` - Integration tests (database, API)
- `@pytest.mark.e2e` - End-to-end tests (full user flows)
- `@pytest.mark.slow` - Tests taking > 1 second (run with `--runslow`)

**Running Subsets:**
```bash
pytest -m unit              # Run only unit tests
pytest -m "not slow"        # Skip slow tests
pytest -m "unit or integration"  # Run unit + integration
```

**Enforcement:**
- All tests MUST be marked with appropriate category
- CI pipeline runs fast tests (`unit`) on every commit
- CI pipeline runs full suite (`unit + integration + e2e`) before merge

**Rationale:**
Organized tests scale across all 5 phases. Fixture patterns prevent test pollution. Parametrization reduces duplication. Markers enable fast feedback loops (run unit tests in seconds, full suite in minutes).

**Authority:** pytest documentation (Context7: `/pytest-dev/pytest`), pytest best practices for fixture scope and parametrization

### IV. Clean Separation of Concerns

System architecture **MUST** maintain clear boundaries between layers.

**Layer Boundaries:**
- **Frontend ↔ Backend:** API contracts only, no direct database access from frontend
- **Backend ↔ Domain:** Application services coordinate, domain contains business logic
- **Domain ↔ Infrastructure:** Domain remains pure, infrastructure adapts to domain
- **AI ↔ Backend:** MCP tools provide interface, stateless conversation handling
- **Database ↔ Domain:** Repository pattern with domain-defined interfaces

**Agent Enforcement:**
- **Domain Guardian:** Blocks infrastructure concerns in domain layer
- **Data & Schema Guardian:** Manages database contracts aligned with domain
- **Backend Architect:** Coordinates services without domain logic implementation
- **Frontend Architect:** Implements UI without business logic
- **Better Auth Guardian:** Defines authentication contracts and security boundaries

**Rationale:** Separation of concerns enables independent testing, parallel development, technology swaps, and clear ownership boundaries between specialist agents.

#### Dependency Inversion & Interface Segregation (ADDENDUM IV - v1.1.0)

**Dependency Inversion Principle (DIP):**
- High-level modules (domain, application) MUST NOT depend on low-level modules (infrastructure)
- Both MUST depend on abstractions (interfaces, protocols)
- Domain layer defines repository interfaces, infrastructure layer implements them

**Example (Task Repository):**
```python
# domain/repositories.py (abstract interface)
from abc import ABC, abstractmethod
from typing import Protocol

class TaskRepository(Protocol):
    """Abstract repository interface defined by domain layer."""

    async def get_by_id(self, task_id: str) -> Task | None:
        """Retrieve task by ID."""
        ...

    async def save(self, task: Task) -> None:
        """Persist task."""
        ...

    async def delete(self, task_id: str) -> None:
        """Delete task."""
        ...

# infrastructure/repositories.py (concrete implementation)
class SQLTaskRepository:
    """SQLAlchemy implementation of TaskRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, task_id: str) -> Task | None:
        result = await self.session.execute(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        return result.scalar_one_or_none()

    async def save(self, task: Task) -> None:
        # Save task to database
        pass

# application/services.py (depends on abstraction)
class TaskService:
    """Application service coordinating task operations."""

    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo  # Depends on interface, not implementation

    async def create_task(self, title: str) -> Task:
        task = Task(title=title)
        await self.task_repo.save(task)
        return task
```

**Interface Segregation:**
- Repository interfaces MUST be focused (single responsibility)
- Large interfaces split into smaller, specific interfaces
- Example: `TaskQueryRepository` (read) vs `TaskCommandRepository` (write) for CQRS patterns (Phase V+)

**Enforcement:**
- Domain Guardian blocks infrastructure dependencies in domain layer
- Data & Schema Guardian ensures repository interfaces defined by domain
- Backend Architect implements repository pattern consistently

#### Error Propagation Patterns

**Error Flow Across Layers:**
```
API Layer (FastAPI)
    ↓ Catches HTTPException, returns HTTP status codes
Application Layer (Services)
    ↓ Catches domain errors, wraps in application errors
Domain Layer (Entities)
    ↓ Raises domain-specific exceptions
Infrastructure Layer (Database)
    ↓ Raises infrastructure exceptions (connection errors, etc.)
```

**Domain Errors (Business Rule Violations):**
```python
# domain/errors.py
class DomainError(Exception):
    """Base class for domain errors."""
    pass

class TaskNotFoundError(DomainError):
    """Task does not exist."""
    pass

class InvalidTaskStateError(DomainError):
    """Task state transition is invalid."""
    pass

# domain/entities.py
class Task:
    def complete(self) -> None:
        if self.status == TaskStatus.COMPLETED:
            raise InvalidTaskStateError("Task is already completed")
        self.status = TaskStatus.COMPLETED
```

**Application Errors (Use Case Failures):**
```python
# application/errors.py
class ApplicationError(Exception):
    """Base class for application errors."""
    pass

class UnauthorizedError(ApplicationError):
    """User is not authorized for this operation."""
    pass

# application/services.py
class TaskService:
    async def delete_task(self, task_id: str, user_id: str) -> None:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")
        if task.user_id != user_id:
            raise UnauthorizedError("Cannot delete another user's task")
        await self.task_repo.delete(task_id)
```

**API Layer Error Handling (FastAPI):**
```python
from fastapi import HTTPException, status

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str, current_user: User = Depends(get_current_user)):
    try:
        await task_service.delete_task(task_id, current_user.id)
        return {"status": "deleted"}
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        # Log internal error, return generic message to user
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred"
        )
```

**Error Logging:**
- Domain errors: INFO level (expected business rule violations)
- Application errors: WARNING level (authorization failures, invalid operations)
- Infrastructure errors: ERROR level (database connection failures, external API errors)
- Unexpected errors: CRITICAL level (unhandled exceptions)

**Enforcement:**
- Error & Reliability Architect defines error taxonomy (domain, application, infrastructure)
- Backend Architect implements error propagation patterns
- Integration Orchestrator validates error handling in integration tests
- Better Auth Guardian validates authorization error handling

**Rationale:**
Dependency Inversion enables infrastructure swapping (in-memory → PostgreSQL → distributed cache). Error propagation patterns ensure consistent error handling across layers. Clear error boundaries prevent business logic leaking into API responses.

**Authority:** Clean Architecture principles (Robert C. Martin), Domain-Driven Design error handling patterns

### V. Code Modularity & Reusability

Code **MUST** be designed for reuse across features and phases.

**Reusability Requirements:**
- **Agent Skills:** Operational agents own repeatable workflow skills (8 skills across 2 agents)
- **Domain-Agnostic Design:** Agents and patterns work across different business domains
- **MCP Tools:** AI tools designed as reusable, composable operations
- **Component Libraries:** Shared UI patterns extracted into component libraries (Phase II+)
- **Service Abstractions:** Backend operations abstracted for reuse across features

**Current Skill Ownership:**
- **Data & Schema Guardian:** 4 skills (migration, rollback, validation, integrity)
- **Integration Orchestrator:** 4 skills (coordination, validation, E2E tests, reporting)
- **Other Agents:** 0 skills (reasoning/coordination only, no operational workflows)

**Rationale:** Reusability reduces duplication, accelerates development, ensures consistency, and enables pattern extraction for future projects.

### VI. Security, Isolation & Observability

System **MUST** enforce security, user isolation, and comprehensive observability.

**Security Requirements:**
- **Multi-User Isolation:** JWT-based authentication with user_id filtering on all queries
- **Data Segregation:** Database row-level security policies (Neon DB, Phase II+)
- **Stateless Architecture:** AI agents reconstruct context from database, no server state
- **Secret Management:** API keys and credentials never committed to Git
- **Security Reviews:** Better Auth Guardian blocks authentication changes with security gaps

**Observability Requirements:**
- **Structured Logging:** JSON format with timestamp, level, service, user_id, request_id, context
- **Log Levels:** DEBUG (dev), INFO (operations), WARNING (issues), ERROR (failures), CRITICAL (urgent)
- **Metrics Tracking (Phase IV+):** Request rate, response time, error rate, active users, task operations
- **Monitoring Stack (Phase V):** Prometheus + Grafana + Loki + Jaeger

**Rationale:** Security prevents data breaches and unauthorized access. Isolation ensures compliance and user privacy. Observability enables debugging, performance optimization, and incident response.

**Password Hashing (Phase II+):**
- **Algorithm:** bcrypt with salt (minimum 10 rounds)
- **Verification:** Password comparison via bcrypt.checkpw()
- **No Plain Text:** Never store passwords in plain text or reversibly encrypted

---

### VII. Code Quality & AI-Readability Standards (ADDENDUM I - v1.1.0)

All code **MUST** be written for both human and AI readability, following PEP 8 and modern Python best practices.

#### PEP 8 Compliance (Mandatory)

**Line Length:**
- Maximum 88 characters per line (Black default, more permissive than PEP 8's 79)
- Docstrings and comments: 72 characters maximum for readability

**Indentation:**
- 4 spaces per indentation level (no tabs)
- Continuation lines aligned with opening delimiter or use hanging indent

**Naming Conventions:**
- Modules: `lowercase_with_underscores.py`
- Classes: `PascalCase` (e.g., `TaskRepository`, `UserService`)
- Functions/Methods: `lowercase_with_underscores` (e.g., `create_task`, `validate_user`)
- Constants: `UPPERCASE_WITH_UNDERSCORES` (e.g., `MAX_TITLE_LENGTH`, `API_VERSION`)
- Private attributes: `_leading_underscore` (e.g., `_internal_state`)

**Imports:**
- Absolute imports preferred over relative imports
- Import order: standard library → third-party → local application (enforced by ruff)
- One import per line (except `from module import a, b`)

#### Type Hints (Mandatory)

**Function Signatures:**
- All public functions/methods MUST have type hints for parameters and return values
- Use `typing` module for complex types (List, Dict, Optional, Union, Callable)
- Use `None` return type explicitly for functions with no return value

```python
# ✅ CORRECT
def create_task(title: str, description: str | None = None) -> Task:
    """Create a new task with optional description."""
    return Task(title=title, description=description)

# ❌ INCORRECT (no type hints)
def create_task(title, description=None):
    return Task(title=title, description=description)
```

**Type Alias Definitions:**
- Complex types extracted as type aliases for reusability
- Type aliases documented with docstrings

```python
from typing import TypeAlias

TaskID: TypeAlias = str
TaskDict: TypeAlias = dict[str, Any]
```

**Enforcement:**
- mypy in strict mode (no implicit `Any`, no untyped definitions)
- Type hint coverage: 100% for domain layer, 95% for application layer, 90% for infrastructure layer

#### Docstring Standards (Mandatory)

**Module Docstrings:**
- Every Python module MUST have a module-level docstring
- First line: concise summary (one sentence)
- Subsequent lines: detailed description, usage examples (if applicable)

```python
"""Task domain models and business logic.

This module defines the core Task entity and its business rules including
state transitions, validation, and invariants.
"""
```

**Class Docstrings:**
- Every class MUST have a docstring
- Describe purpose, responsibilities, and usage patterns
- Document class-level invariants

```python
class Task:
    """Represents a todo task with lifecycle management.

    Invariants:
    - Title must be non-empty and ≤ 200 characters
    - Status must be one of: pending, in_progress, completed
    - Once completed, status cannot change

    Lifecycle:
    pending → in_progress → completed
    """
```

**Function/Method Docstrings:**
- All public functions/methods MUST have docstrings
- Private functions (_prefixed) SHOULD have docstrings if complex
- Format: Google style (summary, Args, Returns, Raises)

```python
def update_task(task_id: str, updates: dict[str, Any]) -> Task:
    """Update specified task fields.

    Args:
        task_id: Unique identifier for the task
        updates: Dictionary of field names and new values

    Returns:
        Updated Task instance

    Raises:
        TaskNotFoundError: If task_id does not exist
        ValidationError: If updates violate task invariants
    """
```

**Enforcement:**
- ruff configured to check docstring presence (D100-D107 rules)
- Spec Governance Enforcer blocks PRs with missing docstrings for public APIs

#### Code Readability Rules

**Function Length:**
- Maximum 50 lines per function (excluding docstring)
- Complex functions MUST be decomposed into smaller helper functions
- Rationale: AI agents analyze code in chunks; shorter functions improve comprehension

**Cyclomatic Complexity:**
- Maximum complexity: 10 per function (enforced by ruff)
- High complexity triggers refactoring requirement

**Magic Numbers:**
- No magic numbers in code (extract as named constants)
- Exception: 0, 1, -1 (contextually obvious meanings)

```python
# ✅ CORRECT
MAX_TITLE_LENGTH = 200
if len(title) > MAX_TITLE_LENGTH:
    raise ValidationError(f"Title exceeds {MAX_TITLE_LENGTH} characters")

# ❌ INCORRECT
if len(title) > 200:
    raise ValidationError("Title too long")
```

**Comments:**
- Use comments to explain **why**, not **what** (code should be self-documenting)
- TODOs must include issue number: `# TODO(#123): Implement priority sorting`
- FIXMEs prohibited in main branch (must be resolved before merge)

#### Enforcement

**Pre-Commit Checks:**
- Black formatting verification
- Ruff linting (all PEP 8 rules enabled)
- Mypy type checking (strict mode)

**Blocking Authority:**
- Spec Governance Enforcer blocks PRs failing any pre-commit check
- No exceptions (emergency fixes require retroactive compliance)

**Rationale:**
Consistent code quality ensures AI agents can analyze, modify, and generate code reliably across all 5 phases. Type hints enable static analysis and prevent runtime errors. Docstrings create self-documenting code that future agents and developers can understand without context.

**Authority:** PEP 8 (official Python style guide), Python 3.15 documentation (Context7: `/websites/python_3_15`), Black formatting standards

---

### VIII. Performance Standards & Efficiency (ADDENDUM III - v1.1.0)

All code **MUST** be written with performance awareness appropriate to the current phase.

#### Phase-Appropriate Performance Expectations

**Phase I (Console App):**
- Acceptable: Synchronous operations, in-memory storage
- Response time: < 100ms for CRUD operations
- No performance optimization required (YAGNI principle)

**Phase II (Web Application):**
- **Mandatory**: Async/await for all I/O operations (database, external APIs)
- API response time: p95 < 500ms for read operations, p95 < 1s for write operations
- Database connection pooling required (SQLAlchemy pool size: 5-20 connections)
- N+1 query prevention (see below)

**Phase III (AI Chatbot):**
- MCP tool response time: p95 < 2s (including AI processing)
- Streaming responses for long-running operations (progress indicators)
- Conversation history retrieval: < 100ms

**Phase IV (Kubernetes):**
- Container startup time: < 30s (health checks pass)
- Graceful shutdown: < 10s (complete in-flight requests)
- Resource limits: CPU 500m (0.5 cores), Memory 512Mi

**Phase V (Cloud-Native):**
- Auto-scaling triggers: CPU > 70%, Memory > 80%
- Event processing latency: p95 < 5s (Kafka consumers)
- Load testing passed: 100 req/s sustained, 500 req/s peak

#### Async/Await Patterns (Phase II+)

**When to Use Async:**
- Database queries (SQLAlchemy async engine)
- HTTP requests (httpx async client)
- File I/O operations (aiofiles)
- External API calls (OpenAI, third-party services)

**When NOT to Use Async:**
- Pure computation (no I/O)
- Short in-memory operations
- Synchronous libraries (blocking calls defeat async benefits)

**FastAPI Async Patterns:**
```python
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

# ✅ CORRECT - Async database query
@app.get("/tasks")
async def list_tasks(db: AsyncSession = Depends(get_db)):
    """Async endpoint with async database query."""
    result = await db.execute(select(Task))
    tasks = result.scalars().all()
    return tasks

# ❌ INCORRECT - Blocking call in async endpoint
@app.get("/tasks")
async def list_tasks(db: Session = Depends(get_db)):
    """Async endpoint but synchronous database query (blocks event loop)."""
    tasks = db.query(Task).all()  # Blocking call
    return tasks
```

**Async Context Managers:**
```python
# Proper async resource management
async with httpx.AsyncClient() as client:
    response = await client.get("https://api.example.com/data")
    data = response.json()
```

#### N+1 Query Prevention

**Problem**: Loading related data in loops causes N+1 queries (1 query for parent + N queries for children)

**Solution**: Use eager loading (JOINs) or batching

**Example (Task with Owner):**
```python
# ❌ BAD - N+1 queries (1 for tasks + N for users)
tasks = await db.execute(select(Task))
for task in tasks.scalars():
    user = await db.execute(select(User).where(User.id == task.user_id))
    task.owner = user.scalar_one()  # N queries

# ✅ GOOD - Single query with JOIN
from sqlalchemy.orm import selectinload

tasks = await db.execute(
    select(Task).options(selectinload(Task.owner))
)
# Single query with JOIN, all data loaded
```

**Enforcement:**
- Error & Reliability Architect advises on N+1 issues (detected via query logging)
- Test Strategy Architect requires performance tests for endpoints returning lists
- Integration Orchestrator validates query count in integration tests

#### Resource Cleanup Guarantees

**Database Connections:**
- Use context managers (`with` statements) for automatic cleanup
- FastAPI dependency injection with `yield` ensures cleanup

```python
async def get_db() -> AsyncSession:
    """Provide database session with guaranteed cleanup."""
    async with AsyncSessionLocal() as session:
        yield session
        # Automatic commit/rollback and close
```

**File Handles:**
- Use `with` statements for file operations
- Async file operations with `aiofiles`

```python
# Synchronous file I/O (Phase I)
with open("data.txt", "r") as f:
    data = f.read()
    # File automatically closed

# Async file I/O (Phase II+)
import aiofiles

async with aiofiles.open("data.txt", "r") as f:
    data = await f.read()
    # File automatically closed
```

**HTTP Connections:**
- Use `httpx.AsyncClient()` with context manager
- Connection pooling enabled by default

**Enforcement:**
- Spec Governance Enforcer blocks PRs with resource leaks (unclosed connections, files)
- Test Strategy Architect requires resource cleanup verification in tests

#### Performance Testing (Phase II+)

**Load Testing Requirements:**
- Phase II: Smoke tests (1-10 req/s)
- Phase IV: Load tests (100 req/s sustained)
- Phase V: Stress tests (500 req/s peak, auto-scaling validation)

**Tools:**
- Locust (Python load testing framework)
- k6 (Grafana's load testing tool)

**Metrics to Track:**
- Response time percentiles (p50, p95, p99)
- Error rate (% of requests failing)
- Throughput (requests per second)
- Resource utilization (CPU, memory, database connections)

**Enforcement:**
- Integration Orchestrator runs load tests before Phase IV/V deployments
- Performance regressions (>20% slower) block deployment

**Rationale:**
Performance awareness prevents technical debt. Async patterns leverage FastAPI's concurrency model. N+1 query prevention avoids database bottlenecks. Resource cleanup prevents leaks that degrade system stability over time.

**Authority:** FastAPI async best practices (Context7: `/websites/fastapi_tiangolo`), SQLAlchemy async documentation, Python asyncio patterns

---

## Phase-Specific Governance

### Phase I: Console Application (Current)

**Scope:** In-memory Python todo app with 5 basic CRUD operations (Add, Delete, Update, View, Mark Complete)

**Technology Stack:**
- **Language:** Python 3.13+
- **Package Manager:** UV (fast Python package management)
- **Testing:** pytest (unit tests), pytest-cov (coverage reporting)
- **Code Quality:** ruff (linting), black (formatting), mypy (type checking)
- **Development Tools:** Claude Code + Spec-Kit Plus

**Architecture:**
- Simple CLI with in-memory storage (no persistence)
- Domain models for Task entity
- CLI interface for user commands
- In-memory storage layer

**Project Structure:**
```
todo-app/
├── .specify/memory/constitution.md    # This document
├── specs/<feature>/                   # Feature specifications
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
├── src/
│   ├── domain/                        # Domain models and business logic
│   ├── cli/                           # CLI interface
│   └── storage/                       # In-memory storage
├── tests/
│   ├── unit/                          # Unit tests
│   └── integration/                   # Integration tests
├── CLAUDE.md                          # Claude Code instructions
└── README.md                          # Setup and usage instructions
```

**Quality Gates:**
- All 5 CRUD operations functional
- TDD compliance verified (tests written first)
- 80% unit test coverage achieved
- All tests passing before phase completion

**Deliverables:**
1. Constitution (this document)
2. Feature specifications in specs/
3. Source code in src/
4. Test suite in tests/
5. README.md with setup instructions
6. CLAUDE.md with development guidance

### Phase II: Full-Stack Web Application

**Scope:** Web UI + REST API + PostgreSQL persistence + multi-user authentication

**Technology Stack:**
- **Backend:** Python FastAPI + SQLModel + Neon DB (serverless PostgreSQL)
- **Frontend:** Next.js 16 (App Router) + Tailwind CSS + TypeScript
- **Authentication:** Better Auth + JWT tokens
- **Deployment:** Vercel (frontend), Railway/Render (backend)

**Architecture:**
- Clean architecture with repository pattern
- RESTful API with OpenAPI documentation
- JWT-based authentication and authorization
- Database persistence with migrations (Alembic)

**Quality Gates:**
- Multi-user support with user isolation
- Authentication and authorization working
- API contract tests passing
- Frontend component tests passing
- E2E user flows tested
- Data persistence verified

### Phase III: AI Chatbot Interface

**Scope:** Natural language todo management via conversational AI

**Technology Stack:**
- **AI Framework:** OpenAI Agents SDK (official Python SDK)
- **MCP Protocol:** Official MCP SDK for tool definitions
- **Conversation Storage:** PostgreSQL (conversation_history table)
- **Authentication:** JWT token in conversation context

**AI Governance:**
- **MCP Tools:** create_task, list_tasks, update_task, delete_task, complete_task
- **Natural Language Mapping:** "add a task to buy groceries" → create_task(title="buy groceries")
- **Stateless Handling:** All conversation state stored in database, no server-side sessions
- **User Isolation:** JWT token passed with every AI request for user identification

**Quality Gates:**
- Natural language commands correctly mapped to MCP tool calls
- Stateless conversation handling verified
- User isolation in AI context tested
- Multi-turn conversation flows working
- MCP tool contract tests passing

### Phase IV: Local Kubernetes Deployment

**Scope:** Containerize and deploy to local Minikube cluster

**Technology Stack:**
- **Containerization:** Docker (multi-stage builds)
- **Orchestration:** Kubernetes (Minikube local)
- **Package Management:** Helm 3 (chart versioning, rollback support)
- **Tools:** kubectl, kubectl-ai, kagent

**Deployment Architecture:**
- Microservices: backend, frontend, ai-agent services
- Services: ClusterIP (internal), LoadBalancer (external)
- ConfigMaps: Non-sensitive configuration
- Secrets: JWT keys, DB credentials, OpenAI API keys
- Health Checks: Liveness, readiness, startup probes

**Quality Gates:**
- Local Minikube deployment successful
- All services healthy and communicating
- Helm chart deployment and rollback working
- Health check endpoints responding
- Rolling updates functional

### Phase V: Cloud-Native Event-Driven Architecture

**Scope:** Deploy to cloud (AKS/GKE/DOKS), implement event-driven features

**Technology Stack:**
- **Cloud Kubernetes:** AKS (Azure) / GKE (Google) / DOKS (DigitalOcean)
- **Event Streaming:** Kafka / Redpanda (cloud-managed preferred)
- **Service Mesh:** Dapr (event pub/sub, state management, service invocation)
- **CI/CD:** GitHub Actions / GitLab CI
- **Infrastructure:** Terraform / Pulumi (infrastructure as code)
- **Monitoring:** Prometheus + Grafana + Loki + Jaeger

**Event-Driven Features:**
- Task created/updated/deleted events published to Kafka topics
- Notification service subscribes to task events
- Recurring task scheduler publishes create events
- Audit log service consumes all task events

**Quality Gates:**
- Cloud deployment successful
- Auto-scaling policies working
- Event flow from publishers to subscribers verified
- CI/CD pipeline deploying automatically
- Monitoring dashboards showing metrics
- Load testing passed

---

## Technology Stack Standards

### Phase I Standards (Immediate)

**Core Technologies:**
- **Python:** 3.13+ (latest stable)
- **Package Manager:** UV (replaces pip, faster dependency resolution)
- **Testing:** pytest + pytest-cov
- **Code Quality:** ruff + black + mypy

**Development Workflow:**
```bash
# Install dependencies
uv sync

# Run tests
pytest tests/ --cov=src --cov-report=term

# Lint and format
ruff check src/
black src/

# Type check
mypy src/
```

### Phase II+ Standards (Web Application)

**Backend:**
- **Framework:** FastAPI (async, type-safe, auto-documentation)
- **ORM:** SQLModel (SQLAlchemy + Pydantic integration)
- **Database:** Neon DB (serverless PostgreSQL, auto-scaling)
- **Authentication:** Better Auth (JWT tokens, session management)
- **Migrations:** Alembic (database schema versioning)

**Frontend:**
- **Framework:** Next.js 16 with App Router (file-based routing, server components)
- **Styling:** Tailwind CSS + shadcn/ui components
- **Language:** TypeScript (strict mode)
- **State Management:** React Context / Zustand (as needed)
- **API Communication:** Fetch API / TanStack Query (caching, invalidation)

### Phase III+ Standards (AI Features)

**AI Integration:**
- **AI SDK:** OpenAI Agents SDK (official Python SDK for agents)
- **MCP Protocol:** Official MCP SDK (tool definitions, conversation handling)
- **Conversation Storage:** PostgreSQL (conversation_history table with user_id, message, role, timestamp)
- **Tool Validation:** Pydantic models for input schema validation

**MCP Tool Format:**
- Input schema validation (Pydantic models)
- Output format specification (structured responses)
- Error handling for tool failures (user-friendly messages)
- Usage examples in tool descriptions (for agent context)

### Phase IV+ Standards (Kubernetes)

**Containerization:**
- **Docker:** Multi-stage builds (build stage → runtime stage for size optimization)
- **Orchestration:** Kubernetes (Minikube local, managed cloud for production)
- **Package Management:** Helm 3 (declarative deployments, easy rollbacks)

**Kubernetes Resources:**
- **Deployments:** Replica sets, rolling updates
- **Services:** ClusterIP (internal), LoadBalancer (external)
- **ConfigMaps:** Environment-specific configuration
- **Secrets:** Sensitive data (base64 encoded, encrypted at rest)
- **Health Checks:** Liveness (is alive?), readiness (ready for traffic?), startup (slow start handling)

### Phase V+ Standards (Cloud-Native)

**Cloud Deployment:**
- **Providers:** AKS (Azure), GKE (Google), DOKS (DigitalOcean)
- **Event Streaming:** Kafka (Confluent Cloud, AWS MSK) / Redpanda (self-hosted in K8s)
- **Service Mesh:** Dapr (language-agnostic, sidecar pattern)
- **CI/CD:** GitHub Actions / GitLab CI (build → test → deploy pipeline)
- **Infrastructure:** Terraform / Pulumi (version-controlled infrastructure definitions)
- **Monitoring:** Prometheus (metrics), Grafana (dashboards), Loki (logs), Jaeger (traces)

---

## Spec Governance & Workflow

### Directory Structure

```
.specify/
  ├── memory/constitution.md           # This document
  ├── templates/                       # Specification templates
  │   ├── spec-template.md
  │   ├── plan-template.md
  │   ├── tasks-template.md
  │   ├── adr-template.md
  │   └── phr-template.prompt.md
  └── scripts/bash/                    # Utility scripts
      ├── create-phr.sh
      ├── create-adr.sh
      └── create-new-feature.sh

specs/
  └── <feature-name>/
      ├── spec.md                      # Requirements and acceptance criteria
      ├── plan.md                      # Architecture and design decisions
      ├── tasks.md                     # Task breakdown with dependencies
      └── checklists/                  # Validation checklists
          ├── requirements.md
          ├── ux.md
          └── security.md

history/
  ├── prompts/                         # Prompt History Records (traceability)
  │   ├── constitution/                # Constitution-related prompts
  │   ├── general/                     # General prompts
  │   └── <feature-name>/              # Feature-specific prompts
  └── adr/                             # Architecture Decision Records
      ├── 001-<title>.md
      ├── 002-<title>.md
      └── 003-<title>.md
```

### Spec Workflow (SpecifyPlus Commands)

**Command Sequence:**
1. **sp.specify** - Create feature specification from natural language description
2. **sp.clarify** - Ask up to 5 clarification questions, update spec with answers
3. **sp.plan** - Generate implementation plan with architecture decisions
4. **sp.adr** - Document architecturally significant decisions as ADRs
5. **sp.tasks** - Break down plan into dependency-ordered tasks
6. **sp.checklist** - Generate validation checklists for quality gates
7. **sp.analyze** - Cross-artifact consistency and quality analysis
8. **sp.implement** - Execute tasks via Claude Code (TDD workflow)
9. **sp.git.commit_pr** - Autonomous Git workflow (commit changes + create PR)
10. **sp.phr** - Record prompt history for traceability and learning

**Referencing Format:**
- Feature specs: `@specs/features/<feature-name>/spec.md`
- Architecture decisions: `@history/adr/<ID>-<title>.md`
- Templates: `@.specify/templates/<template-name>.md`
- Agents: Reference by name (e.g., "Domain Guardian agent validates domain purity")

**Versioning:**
- Specifications versioned via Git commits (full history preserved)
- Major spec changes require new ADR documenting rationale
- Spec history maintained in `history/prompts/<feature>/`
- ADRs numbered sequentially (001, 002, 003...) with descriptive titles

**CLAUDE.md Integration:**
- **Root CLAUDE.md:** General SDD and TDD rules, references this Constitution
- **Backend CLAUDE.md (Phase II+):** Python/FastAPI context, backend patterns
- **Frontend CLAUDE.md (Phase II+):** Next.js/React context, frontend patterns
- All CLAUDE.md files reference Constitution for authoritative principles

---

## Agent & Multi-Agent Governance

**Authoritative Source:** AGENTS.md defines the complete multi-agent architecture specification including detailed agent responsibilities, blocking conditions, and skill ownership. This section provides constitutional summaries aligned with AGENTS.md.

**Cross-Reference:** @AGENTS.md for complete agent specifications, execution order, and enforcement protocols.

### Agent Categories

Agents are classified into four categories with distinct authorities:

**Governance Agents (Blocking Authority):**
- **Spec Governance Enforcer:** Blocks if no approved specification exists, specification violates constitutional principles, implementation deviates from approved spec, or ADRs missing for significant decisions
- **Test Strategy Architect:** Blocks if tests not written before implementation, TDD cycle violated (code before tests), test coverage below minimum thresholds, or critical paths lack tests
- **Skills:** None (governance agents validate process, do not own operational skills)

**Domain Agents (Blocking Authority):**
- **Domain Guardian (Generic):** Blocks if domain boundaries violated (infrastructure in domain), domain invariants broken, invalid state transitions detected, or domain pollution detected (domain-agnostic, configurable for any business domain)
- **Core Todo Domain:** Blocks if Task domain boundaries violated, Task invariants broken, or invalid Task state transitions (Todo-specific enforcement, specialization of Domain Guardian)
- **Skills:** None (reasoning agents, no operational skills)

**Design/Guidance Agents (Advisory):**
- **Error & Reliability Architect:** Advises on error handling, resilience patterns, observability strategies (no blocking authority, provides recommendations only)
- **Skills:** None (design agents define contracts, do not own operational skills)

**Operational Agents (Variable Authority):**
- **Better Auth Guardian:** Blocks if critical security issues detected (hardcoded secrets, disabled CSRF), session handling violates Better Auth security patterns, or auth flows have security gaps; warns for high-severity issues (user discretion to proceed)
  - **Skills:** 1 skill (`validate-better-auth-security`)
- **Python Backend Architect:** Implements application services (can be blocked by Domain Guardian if violates domain boundaries, Integration Orchestrator if integration fails, Test Strategy Architect if tests missing)
  - **Skills:** 3 skills (`validate-api-contracts`, `generate-api-documentation`, `check-authorization-coverage`)
- **Next.js Frontend Architect:** Implements UI components (can be blocked by Spec Governance if no approved spec, Integration Orchestrator if integration fails, Test Strategy Architect if tests missing)
  - **Skills:** 1 skill (`verify-nextjs-16-patterns`)
- **Data & Schema Guardian:** Blocks if schema conflicts with domain model, migration has no rollback path, or migration causes data loss without approval
  - **Skills:** 4 skills (`generate-migration`, `execute-migration-rollback`, `validate-schema-alignment`, `verify-data-integrity`)
- **Integration Orchestrator:** Blocks if cross-layer contract violations detected, integration tests fail, or required agent skipped in workflow
  - **Skills:** 6 skills (`coordinate-agent-sequence`, `validate-integration-points`, `execute-e2e-tests`, `aggregate-workflow-results`, `validate-error-propagation`, `validate-test-coverage`)

### Agent Invocation Order

Agents execute sequentially following CrewAI Process.sequential pattern:

```
1. Spec Governance Enforcer
   ↓ (validates spec exists and is complete)
2. Domain Guardian
   ↓ (validates domain model changes)
3. Data & Schema Guardian
   ↓ (designs database schema aligned with domain)
4. Python Backend Architect [if backend changes needed]
   ↓ (implements application services)
5. Next.js Frontend Architect [if frontend changes needed]
   ↓ (implements user interface)
6. Better Auth Guardian [if auth changes needed]
   ↓ (defines authentication requirements)
7. Error & Reliability Architect (always runs)
   ↓ (reviews error handling - advisory)
8. Test Strategy Architect (always runs)
   ↓ (validates TDD compliance)
9. Integration Orchestrator (always runs)
   └─ (validates end-to-end integration)
```

**Blocking Semantics:**
- **STOP:** Critical failure, execution halts immediately, requires user intervention
- **BLOCK:** Agent refuses to approve work until issues resolved, downstream agents do not execute
- **ADVISE:** Recommendations provided, execution continues, user decides whether to address

### Agent Skills

Skills represent repeatable operational workflows owned by Operational Agents only.

**Current Skill Distribution:**

- **Better Auth Guardian:** 1 skill
  - validate-better-auth-security (Security audit of Better Auth implementations using Context7 MCP)

- **Python Backend Architect:** 3 skills
  - validate-api-contracts (Verify API endpoints match OpenAPI schema using automated contract testing)
  - generate-api-documentation (Auto-generate comprehensive API documentation from route definitions and Pydantic models)
  - check-authorization-coverage (Ensure all protected API endpoints verify permissions and authorization using Security() dependencies)

- **Next.js Frontend Architect:** 1 skill
  - verify-nextjs-16-patterns (Validate Next.js code patterns against Next.js 16 best practices using Context7 MCP)

- **Data & Schema Guardian:** 4 skills
  - generate-migration (Generate Alembic migrations from domain changes)
  - execute-migration-rollback (Safely rollback migrations with data preservation)
  - validate-schema-alignment (Verify schema aligns with domain model)
  - verify-data-integrity (Validate data consistency after migrations)

- **Integration Orchestrator:** 6 skills
  - coordinate-agent-sequence (Execute multi-agent workflows in correct dependency order)
  - validate-integration-points (Verify contracts between system layers)
  - execute-e2e-tests (Run integration and E2E tests)
  - aggregate-workflow-results (Collect and summarize workflow results)
  - validate-error-propagation (Validate error handling and propagation across all system layers using Clean Architecture and DDD best practices)
  - validate-test-coverage (Validate test coverage against minimum thresholds using pytest-cov and coverage.py)

- **Governance, Design/Guidance, and Domain Agents:** 0 skills (reasoning/coordination only, no operational workflows)

**Total Skills:** 15 across 5 operational agents (Better Auth Guardian, Python Backend Architect, Next.js Frontend Architect, Data & Schema Guardian, Integration Orchestrator)

**Skill Governance Rules:**
1. Skills ONLY owned by Operational Agents (not governance, design, or domain agents)
2. Skills represent repeatable workflows (used 3+ times across features)
3. Existing skills NEVER modified or removed without governance approval
4. New skills require approval from Spec Governance Enforcer agent

---

## AI Agent Behavior Governance (Phase III+)

### MCP Tool Specifications

**Tool: create_task**
- **Input:** `{title: str, description: str, priority?: str, due_date?: str}`
- **Output:** `{task_id: str, created_at: str, status: str}`
- **Behavior:** Create new task in user's task list
- **Validation:** Title required (max 200 chars), description optional (max 2000 chars)
- **Authorization:** JWT token from conversation context identifies user

**Tool: list_tasks**
- **Input:** `{filter?: str, status?: str, sort_by?: str}`
- **Output:** `{tasks: [Task], total_count: int}`
- **Behavior:** Retrieve user's tasks with optional filters
- **Validation:** Filter by status (pending/complete), sort by priority/due_date/created_at

**Tool: update_task**
- **Input:** `{task_id: str, updates: {title?, description?, priority?, status?}}`
- **Output:** `{task_id: str, updated_at: str, updated_fields: [str]}`
- **Behavior:** Update specified task fields
- **Validation:** task_id must exist and belong to user (enforced via JWT)

**Tool: delete_task**
- **Input:** `{task_id: str}`
- **Output:** `{deleted: bool, task_id: str}`
- **Behavior:** Soft delete task (mark as deleted, retain for history/audit)
- **Validation:** task_id must exist and belong to user

**Tool: complete_task**
- **Input:** `{task_id: str}`
- **Output:** `{task_id: str, status: str, completed_at: str}`
- **Behavior:** Mark task as complete
- **Validation:** task_id must exist, status must be "pending" (cannot re-complete)

### Natural Language Command Mapping

**Examples:**
- "add a task to buy groceries" → `create_task(title="buy groceries")`
- "show me my pending tasks" → `list_tasks(status="pending")`
- "mark task #123 as done" → `complete_task(task_id="123")`
- "update my meeting task to high priority" → `update_task(task_id=<lookup>, updates={priority: "high"})`
- "delete the shopping task" → `delete_task(task_id=<lookup>)` [requires task lookup first]

### Stateless Conversation Handling

**Database Schema:**
```sql
CREATE TABLE conversation_history (
  id UUID PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  message TEXT NOT NULL,
  role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
  timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
  context_json JSONB
);
```

**Stateless Architecture:**
- All conversation state stored in `conversation_history` table
- No server-side session state (agents reconstruct context from database)
- JWT token passed with every AI request for user identification
- Conversation context includes recent N messages (configurable, default 10)
- Agent loads context from DB, processes request, saves response to DB

**Error Handling:**
- Tool errors return structured error responses (HTTP status codes)
- Agent provides user-friendly error messages (no technical stack traces)
- Errors logged server-side with context (user_id, tool_name, error_type, timestamp)

---

## Deployment & Infrastructure Governance

### Phase I: Local Execution

**Environment:**
- No deployment infrastructure required
- Run via `python src/main.py` or `uv run src/main.py`
- Configuration via environment variables (`.env` file, git-ignored)

**Configuration:**
```bash
# .env (example for Phase I)
LOG_LEVEL=INFO
DEBUG_MODE=false
```

### Phase II: Web Application Deployment

**Backend Deployment:**
- **Platform:** Vercel / Railway / Render (serverless or container-based)
- **Database:** Neon DB (serverless PostgreSQL, auto-scaling)
- **Environment Variables:** Managed via platform dashboard (DATABASE_URL, JWT_SECRET, etc.)
- **CI/CD:** GitHub Actions (automated deployments on push to main)

**Frontend Deployment:**
- **Platform:** Vercel / Netlify (optimized for Next.js)
- **Build:** Next.js static export or standalone mode
- **Environment Variables:** NEXT_PUBLIC_API_URL (backend API base URL)

### Phase IV: Kubernetes Deployment

**Local Environment:**
- **Cluster:** Minikube (local Kubernetes cluster)
- **CLI Tools:** kubectl, kubectl-ai, kagent, helm

**Containerization:**
- **Backend Dockerfile:** Multi-stage build (dependencies → app → runtime)
- **Frontend Dockerfile:** Next.js build → static export or standalone
- **AI Services Dockerfile:** Python + OpenAI SDK + MCP tools

**Kubernetes Resources:**
- **Deployments:** backend, frontend, ai-agent (replicas, resource limits)
- **Services:** ClusterIP (internal), LoadBalancer (external access)
- **ConfigMaps:** API URLs, feature flags, non-sensitive configuration
- **Secrets:** JWT secret, DB credentials, OpenAI API key (base64 encoded)

**Helm Charts:**
- **Chart Structure:** templates/, values.yaml, Chart.yaml
- **Parameterization:** Replicas, image tags, resource limits configurable via values
- **Version Management:** `helm upgrade`, `helm rollback` for safe deployments

**Health Checks:**
- **Liveness Probe:** `/health/live` endpoint (is service alive?)
- **Readiness Probe:** `/health/ready` endpoint (ready to receive traffic?)
- **Startup Probe:** For slow-starting services (AI model loading, etc.)

### Phase V: Cloud-Native Deployment

**Cloud Kubernetes:**
- **Providers:** AKS (Azure), GKE (Google), DOKS (DigitalOcean)
- **Node Pools:** Separate pools for backend, frontend, AI services (different resource needs)
- **Auto-Scaling:** Horizontal Pod Autoscaler (HPA) based on CPU/memory metrics

**Infrastructure as Code:**
- **Tools:** Terraform / Pulumi
- **Resources:** Kubernetes cluster, node pools, networking, storage, load balancers
- **Version Control:** Infrastructure definitions committed to Git
- **Environments:** Separate configurations for dev, staging, production

**Event Streaming:**
- **Kafka:** Cloud-managed (Confluent Cloud, AWS MSK, Azure Event Hubs) or self-hosted Redpanda
- **Topics:** task_created, task_updated, task_deleted, task_completed
- **Producers:** Backend services publish events on task operations
- **Consumers:** Notification service, audit log service, recurring task scheduler

**Dapr Integration:**
- **Pub/Sub Component:** Connects to Kafka for event publishing/subscribing
- **State Management:** Distributed caching for session state (if needed)
- **Service Invocation:** Service-to-service communication with retries and circuit breakers

**CI/CD Pipeline:**
- **Tools:** GitHub Actions / GitLab CI
- **Stages:**
  1. **Build:** Compile code, run linters and type checkers
  2. **Test:** Run unit, integration, E2E tests
  3. **Build Images:** Create Docker images, tag with commit SHA
  4. **Push to Registry:** Push images to container registry (Docker Hub, GCR, ACR)
  5. **Deploy to Kubernetes:** Update Helm releases in dev → staging → production
  6. **Validate Deployment:** Run smoke tests, check health endpoints
- **Approval Gates:** Manual approval required for production deployments

**Monitoring & Observability:**
- **Metrics:** Prometheus (time-series metrics collection)
- **Dashboards:** Grafana (visualize metrics, create alerts)
- **Logs:** Loki (log aggregation, searchable via LogQL)
- **Traces:** Jaeger / Tempo (distributed tracing for debugging)
- **Alerting:** Alert rules for critical failures (high error rate, service down, etc.)

**Environment Management:**
- **Development:** Local Minikube, in-memory storage for testing
- **Staging:** Cloud Kubernetes, separate namespace, Neon DB staging instance
- **Production:** Cloud Kubernetes, production namespace, Neon DB production instance

**Secrets Management:**
- **Phase I-II:** `.env` files (git-ignored, local only)
- **Phase IV:** Kubernetes Secrets (base64 encoded)
- **Phase V (Production):** Cloud secret managers (Azure Key Vault, GCP Secret Manager, AWS Secrets Manager)

---

## Quality, Security & Testing Standards

### Testing Standards

**Unit Testing (TDD Required):**
- **Coverage Minimum:** 80% for domain logic
- **Framework:** pytest (Python), Jest/Vitest (TypeScript)
- **Naming Convention:** `test_<module>.py` or `<module>.test.ts`
- **Structure:** Arrange-Act-Assert pattern
- **Enforcement:** Test Strategy Architect blocks implementation if tests not written first

**Integration Testing:**
- **Coverage Minimum:** 70% for API endpoints and database operations
- **Framework:** pytest with TestClient (FastAPI), Supertest (Express/Next.js API routes)
- **Scope:** API contract tests, database integration tests, MCP tool contract tests (Phase III+)

**End-to-End Testing (Phase II+):**
- **Framework:** Playwright / Cypress
- **Scope:** Critical user flows (signup → create task → complete task → delete task)
- **Execution:** Run in CI/CD pipeline before deployment to staging/production

### Security Requirements

**Authentication & Authorization:**
- **Framework:** Better Auth (JWT-based authentication)
- **Token Expiration:** Access tokens: 1 hour, refresh tokens: 7 days
- **Password Hashing:** bcrypt with salt (minimum 10 rounds)
- **Role-Based Access Control (Future):** User, admin roles with different permissions

**User Isolation:**
- **Query Filtering:** All database queries MUST filter by user_id (extracted from JWT)
- **Row-Level Security:** Neon DB policies enforce user_id filtering at database level (Phase II+)
- **No Cross-User Access:** Backend services enforce user isolation, tested in integration tests
- **Audit Logging:** Sensitive operations (create/delete user) logged with user_id and timestamp

**Data Protection:**
- **Transport Security:** HTTPS only in production (TLS 1.2+)
- **Encryption at Rest:** Database-level encryption (Neon DB default)
- **Secret Management:** API keys, credentials never committed to Git, stored in environment variables or secret managers
- **Rate Limiting (Phase II+):** 100 requests/minute per user (configurable)

**Input Validation:**
- **Backend Validation:** All inputs validated via Pydantic models (type checking, length limits)
- **SQL Injection Prevention:** Parameterized queries via SQLModel ORM (never string concatenation)
- **XSS Prevention:** React auto-escaping, Content Security Policy (CSP) headers
- **CSRF Protection:** SameSite cookies, CSRF tokens for state-changing operations

### Error Handling

**User-Facing Errors:**
- **Generic Messages:** Never expose internal errors (e.g., "An error occurred" instead of stack traces)
- **HTTP Status Codes:** 400 (bad request), 401 (unauthorized), 403 (forbidden), 404 (not found), 500 (server error)
- **Helpful Messages:** User-friendly error messages in UI (e.g., "Task not found" instead of "404")

**Server-Side Logging:**
- **Detailed Errors:** Full stack traces, context, user_id logged server-side for debugging
- **Structured Format:** JSON logs with timestamp, level, service, user_id, request_id, error_message, stack_trace

### Logging & Monitoring

**Structured Logging (JSON Format):**
```json
{
  "timestamp": "2025-01-02T10:30:00Z",
  "level": "INFO",
  "service": "backend-api",
  "user_id": "user_123",
  "request_id": "req_abc456",
  "message": "Task created successfully",
  "context": {"task_id": "task_789"}
}
```

**Log Levels:**
- **DEBUG:** Detailed diagnostics (development only, disabled in production)
- **INFO:** General informational messages (task created, user logged in)
- **WARNING:** Potential issues (rate limit approaching, slow query detected)
- **ERROR:** Errors that don't stop execution (task not found, validation failed)
- **CRITICAL:** Errors requiring immediate attention (database down, auth service unreachable)

**Metrics to Track (Phase IV+):**
- **Request Rate:** Requests per second (RPS)
- **Response Time:** p50, p95, p99 latencies
- **Error Rate:** Percentage of failed requests (5xx errors)
- **Active Users:** Concurrent sessions
- **Task Operations:** Creates, updates, deletes per day

### Optional Features (Intermediate/Advanced)

**Multi-Language Support:**
- **Languages:** English (primary), Urdu (optional, future)
- **Framework:** react-i18next (frontend internationalization)
- **Translation Files:** `locales/en.json`, `locales/ur.json`

**Voice Input (Optional):**
- **Web Speech API:** Browser-based voice input (Chrome, Edge support)
- **OpenAI Whisper:** Backend voice-to-text processing (Phase III+)
- **Command Mapping:** Voice commands mapped to natural language intents (e.g., "add task" → create_task)

---

## Governance

### Constitution Authority

This Constitution is the **authoritative governance document** for all phases of the Evolution of Todo project.

**Authority Hierarchy:**
1. **Constitution (this document):** Defines principles, standards, and governance rules
2. **AGENTS.md:** Defines agent architecture and responsibilities (implements Constitution)
3. **CLAUDE.md:** Defines operational SDD and TDD workflows (implements Constitution)
4. **Agent Ownership Matrix:** Defines blocking authority and conflict resolution (enforces Constitution)
5. **Agent Invocation Protocol:** Defines execution flow and handoff contracts (operationalizes Constitution)

**Precedence Rules:**
- Constitution supersedes conflicting guidance in other documents
- All feature specs MUST comply with Constitution principles
- Agents reference Constitution via CLAUDE.md and agent definitions

### Amendment Process

**Proposal:**
1. Create ADR proposing Constitution amendment with rationale
2. Document impact analysis (which principles/sections affected, which specs need updates)

**Review:**
1. Multi-agent review (Spec Governance Enforcer + relevant specialist agents)
2. User (hackathon team) reviews amendment proposal
3. Identify affected specs, code, and documentation requiring updates

**Approval:**
1. User approves amendment (explicit consent required)
2. Version number incremented according to semantic versioning:
   - **MAJOR:** Breaking changes to principles or workflow
   - **MINOR:** New sections, clarifications, non-breaking additions
   - **PATCH:** Typo fixes, formatting improvements, wording refinements

**Update:**
1. Constitution updated with new version number and last amended date
2. Affected specs and code updated to comply with amended principles
3. PHR created documenting amendment rationale and impact

**Communication:**
1. Amendment announced to team via commit message and PHR
2. Migration plan provided if existing work needs updates

### Compliance Enforcement

**Agent Enforcement:**
- **Spec Governance Enforcer:** Blocks non-compliant work (no approved spec)
- **Domain Guardian:** Blocks domain boundary violations
- **Test Strategy Architect:** Blocks TDD violations (tests not written first, coverage insufficient)
- **Better Auth Guardian:** Blocks security requirement violations
- **Data & Schema Guardian:** Blocks schema conflicts with domain model
- **Integration Orchestrator:** Blocks integration test failures

**PR/Merge Verification:**
- All pull requests verified for Constitution compliance before merge
- Automated checks for test coverage, linting, type checking
- Agent reviews triggered for architectural changes

**Complexity Justification:**
- Any complexity beyond simple CRUD operations MUST be justified in spec or ADR
- Premature optimization rejected unless performance requirements documented
- YAGNI principle enforced (You Aren't Gonna Need It)

### Version Control

**Version Format:** MAJOR.MINOR.PATCH (semantic versioning)

**Version History:**
- All Constitution versions tracked in Git history
- ADRs reference Constitution version in effect at time of decision
- Specs reference Constitution version they were created under

**Review Schedule:**
- Constitution reviewed after each phase completion
- Amendments proposed based on lessons learned
- Continuous improvement via PHR analysis and retrospectives

---

**Version:** 1.1.1 | **Ratified:** 2025-01-02 | **Last Amended:** 2026-01-10
