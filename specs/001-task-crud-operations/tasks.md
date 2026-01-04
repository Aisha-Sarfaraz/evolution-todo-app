---
description: "Task breakdown for Task CRUD Operations - Phase I In-Memory Console Application"
---

# Tasks: Task CRUD Operations - Phase I

**Input**: Design documents from `/specs/001-task-crud-operations/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are MANDATORY per Constitution Principle III (TDD NON-NEGOTIABLE). All tasks MUST follow Red-Green-Refactor cycle. Tests MUST be written FIRST and FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Phase I**: All code in `Phase-1/` directory (isolated from future phases)
- **Source**: `Phase-1/src/domain/`, `Phase-1/src/storage/`, `Phase-1/src/cli/`
- **Tests**: `Phase-1/tests/unit/`, `Phase-1/tests/integration/`
- Three-layer architecture: Domain (pure logic) → Storage (persistence) → CLI (interface)

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create Phase-1 project structure and configuration

- [X] T001 Create Phase-1 directory structure (src/domain, src/storage, src/cli, tests/)
- [X] T002 [P] Create Python project configuration in Phase-1/pyproject.toml
- [X] T003 [P] Create environment configuration template Phase-1/.env.example
- [X] T004 [P] Create .gitignore for Phase-1
- [X] T005 [P] Create __init__.py files for all Python packages
- [X] T006 [P] Create Phase-1/README.md with setup and usage instructions

---

## Phase 2: Foundational (Domain Layer - Blocking Prerequisites)

**Purpose**: Core domain logic that MUST be complete before ANY user story CLI implementation

**⚠️ CRITICAL**: No CLI operations can begin until domain layer is complete

### Foundation Tests (TDD - Red Phase)

- [X] T007 [P] Write tests for Task entity creation with valid inputs in Phase-1/tests/unit/domain/test_task_entity.py
- [X] T008 [P] Write tests for Task title validation (empty, length, trim) in Phase-1/tests/unit/domain/test_task_entity.py
- [X] T009 [P] Write tests for Task description validation (truncation) in Phase-1/tests/unit/domain/test_task_entity.py
- [X] T010 [P] Write tests for Task lifecycle methods in Phase-1/tests/unit/domain/test_task_lifecycle.py
- [X] T011 [P] Write tests for Task Unicode and edge cases in Phase-1/tests/unit/domain/test_task_validation.py

### Foundation Implementation (TDD - Green Phase)

- [X] T012 Create domain exceptions in Phase-1/src/domain/exceptions.py
- [X] T013 Implement Task entity constructor with validation in Phase-1/src/domain/task.py
- [X] T014 Implement Task title validation (invariants 1-2) in Phase-1/src/domain/task.py
- [X] T015 Implement Task description auto-truncation (invariant 3) in Phase-1/src/domain/task.py
- [X] T016 Implement Task update_title method in Phase-1/src/domain/task.py
- [X] T017 Implement Task update_description method in Phase-1/src/domain/task.py
- [X] T018 Implement Task mark_complete method in Phase-1/src/domain/task.py
- [X] T019 Implement Task to_dict serialization method in Phase-1/src/domain/task.py

### Storage Layer Tests (TDD - Red Phase)

- [X] T020 [P] Write tests for MemoryRepository add operation in Phase-1/tests/unit/storage/test_memory_repository.py
- [X] T021 [P] Write tests for MemoryRepository get operations in Phase-1/tests/unit/storage/test_memory_repository.py
- [X] T022 [P] Write tests for MemoryRepository update and delete in Phase-1/tests/unit/storage/test_memory_repository.py

### Storage Layer Implementation (TDD - Green Phase)

- [X] T023 Create RepositoryInterface abstraction in Phase-1/src/storage/repository_interface.py
- [X] T024 Implement MemoryRepository add operation in Phase-1/src/storage/memory_repository.py
- [X] T025 Implement MemoryRepository get operations (get, get_all) in Phase-1/src/storage/memory_repository.py
- [X] T026 Implement MemoryRepository update and delete operations in Phase-1/src/storage/memory_repository.py

### Foundation Refactor

- [X] T027 Add type hints and docstrings to domain layer (Phase-1/src/domain/)
- [X] T028 Add type hints and docstrings to storage layer (Phase-1/src/storage/)

**Checkpoint**: Domain + Storage layers complete and fully tested (80% coverage minimum)

---

## Phase 3: User Story 1 - Create Task (Priority: P1) 🎯 MVP

**Goal**: User can add new tasks with title and description to track work

**Independent Test**: Run app, create 3 tasks with different titles/descriptions, verify tasks exist in memory

### Tests for User Story 1 (TDD - Red Phase) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T029 [P] [US1] Write integration test for create task with valid inputs in Phase-1/tests/integration/test_create_workflow.py
- [X] T030 [P] [US1] Write integration test for create task with empty title in Phase-1/tests/integration/test_create_workflow.py
- [X] T031 [P] [US1] Write integration test for create task with title > 200 chars in Phase-1/tests/integration/test_create_workflow.py
- [X] T032 [P] [US1] Write integration test for create task with description > 2000 chars in Phase-1/tests/integration/test_create_workflow.py
- [X] T033 [P] [US1] Write integration test for create task with whitespace trimming in Phase-1/tests/integration/test_create_workflow.py
- [X] T034 [P] [US1] Write integration test for create task with Unicode characters in Phase-1/tests/integration/test_create_workflow.py

### Implementation for User Story 1 (TDD - Green Phase)

- [X] T035 [US1] Implement create_task_operation function in Phase-1/src/cli/operations.py
- [X] T036 [US1] Add input prompts for title and description in create_task_operation
- [X] T037 [US1] Add error handling for DomainValidationError in create_task_operation
- [X] T038 [US1] Add success message display with UUID in create_task_operation

**Checkpoint**: User Story 1 complete - can create tasks with validation

---

## Phase 4: User Story 2 - View Tasks (Priority: P2)

**Goal**: User can see all tasks or view specific task details

**Independent Test**: Create 3 tasks (P1), view list, verify all 3 displayed with correct status/title

### Tests for User Story 2 (TDD - Red Phase) ⚠️

- [X] T039 [P] [US2] Write integration test for view all tasks when empty in Phase-1/tests/integration/test_view_workflow.py
- [X] T040 [P] [US2] Write integration test for view all tasks with 5 tasks in Phase-1/tests/integration/test_view_workflow.py
- [X] T041 [P] [US2] Write integration test for view task details by ID in Phase-1/tests/integration/test_view_workflow.py
- [X] T042 [P] [US2] Write integration test for long description truncation in Phase-1/tests/integration/test_view_workflow.py
- [X] T043 [P] [US2] Write integration test for complete task indicator [✓] in Phase-1/tests/integration/test_view_workflow.py
- [X] T044 [P] [US2] Write integration test for pending task indicator [ ] in Phase-1/tests/integration/test_view_workflow.py

### Implementation for User Story 2 (TDD - Green Phase)

- [X] T045 [US2] Implement view_all_tasks_operation function in Phase-1/src/cli/operations.py
- [X] T046 [US2] Add task list formatting (ID, Status, Title, Created) in view_all_tasks_operation
- [X] T047 [US2] Add task summary (Total, Pending, Complete counts) in view_all_tasks_operation
- [X] T048 [US2] Implement view_task_details_operation function in Phase-1/src/cli/operations.py
- [X] T049 [US2] Add full task detail display (all 7 attributes) in view_task_details_operation
- [X] T050 [US2] Add "Task not found" error handling in view operations

**Checkpoint**: User Stories 1 AND 2 complete - can create and view tasks

---

## Phase 5: User Story 3 - Update Task (Priority: P3)

**Goal**: User can edit task title or description

**Independent Test**: Create task (P1), update title from "Old" to "New", view task (P2), verify change persisted

### Tests for User Story 3 (TDD - Red Phase) ⚠️

- [X] T051 [P] [US3] Write integration test for update title only in Phase-1/tests/integration/test_update_workflow.py
- [X] T052 [P] [US3] Write integration test for update description only in Phase-1/tests/integration/test_update_workflow.py
- [X] T053 [P] [US3] Write integration test for update both title and description in Phase-1/tests/integration/test_update_workflow.py
- [X] T054 [P] [US3] Write integration test for update with empty title rejection in Phase-1/tests/integration/test_update_workflow.py
- [X] T055 [P] [US3] Write integration test for update with invalid task ID in Phase-1/tests/integration/test_update_workflow.py
- [X] T056 [P] [US3] Write integration test for update with Enter key (keep current value) in Phase-1/tests/integration/test_update_workflow.py
- [X] T057 [P] [US3] Write integration test for update completed task in Phase-1/tests/integration/test_update_workflow.py
- [X] T058 [P] [US3] Write integration test for update cancellation (Ctrl+C) in Phase-1/tests/integration/test_update_workflow.py

### Implementation for User Story 3 (TDD - Green Phase)

- [X] T059 [US3] Implement update_task_operation function in Phase-1/src/cli/operations.py
- [X] T060 [US3] Add input prompts for new title and description with "keep current" option
- [X] T061 [US3] Add error handling and retry logic for validation errors
- [X] T062 [US3] Add KeyboardInterrupt (Ctrl+C) cancellation handling

**Checkpoint**: User Stories 1, 2, AND 3 complete - can create, view, and update tasks

---

## Phase 6: User Story 4 - Mark Task Complete (Priority: P4)

**Goal**: User can mark tasks as done

**Independent Test**: Create pending task (P1), mark complete (P4), view task (P2), verify status changed to "complete"

### Tests for User Story 4 (TDD - Red Phase) ⚠️

- [X] T063 [P] [US4] Write integration test for mark pending task complete in Phase-1/tests/integration/test_complete_workflow.py
- [X] T064 [P] [US4] Write integration test for mark complete task again (rejected) in Phase-1/tests/integration/test_complete_workflow.py
- [X] T065 [P] [US4] Write integration test for mark complete with invalid task ID in Phase-1/tests/integration/test_complete_workflow.py
- [X] T066 [P] [US4] Write integration test for complete task shows [✓] in list in Phase-1/tests/integration/test_complete_workflow.py
- [X] T067 [P] [US4] Write integration test for mark one task complete (others unchanged) in Phase-1/tests/integration/test_complete_workflow.py

### Implementation for User Story 4 (TDD - Green Phase)

- [X] T068 [US4] Implement mark_complete_operation function in Phase-1/src/cli/operations.py
- [X] T069 [US4] Add success message with completion timestamp
- [X] T070 [US4] Add error handling for DomainStateError (already complete)

**Checkpoint**: User Stories 1-4 complete - full CRUD except delete

---

## Phase 7: User Story 5 - Delete Task (Priority: P5)

**Goal**: User can remove tasks permanently

**Independent Test**: Create 3 tasks (P1), delete middle task (P5), view list (P2), verify only 2 tasks remain

### Tests for User Story 5 (TDD - Red Phase) ⚠️

- [X] T071 [P] [US5] Write integration test for delete task with confirmation (y) in Phase-1/tests/integration/test_delete_workflow.py
- [X] T072 [P] [US5] Write integration test for delete task with declination (n) in Phase-1/tests/integration/test_delete_workflow.py
- [X] T073 [P] [US5] Write integration test for delete with invalid task ID in Phase-1/tests/integration/test_delete_workflow.py
- [X] T074 [P] [US5] Write integration test for delete last task (list becomes empty) in Phase-1/tests/integration/test_delete_workflow.py
- [X] T075 [P] [US5] Write integration test for delete completed task in Phase-1/tests/integration/test_delete_workflow.py

### Implementation for User Story 5 (TDD - Green Phase)

- [X] T076 [US5] Implement delete_task_operation function in Phase-1/src/cli/operations.py
- [X] T077 [US5] Add task details display before confirmation prompt
- [X] T078 [US5] Add confirmation prompt (y/n) with cancellation handling
- [X] T079 [US5] Add success message for deletion

**Checkpoint**: All 5 user stories complete - full CRUD functional

---

## Phase 8: Main Menu & Application Entry

**Purpose**: CLI menu orchestration and application entry point

### Menu Tests (TDD - Red Phase)

- [X] T080 [P] Write integration test for menu display (6 options) in Phase-1/tests/integration/test_menu.py
- [X] T081 [P] Write integration test for menu accepts valid choice (1-6) in Phase-1/tests/integration/test_menu.py
- [X] T082 [P] Write integration test for menu rejects invalid choice in Phase-1/tests/integration/test_menu.py
- [X] T083 [P] Write integration test for menu exits on choice 6 in Phase-1/tests/integration/test_menu.py
- [X] T084 [P] Write integration test for menu option routing (choices 1-5) in Phase-1/tests/integration/test_menu.py
- [X] T085 [P] Write integration test for menu error handling (KeyboardInterrupt, exceptions) in Phase-1/tests/integration/test_menu.py

### Menu Implementation (TDD - Green Phase)

- [X] T086 Implement display_menu function in Phase-1/src/cli/menu.py
- [X] T087 Add menu loop with input capture and validation
- [X] T088 Add menu option routing to CRUD operations
- [X] T089 Add global error handling in menu (never crash)

### Application Entry Tests (TDD - Red Phase)

- [X] T090 [P] Write integration test for main initializes MemoryRepository in Phase-1/tests/integration/test_main.py
- [X] T091 [P] Write integration test for main calls display_menu in Phase-1/tests/integration/test_main.py
- [X] T092 [P] Write integration test for main handles global exceptions in Phase-1/tests/integration/test_main.py
- [X] T093 [P] Write unit test for logging configuration in Phase-1/tests/unit/test_main_logging.py

### Application Entry Implementation (TDD - Green Phase)

- [X] T094 Implement main entry point with dependency injection in Phase-1/src/main.py
- [X] T095 Configure JSON structured logging in Phase-1/src/main.py
- [X] T096 Add global exception handling in Phase-1/src/main.py

**Checkpoint**: Complete application with menu, logging, and error handling

---

## Phase 9: End-to-End Testing

**Purpose**: Validate complete user journeys across all operations

### E2E Tests

- [X] T097 [P] Write E2E test: create → view → update → view (verify changes) in Phase-1/tests/integration/test_e2e.py
- [X] T098 [P] Write E2E test: create → mark complete → view (verify [✓]) in Phase-1/tests/integration/test_e2e.py
- [X] T099 [P] Write E2E test: create multiple → delete one → view (verify count) in Phase-1/tests/integration/test_e2e.py

**Checkpoint**: End-to-end workflows validated

---

## Phase 10: Polish & Quality Assurance

**Purpose**: Code quality, documentation, and final validation

- [X] T100 [P] Run ruff linting on Phase-1/src/ and fix all errors
- [X] T101 [P] Run black formatting on Phase-1/src/
- [X] T102 [P] Run mypy type checking on Phase-1/src/ and fix all errors
- [X] T103 [P] Run pytest with coverage report (target: 80% minimum)
- [X] T104 [P] Verify all tests pass (60-70 tests expected)
- [X] T105 [P] Update Phase-1/README.md with final setup and usage instructions
- [X] T106 Validate quickstart.md instructions (manual walkthrough)

**Checkpoint**: Code quality standards met, ready for Phase II migration

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - User stories CAN proceed in parallel (if staffed)
  - Or sequentially in priority order: US1 → US2 → US3 → US4 → US5
- **Main Menu (Phase 8)**: Depends on all 5 user stories being complete
- **E2E Testing (Phase 9)**: Depends on Phase 8 completion
- **Polish (Phase 10)**: Depends on all implementation phases (1-9)

### User Story Dependencies

- **User Story 1 (P1)**: Independent - can start after Foundational (Phase 2)
- **User Story 2 (P2)**: Independent - can start after Foundational (Phase 2)
- **User Story 3 (P3)**: Independent - can start after Foundational (Phase 2)
- **User Story 4 (P4)**: Independent - can start after Foundational (Phase 2)
- **User Story 5 (P5)**: Independent - can start after Foundational (Phase 2)

**Note**: All user stories are independently testable. Each builds on Domain + Storage foundation.

### Within Each Phase

- Tests (Red phase) MUST be written and FAIL before implementation (Green phase)
- Models before services (not applicable - no separate service layer in Phase I)
- Domain before Storage before CLI
- Tests marked [P] can run in parallel (different files)

### Parallel Opportunities

**Phase 1 (Setup)**: Tasks T002-T006 can run in parallel

**Phase 2 (Foundational)**:
- Tests T007-T011 can run in parallel
- Tests T020-T022 can run in parallel
- Refactor tasks T027-T028 can run in parallel

**Phase 3 (User Story 1)**:
- Tests T029-T034 can run in parallel

**Phase 4 (User Story 2)**:
- Tests T039-T044 can run in parallel

**Phase 5 (User Story 3)**:
- Tests T051-T058 can run in parallel

**Phase 6 (User Story 4)**:
- Tests T063-T067 can run in parallel

**Phase 7 (User Story 5)**:
- Tests T071-T075 can run in parallel

**Phase 8 (Main Menu)**:
- Menu tests T080-T085 can run in parallel
- App entry tests T090-T093 can run in parallel

**Phase 9 (E2E)**:
- E2E tests T097-T099 can run in parallel

**Phase 10 (Polish)**:
- Quality tasks T100-T105 can run in parallel

**Cross-Phase Parallelism**:
- After Foundational phase (Phase 2) completes, ALL user story phases (3-7) can run in parallel by different developers

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (Red phase):
Task T029: "Write integration test for create task with valid inputs"
Task T030: "Write integration test for create task with empty title"
Task T031: "Write integration test for create task with title > 200 chars"
Task T032: "Write integration test for create task with description > 2000 chars"
Task T033: "Write integration test for create task with whitespace trimming"
Task T034: "Write integration test for create task with Unicode characters"

# After tests written and FAILING, implement (Green phase):
Task T035: "Implement create_task_operation function"
Task T036: "Add input prompts for title and description"
Task T037: "Add error handling for DomainValidationError"
Task T038: "Add success message display with UUID"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T028) - CRITICAL blocking phase
3. Complete Phase 3: User Story 1 (T029-T038)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Demo minimal viable product (can create tasks)

### Incremental Delivery (Recommended)

1. Complete Setup + Foundational (T001-T028) → Foundation ready
2. Add User Story 1 (T029-T038) → Test independently → **Deploy/Demo MVP!**
3. Add User Story 2 (T039-T050) → Test independently → Deploy/Demo (can view)
4. Add User Story 3 (T051-T062) → Test independently → Deploy/Demo (can update)
5. Add User Story 4 (T063-T070) → Test independently → Deploy/Demo (can complete)
6. Add User Story 5 (T071-T079) → Test independently → Deploy/Demo (full CRUD)
7. Add Menu (T080-T096) → Complete application
8. Add E2E tests (T097-T099) → Validate workflows
9. Polish (T100-T106) → Production ready

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T028)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T029-T038)
   - **Developer B**: User Story 2 (T039-T050)
   - **Developer C**: User Story 3 (T051-T062)
   - **Developer D**: User Story 4 (T063-T070)
   - **Developer E**: User Story 5 (T071-T079)
3. Stories complete independently, then integrate in Phase 8 (Menu)

---

## Task Summary

**Total Tasks**: 106 tasks

**Breakdown by Phase**:
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 22 tasks (11 test tasks + 11 implementation tasks)
- Phase 3 (User Story 1): 10 tasks (6 test tasks + 4 implementation tasks)
- Phase 4 (User Story 2): 12 tasks (6 test tasks + 6 implementation tasks)
- Phase 5 (User Story 3): 12 tasks (8 test tasks + 4 implementation tasks)
- Phase 6 (User Story 4): 8 tasks (5 test tasks + 3 implementation tasks)
- Phase 7 (User Story 5): 9 tasks (5 test tasks + 4 implementation tasks)
- Phase 8 (Main Menu & Entry): 17 tasks (10 test tasks + 7 implementation tasks)
- Phase 9 (E2E Testing): 3 tasks
- Phase 10 (Polish): 7 tasks

**Test Tasks**: 56 tasks (53% of total - TDD mandate satisfied)
**Implementation Tasks**: 50 tasks (47% of total)

**Parallel Opportunities**: 61 tasks marked [P] can run in parallel

**Independent Test Criteria**:
- US1: Create 3 tasks, verify in memory
- US2: Create 3 tasks, view list, verify all displayed
- US3: Create task, update title, view, verify change
- US4: Create pending task, mark complete, view, verify [✓]
- US5: Create 3 tasks, delete one, view, verify count

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 38 tasks

---

## Format Validation ✅

**Checklist Format Compliance**:
- ✅ All tasks start with `- [ ]` (checkbox)
- ✅ All tasks have sequential IDs (T001-T106)
- ✅ Parallelizable tasks marked with [P]
- ✅ User story tasks labeled [US1], [US2], [US3], [US4], [US5]
- ✅ Setup/Foundational/Polish tasks have NO story label
- ✅ All tasks include file paths in descriptions
- ✅ Tasks organized by user story for independent implementation
- ✅ TDD mandate satisfied (tests before implementation, 56 test tasks)

**Ready for `/sp.implement` execution**

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story independently completable and testable
- **TDD NON-NEGOTIABLE**: All tests MUST be written FIRST and FAIL before implementation
- Verify tests fail (Red) → Implement (Green) → Refactor → Commit
- Stop at any checkpoint to validate story independently
- Phase I isolation: All code in `Phase-1/` directory
- Three-layer architecture: Domain → Storage → CLI
- 80% minimum test coverage required (Constitution Principle III)
