# Phase I - Task CRUD Operations

**Version**: 0.1.0
**Status**: Implementation Phase
**Specification**: [spec.md](../specs/001-task-crud-operations/spec.md)
**Plan**: [plan.md](../specs/001-task-crud-operations/plan.md)

---

## Overview

Phase I implements an in-memory Python console todo application with 5 basic CRUD operations (Create, View, Update, Mark Complete, Delete). The application follows a three-layer architecture (Domain, Storage, CLI) with strict Test-Driven Development (TDD) workflow.

**Key Features**:
- Create tasks with title and description
- View all tasks or individual task details
- Update task title and description
- Mark tasks as complete
- Delete tasks permanently
- In-memory storage (no persistence between sessions)

---

## Prerequisites

- **Python 3.13+** ([python.org](https://www.python.org/downloads/))
- **UV package manager** (`pip install uv`)

---

## Setup Instructions

### 1. Navigate to Phase-1 Directory

```bash
cd Phase-1
```

### 2. Install Dependencies

```bash
uv sync
```

This installs development dependencies: pytest, pytest-cov, ruff, black, mypy

### 3. Run the Application

```bash
uv run python src/main.py
```

---

## Running Tests

### Run All Tests

```bash
uv run pytest
```

### Run with Coverage Report

Coverage is configured in `pyproject.toml` and runs automatically:

```bash
uv run pytest
```

HTML coverage report is generated at `htmlcov/index.html`.

View HTML coverage report:
```bash
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html # Windows
```

### Run Specific Test File

```bash
uv run pytest tests/unit/domain/test_task_entity.py
```

---

## Code Quality

### Linting (Ruff)

```bash
uv run ruff check src/
```

Fix automatically:
```bash
uv run ruff check src/ --fix
```

### Formatting (Black)

```bash
uv run black src/
```

Check formatting:
```bash
uv run black src/ --check
```

### Type Checking (Mypy)

```bash
uv run mypy src/
```

---

## Project Structure

```text
Phase-1/
├── src/
│   ├── domain/              # Pure business logic (no dependencies)
│   │   ├── task.py          # Task entity with invariants
│   │   └── exceptions.py    # Domain exceptions
│   ├── storage/             # In-memory persistence
│   │   ├── repository_interface.py  # Abstract interface
│   │   └── memory_repository.py     # Dictionary-based implementation
│   ├── cli/                 # User interface
│   │   ├── menu.py          # Main menu loop
│   │   └── operations.py    # CRUD operation handlers
│   └── main.py              # Application entry point
├── tests/
│   ├── unit/                # Unit tests (domain layer)
│   └── integration/         # Integration tests (workflows)
├── pyproject.toml           # Python project configuration
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

---

## Architecture

### Three-Layer Design

**Domain Layer** (`src/domain/`):
- Pure business logic with no dependencies
- Task entity with 10 NON-NEGOTIABLE invariants
- Domain exceptions (DomainValidationError, DomainStateError, TaskNotFoundError)

**Storage Layer** (`src/storage/`):
- In-memory dictionary-based persistence
- Repository pattern with abstract interface
- Enables future database migration (Phase II)

**CLI Layer** (`src/cli/`):
- Menu-driven user interface
- CRUD operation handlers
- Error handling and user-friendly messages

### Dependency Flow

```text
CLI Layer
    ↓ depends on
Storage Layer → implements RepositoryInterface defined by ↴
    ↓ depends on
Domain Layer (pure, no dependencies)
```

---

## Usage Example

```bash
$ uv run python src/main.py

=== Todo Application ===

1. Create Task
2. View All Tasks
3. Update Task
4. Mark Task Complete
5. Delete Task
6. Exit

Choose an option (1-6): 1

Enter task title: Buy groceries
Enter task description (optional): Milk, eggs, bread

✓ Task created successfully! ID: 3f8a92b4

Choose an option (1-6): 2

Total: 1 tasks (1 pending, 0 complete)

ID       | Status | Title           | Created
---------|--------|-----------------|------------------
3f8a92b4 | [ ]    | Buy groceries   | 2026-01-03 10:30
```

---

## Test Coverage

**Current Coverage**: 89.23% (exceeds 80% constitutional requirement)

- **Total Tests**: 91 tests (all passing)
  - Unit Tests: 46 tests (domain and storage layers)
  - Integration Tests: 42 tests (CRUD workflows)
  - E2E Tests: 3 tests (end-to-end user journeys)
- **Coverage by Module**:
  - `src/domain/task.py`: 98%
  - `src/storage/memory_repository.py`: 100%
  - `src/cli/operations.py`: 96%
  - `src/cli/menu.py`: 81%
  - `src/main.py`: 68%

**Note**: Main.py coverage is lower due to exception handling paths and Windows-specific UTF-8 encoding configuration that isn't fully exercised in tests.

---

## Development Workflow

This project follows **Test-Driven Development (TDD)**:

1. **Red**: Write failing test first
2. **Green**: Implement minimal code to pass test
3. **Refactor**: Improve code while tests remain green

**Constitution Principle III (TDD)**: All code changes MUST have tests written FIRST.

---

## Phase II Migration Path

Phase I uses in-memory storage for simplicity. Phase II will migrate to PostgreSQL:

1. Create `PostgresRepository` class implementing same `RepositoryInterface`
2. Update `main.py` to inject `PostgresRepository` instead of `MemoryRepository`
3. Add `user_id` column for multi-user support
4. Domain layer remains unchanged (zero modification required)

**Migration Impact**: One-line change in `main.py` due to dependency inversion

---

## Contributing

1. All changes require approved specification (SDD workflow)
2. All code requires tests written first (TDD workflow)
3. Code quality: ruff, black, mypy must pass (80% coverage minimum)
4. Follow three-layer architecture (no layer violations)

---

## License

Internal project - All rights reserved

---

## Support

For issues or questions, refer to:
- [Specification](../specs/001-task-crud-operations/spec.md)
- [Implementation Plan](../specs/001-task-crud-operations/plan.md)
- [Quickstart Guide](../specs/001-task-crud-operations/quickstart.md)
