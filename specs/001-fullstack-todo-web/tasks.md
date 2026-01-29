# Tasks: Full-Stack Todo Web Application

**Feature**: 001-fullstack-todo-web
**Input**: Design documents from `specs/001-fullstack-todo-web/` (spec.md, plan.md)
**Prerequisites**: plan.md (1021 lines), spec.md (846 lines, 7 user stories, 100 functional requirements)

**Tests**: Tests are MANDATORY per Constitution Principle III (TDD NON-NEGOTIABLE). All tasks MUST include test tasks following Red-Green-Refactor cycle. Tests MUST be written FIRST and FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Path Conventions

- **Backend**: `phase-2/backend/src/`, `phase-2/backend/tests/`
- **Frontend**: `phase-2/frontend/app/`, `phase-2/frontend/components/`, `phase-2/frontend/lib/`
- **Migrations**: `phase-2/backend/migrations/versions/`

---

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETE

**Purpose**: Project initialization and basic structure

- [X] T001 Create phase-2/backend directory structure per plan.md (src/, tests/, migrations/)
- [X] T002 Create phase-2/frontend directory structure per plan.md (app/, components/, lib/)
- [X] T003 Initialize backend pyproject.toml with dependencies (FastAPI>=0.115.0, SQLModel>=0.0.22, Alembic>=1.13.0, asyncpg>=0.29.0, pyjwt>=2.9.0, passlib[bcrypt]>=1.7.4)
- [X] T004 [P] Initialize frontend package.json with dependencies (next@^16.0.0, react@^19.0.0, better-auth@^0.8.0, @tanstack/react-query@^5.59.0, tailwindcss@^3.4.0)
- [X] T005 [P] Configure backend .env.example with placeholders (DATABASE_URL, BETTER_AUTH_SECRET, JWT_SECRET_KEY)
- [X] T006 [P] Configure frontend .env.local.example with placeholders (NEXT_PUBLIC_API_URL, BETTER_AUTH_URL)
- [X] T007 [P] Configure ruff and mypy for backend in pyproject.toml
- [X] T008 [P] Configure ESLint and TypeScript strict mode for frontend in tsconfig.json

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETE

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Schema & Migrations

- [x] T009 Generate Alembic migration: Create users table in phase-2/backend/migrations/versions/001_create_users_table.py (id UUID PK, email VARCHAR(255) UNIQUE, password_hash VARCHAR(255), email_verified BOOLEAN, display_name VARCHAR(100), created_at TIMESTAMP, last_signin_at TIMESTAMP)
- [x] T010 [P] Generate Alembic migration: Create categories table in phase-2/backend/migrations/versions/002_create_categories_table.py (id UUID PK, user_id UUID FK, name VARCHAR(100), is_system BOOLEAN, color VARCHAR(7), created_at TIMESTAMP, UNIQUE(user_id, LOWER(name)))
- [x] T011 [P] Generate Alembic migration: Create tags table in phase-2/backend/migrations/versions/003_create_tags_table.py (id UUID PK, user_id UUID FK, name VARCHAR(50), created_at TIMESTAMP, UNIQUE(user_id, LOWER(name)))
- [x] T012 Generate Alembic migration: Create tasks table in phase-2/backend/migrations/versions/004_create_tasks_table.py (id UUID PK, user_id UUID FK, title VARCHAR(200), description TEXT, status VARCHAR(20), priority VARCHAR(20), category_id UUID FK nullable, created_at TIMESTAMP, updated_at TIMESTAMP, completed_at TIMESTAMP nullable, CHECK constraints for status and priority)
- [x] T013 Generate Alembic migration: Create task_tag join table in phase-2/backend/migrations/versions/005_create_task_tag_table.py (task_id UUID FK, tag_id UUID FK, created_at TIMESTAMP, PRIMARY KEY (task_id, tag_id))
- [x] T014 Generate Alembic migration: Create indexes in phase-2/backend/migrations/versions/006_create_indexes.py (idx_tasks_user_id, idx_tasks_user_status, idx_tasks_user_priority, idx_tasks_fulltext GIN, composite indexes per plan.md)
- [x] T015 Generate Alembic migration: Insert system categories in phase-2/backend/migrations/versions/007_insert_system_categories.py (Work, Personal, Shopping, Health, Fitness, Finance, Education, Home with colors from plan.md)
- [x] T016 Execute all Alembic migrations against Neon PostgreSQL database

### Backend Domain Models

- [x] T017 [P] Create User SQLModel in phase-2/backend/src/models/user.py (id, email, password_hash, email_verified, display_name, created_at, last_signin_at, relationships)
- [x] T018 [P] Create Category SQLModel in phase-2/backend/src/models/category.py (id, user_id nullable, name, is_system, color, created_at, unique constraint)
- [x] T019 [P] Create Tag SQLModel in phase-2/backend/src/models/tag.py (id, user_id, name, created_at, unique constraint)
- [x] T020 Create Task SQLModel in phase-2/backend/src/models/task.py (id, user_id, title, description, status, priority, category_id nullable, created_at, updated_at, completed_at nullable, relationships to User/Category/Tags, CHECK constraints)
- [x] T021 [P] Create TaskTag SQLModel in phase-2/backend/src/models/task_tag.py (task_id, tag_id, created_at, composite primary key)

### Backend Infrastructure

- [x] T022 Implement database connection in phase-2/backend/src/database.py (async engine, session factory, connection pool min=5 max=20)
- [x] T023 Implement JWT validation dependency in phase-2/backend/src/api/dependencies.py (get_current_user function: decode JWT, validate signature, check expiration, return user_id, raise 401 on invalid/expired)
- [x] T024 Implement URL user_id validation dependency in phase-2/backend/src/api/dependencies.py (validate_user_id_match function: compare URL user_id vs JWT user_id, raise 403 if mismatch)
- [x] T025 [P] Implement password hashing utilities in phase-2/backend/src/utils/auth.py (hash_password using bcrypt 10+ rounds, verify_password)
- [x] T026 [P] Implement error response formatter in phase-2/backend/src/utils/errors.py (format error_code, detail, field for consistent error responses)

### Frontend Core Setup

- [x] T027 Configure Better Auth client in phase-2/frontend/lib/auth/better-auth.ts (betterAuth config with email/password provider, session management, CSRF settings)
- [x] T028 Implement API client wrapper in phase-2/frontend/lib/api/client.ts (apiClient<T> function: JWT injection, token refresh on 401, error parsing, TypeScript generics)
- [x] T029 Create Next.js 16 authentication proxy in phase-2/frontend/proxy.ts (session validation, protected route detection, redirect unauthenticated users to /signin)
- [x] T030 [P] Configure TanStack Query provider in phase-2/frontend/app/providers.tsx (QueryClientProvider with staleTime, cacheTime settings)
- [x] T031 [P] Create TypeScript types for Task in phase-2/frontend/lib/types/task.ts (match backend Task SQLModel schema)
- [x] T032 [P] Create TypeScript types for Category in phase-2/frontend/lib/types/category.ts (match backend Category SQLModel schema)
- [x] T033 [P] Create TypeScript types for Tag in phase-2/frontend/lib/types/tag.ts (match backend Tag SQLModel schema)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration & Authentication (Priority: P1) 🎯 MVP ✅ COMPLETE

**Goal**: Enable secure user registration, email verification, signin/signout, password reset, and profile management

**Independent Test**: Complete registration flow → receive verification email → click verification link → sign in with credentials → access protected dashboard → navigate to profile → update display name → sign out → reset password via email → sign in with new password

**Mapped Requirements**: FR-001 to FR-010 (Authentication & Authorization)

### Tests for User Story 1 (REQUIRED - TDD NON-NEGOTIABLE) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T034 [P] [US1] Unit test for password hashing in phase-2/backend/tests/unit/test_auth_utils.py (test hash_password bcrypt, verify_password correct/incorrect, hash uniqueness with same password)
- [x] T035 [P] [US1] Unit test for JWT validation in phase-2/backend/tests/unit/test_jwt_validation.py (test get_current_user valid token, expired token raises 401, malformed token raises 401, missing token raises 401)
- [x] T036 [P] [US1] Integration test for signup flow in phase-2/backend/tests/integration/test_auth_signup.py (test valid registration returns 201, duplicate email returns 422, weak password returns 422, password mismatch returns 422)
- [x] T037 [P] [US1] Integration test for signin flow in phase-2/backend/tests/integration/test_auth_signin.py (test correct credentials returns 200 + tokens, incorrect password returns 401, unverified email blocks signin)
- [x] T038 [P] [US1] Integration test for password reset in phase-2/backend/tests/integration/test_auth_password_reset.py (test request reset sends email, valid reset token updates password, expired token returns 401)

### Implementation for User Story 1

**Backend Auth Endpoints**:

- [x] T039 [US1] Implement POST /api/auth/signup endpoint in phase-2/backend/src/api/routes/auth.py (validate email/password, hash password, create user, send verification email, return 201 with user_id)
- [x] T040 [US1] Implement POST /api/auth/verify-email endpoint in phase-2/backend/src/api/routes/auth.py (validate token, mark email_verified=true, return 200)
- [x] T041 [US1] Implement POST /api/auth/signin endpoint in phase-2/backend/src/api/routes/auth.py (verify email/password, check email_verified, issue JWT access + refresh tokens, update last_signin_at, return 200 + tokens)
- [x] T042 [US1] Implement POST /api/auth/refresh endpoint in phase-2/backend/src/api/routes/auth.py (validate refresh token, issue new access token, return 200)
- [x] T043 [US1] Implement POST /api/auth/signout endpoint in phase-2/backend/src/api/routes/auth.py (clear tokens, return 204)
- [x] T044 [US1] Implement POST /api/auth/reset-password-request endpoint in phase-2/backend/src/api/routes/auth.py (validate email, generate reset token, send reset email, return 200)
- [x] T045 [US1] Implement POST /api/auth/reset-password endpoint in phase-2/backend/src/api/routes/auth.py (validate reset token, hash new password, update password_hash, invalidate refresh tokens, return 200)
- [x] T046 [US1] Implement GET /api/{user_id}/profile endpoint in phase-2/backend/src/api/routes/auth.py (return user email, created_at, last_signin_at, display_name)
- [x] T047 [US1] Implement PUT /api/{user_id}/profile endpoint in phase-2/backend/src/api/routes/auth.py (update display_name and/or password, validate current password for password change, return 200)

**Frontend Auth Pages & Components**:

- [x] T048 [P] [US1] Create auth layout in phase-2/frontend/app/(auth)/layout.tsx (centered form layout, server component)
- [x] T049 [P] [US1] Create signup page in phase-2/frontend/app/(auth)/signup/page.tsx (server component, renders SignupForm)
- [x] T050 [P] [US1] Create signin page in phase-2/frontend/app/(auth)/signin/page.tsx (server component, renders SigninForm)
- [x] T051 [P] [US1] Create verify-email page in phase-2/frontend/app/(auth)/verify-email/page.tsx (server component, extract token from URL, call verify endpoint)
- [x] T052 [P] [US1] Create reset-password page in phase-2/frontend/app/(auth)/reset-password/page.tsx (server component, renders ResetPasswordForm)
- [x] T053 [P] [US1] Create signup form component in phase-2/frontend/components/auth/signup-form.tsx (client component, React Hook Form validation, password strength check, call signup API)
- [x] T054 [P] [US1] Create signin form component in phase-2/frontend/components/auth/signin-form.tsx (client component, React Hook Form, call signin API, handle 401/403 errors)
- [x] T055 [P] [US1] Create reset password form component in phase-2/frontend/components/auth/reset-password-form.tsx (client component, validate new password, call reset API)
- [x] T056 [US1] Create profile page in phase-2/frontend/app/(dashboard)/profile/page.tsx (server component, fetch user profile, display email/created_at/last_signin_at, editable display_name)
- [x] T057 [US1] Create profile edit component in phase-2/frontend/components/auth/profile-edit-form.tsx (client component, update display_name, change password with current password validation)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently (users can register, verify email, signin, reset password, update profile)

---

## Phase 4: User Story 2 - Core Task Management (Priority: P2) 🎯 MVP ✅ COMPLETE

**Goal**: Authenticated users can create, view, update, delete, and mark tasks as complete with strict user isolation

**Independent Test**: User signs in → creates 3 tasks ("Buy groceries", "Team meeting", "Write report") → views list showing all 3 tasks → opens "Team meeting" task detail → updates title to "Team meeting notes" → marks "Buy groceries" as complete → deletes "Write report" → views list showing 2 remaining tasks (1 pending, 1 complete)

**Mapped Requirements**: FR-011 to FR-020 (Task Management), FR-051 to FR-056 (Task Endpoints)

### Tests for User Story 2 (REQUIRED - TDD NON-NEGOTIABLE) ⚠️

- [x] T058 [P] [US2] Unit test for Task model validation in phase-2/backend/tests/unit/test_task_model.py (test title non-empty, title ≤200 chars, description truncation at 2000 chars, status enum validation, priority enum validation)
- [x] T059 [P] [US2] Integration test for task creation in phase-2/backend/tests/integration/test_task_create.py (test valid task returns 201, empty title returns 422, title >200 chars returns 422, user_id mismatch returns 403)
- [x] T060 [P] [US2] Integration test for task list in phase-2/backend/tests/integration/test_task_list.py (test user A sees only user A tasks, user B sees only user B tasks, empty list returns empty array)
- [x] T061 [P] [US2] Integration test for task update in phase-2/backend/tests/integration/test_task_update.py (test valid update returns 200 + updated task, cross-user update returns 403, empty title returns 422)
- [x] T062 [P] [US2] Integration test for task completion in phase-2/backend/tests/integration/test_task_complete.py (test toggle pending→complete sets completed_at, toggle complete→pending clears completed_at, cross-user toggle returns 403)
- [x] T063 [P] [US2] Integration test for task deletion in phase-2/backend/tests/integration/test_task_delete.py (test valid deletion returns 204, cross-user deletion returns 403, non-existent task returns 404)

### Implementation for User Story 2

**Backend Task Endpoints**:

- [x] T064 [US2] Implement GET /api/{user_id}/tasks endpoint in phase-2/backend/src/api/routes/tasks.py (list all tasks for user, validate user_id, filter by user_id, sort by created_at DESC default, return 200 + tasks array with populated category and tags)
- [x] T065 [US2] Implement POST /api/{user_id}/tasks endpoint in phase-2/backend/src/api/routes/tasks.py (validate user_id, parse JSON payload {title, description?, priority?, category_id?, tags?}, validate title non-empty ≤200 chars, truncate description at 2000 chars, set user_id from JWT, return 201 + task object)
- [x] T066 [US2] Implement GET /api/{user_id}/tasks/{id} endpoint in phase-2/backend/src/api/routes/tasks.py (validate user_id, fetch task by id AND user_id, return 404 if not found or cross-user access, return 200 + task with populated category and tags)
- [x] T067 [US2] Implement PUT /api/{user_id}/tasks/{id} endpoint in phase-2/backend/src/api/routes/tasks.py (validate user_id, parse JSON payload {title?, description?, priority?, category_id?, tags?}, validate fields, update task, set updated_at to NOW(), return 200 + updated task)
- [x] T068 [US2] Implement DELETE /api/{user_id}/tasks/{id} endpoint in phase-2/backend/src/api/routes/tasks.py (validate user_id, delete task by id AND user_id, return 404 if not found, return 204 on success)
- [x] T069 [US2] Implement PATCH /api/{user_id}/tasks/{id}/complete endpoint in phase-2/backend/src/api/routes/tasks.py (toggle status pending↔complete, set/clear completed_at, return 200 + updated task)

**Frontend Task Pages & Components**:

- [x] T070 [P] [US2] Create dashboard layout in phase-2/frontend/app/(dashboard)/layout.tsx (sidebar navigation, header with user info, signout button, server component)
- [x] T071 [US2] Create tasks list page in phase-2/frontend/app/(dashboard)/tasks/page.tsx (server component, fetch tasks via apiClient, render TaskList component)
- [x] T072 [P] [US2] Create task list component in phase-2/frontend/components/tasks/task-list.tsx (server component, map tasks to TaskCard components, empty state if no tasks)
- [x] T073 [P] [US2] Create task card component in phase-2/frontend/components/tasks/task-card.tsx (server component, display title, status indicator, created_at, priority badge, category badge, tags)
- [x] T074 [US2] Create task form component in phase-2/frontend/components/tasks/task-form.tsx (client component, React Hook Form, create/edit modes, title/description inputs, TanStack Query mutation with optimistic update)
- [x] T075 [US2] Create task detail modal component in phase-2/frontend/components/tasks/task-detail-modal.tsx (client component, display full task details, edit button opens TaskForm in edit mode)
- [x] T076 [US2] Create task actions component in phase-2/frontend/components/tasks/task-actions.tsx (client component, complete/uncomplete checkbox, delete button with confirmation, TanStack Query mutations)
- [x] T077 [US2] Implement task API methods in phase-2/frontend/lib/api/tasks.ts (getTasks, createTask, updateTask, deleteTask, toggleComplete using apiClient wrapper)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently (users can manage tasks with full CRUD + completion)

---

## Phase 5: User Story 3 - User Isolation & Security (Priority: P3) ✅ COMPLETE

**Goal**: Guarantee strict user data isolation, audit logging, rate limiting, and security event monitoring

**Independent Test**: User A creates task → User B attempts to view/update/delete User A's task via API with User B's valid JWT → all attempts return 403 Forbidden or 404 Not Found → audit log records attempted unauthorized access with user_id, task_id, timestamp, IP address

**Mapped Requirements**: FR-064 to FR-070 (Security & Validation), FR-079 to FR-087 (Security & Error Handling)

### Tests for User Story 3 (REQUIRED - TDD NON-NEGOTIABLE) ⚠️

- [x] T078 [P] [US3] Integration test for cross-user task access in phase-2/backend/tests/integration/test_user_isolation.py (test User B GET User A's task returns 404, User B PUT User A's task returns 403, User B DELETE User A's task returns 403)
- [x] T079 [P] [US3] Integration test for JWT validation in phase-2/backend/tests/integration/test_jwt_security.py (test missing token returns 401, expired token returns 401, malformed token returns 401, modified payload signature fails)
- [x] T080 [P] [US3] Integration test for rate limiting in phase-2/backend/tests/integration/test_rate_limiting.py (test 101st request within 1 minute returns 429 with Retry-After header)
- [x] T081 [P] [US3] Integration test for account lockout in phase-2/backend/tests/integration/test_account_lockout.py (test 5 failed signin attempts locks account for 15 minutes)
- [x] T082 [P] [US3] Integration test for audit logging in phase-2/backend/tests/integration/test_audit_logging.py (test unauthorized access logged, failed signin logged, password change logged)

### Implementation for User Story 3

**Backend Security Enhancements**:

- [x] T083 [US3] Implement rate limiting middleware in phase-2/backend/src/middleware/rate_limit.py (100 requests/minute per user using Redis/in-memory counter, return 429 with Retry-After header)
- [x] T084 [US3] Implement account lockout logic in phase-2/backend/src/utils/auth.py (track failed signin attempts in Redis, lock account for 15 minutes after 5 failures)
- [x] T085 [US3] Implement audit logging in phase-2/backend/src/utils/logging.py (structured JSON logging with timestamp, level, user_id, request_id, event type, IP address, context)
- [x] T086 [US3] Add audit log calls to auth endpoints in phase-2/backend/src/api/routes/auth.py (log failed signin, unauthorized access, password changes, email verification)
- [x] T087 [US3] Add audit log calls to task endpoints in phase-2/backend/src/api/routes/tasks.py (log cross-user access attempts with 403 responses)
- [x] T088 [US3] Implement Row-Level Security setup script in phase-2/backend/scripts/setup_rls.py (ALTER TABLE tasks ENABLE ROW LEVEL SECURITY, CREATE POLICY tasks_user_isolation USING (user_id = current_setting('app.current_user_id')::UUID))

**Frontend Security Enhancements**:

- [x] T089 [US3] Implement error boundary in phase-2/frontend/app/error.tsx (catch unhandled errors, display fallback UI)
- [x] T090 [US3] Add CSRF token handling to API client in phase-2/frontend/lib/api/client.ts (read CSRF token from cookie, include in request headers)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work with complete security enforcement (user isolation validated, audit logging active, rate limiting enforced)

---

## Phase 6: User Story 4 - API Contracts & Documentation (Priority: P4) ✅ COMPLETE

**Goal**: Provide auto-generated interactive API documentation at /docs with all endpoints, request/response schemas, and consistent error handling

**Independent Test**: Developer accesses `/docs` endpoint → sees Swagger UI with all 15+ API endpoints documented → selects `POST /api/{user_id}/tasks` → reviews request schema (title: string required, description: string optional, priority, category, tags) → clicks "Try it out" → fills sample data → executes request → receives 201 Created response with task object

**Mapped Requirements**: FR-051 to FR-070 (API Contracts), FR-068 (Error Response Format), FR-069 (API Documentation)

### Tests for User Story 4 (REQUIRED - TDD NON-NEGOTIABLE) ⚠️

- [x] T091 [P] [US4] Integration test for OpenAPI schema generation in phase-2/backend/tests/integration/test_openapi_schema.py (test /openapi.json returns valid OpenAPI 3.0 spec, all endpoints documented, request/response schemas present)
- [x] T092 [P] [US4] Integration test for error response format in phase-2/backend/tests/integration/test_error_responses.py (test 401 returns {error_code, detail}, 403 returns {error_code, detail}, 404 returns {error_code, detail}, 422 returns {error_code, detail, field}, 500 returns {error_code, detail, request_id})

### Implementation for User Story 4

**Backend API Documentation**:

- [x] T093 [US4] Configure FastAPI OpenAPI metadata in phase-2/backend/src/main.py (title, version, description, contact, license)
- [x] T094 [US4] Add request/response schema documentation to auth endpoints in phase-2/backend/src/api/routes/auth.py (Pydantic models for SignupRequest, SigninRequest, ResetPasswordRequest, UserProfile with field descriptions)
- [x] T095 [US4] Add request/response schema documentation to task endpoints in phase-2/backend/src/api/routes/tasks.py (Pydantic models for CreateTaskRequest, UpdateTaskRequest, TaskResponse with examples)
- [x] T096 [US4] Add request/response schema documentation to category endpoints in phase-2/backend/src/api/routes/categories.py (Pydantic models for CreateCategoryRequest, CategoryResponse)
- [x] T097 [US4] Add request/response schema documentation to tag endpoints in phase-2/backend/src/api/routes/tags.py (Pydantic models for CreateTagRequest, UpdateTagRequest, TagResponse)
- [x] T098 [US4] Implement consistent error handler in phase-2/backend/src/api/error_handlers.py (register exception handlers for ValidationError, HTTPException, generic Exception returning {error_code, detail, field?, request_id?})

**Checkpoint**: At this point, all API endpoints are fully documented with interactive Swagger UI at /docs

---

## Phase 7: User Story 5 - Task Organization (Priorities, Categories, Tags) (Priority: P5) ✅ COMPLETE

**Goal**: Enable task organization via priorities (Low/Medium/High/Urgent), predefined + custom categories, and user-created tags with multi-tag assignment

**Independent Test**: User creates task "Prepare presentation" → assigns priority "High" → selects category "Work" → creates tags "meeting", "urgent", "q1-goals" → assigns all 3 tags to task → views task list filtered by "Work" category showing task → views task list filtered by "urgent" tag showing task → sorts task list by priority showing "High" tasks first

**Mapped Requirements**: FR-021 to FR-035 (Task Organization), FR-057 to FR-063 (Category & Tag Endpoints)

### Tests for User Story 5 (REQUIRED - TDD NON-NEGOTIABLE) ⚠️

- [x] T099 [P] [US5] Unit test for priority validation in phase-2/backend/tests/unit/test_priority_validation.py (test valid priorities accepted, invalid priority returns 422, default priority is Medium)
- [x] T100 [P] [US5] Integration test for category management in phase-2/backend/tests/integration/test_categories.py (test create custom category, list includes system + custom categories, cannot delete system category, deleting custom category sets task.category_id=null)
- [x] T101 [P] [US5] Integration test for tag management in phase-2/backend/tests/integration/test_tags.py (test create tag, tag name uniqueness case-insensitive, assign multiple tags to task, remove tag from task, delete tag removes all TaskTag associations, rename tag updates all tasks)

### Implementation for User Story 5

**Backend Category & Tag Endpoints**:

- [x] T102 [US5] Implement GET /api/{user_id}/categories endpoint in phase-2/backend/src/api/routes/categories.py (list all categories: system categories (user_id=null) + user's custom categories, return 200 + categories array)
- [x] T103 [US5] Implement POST /api/{user_id}/categories endpoint in phase-2/backend/src/api/routes/categories.py (validate name unique per user case-insensitive, create category with user_id, return 201 + category object)
- [x] T104 [US5] Implement DELETE /api/{user_id}/categories/{id} endpoint in phase-2/backend/src/api/routes/categories.py (check is_system=false, set task.category_id=null for all tasks using category, delete category, return 204)
- [x] T105 [US5] Implement GET /api/{user_id}/tags endpoint in phase-2/backend/src/api/routes/tags.py (list all tags for user sorted alphabetically, return 200 + tags array)
- [x] T106 [US5] Implement POST /api/{user_id}/tags endpoint in phase-2/backend/src/api/routes/tags.py (validate name unique per user case-insensitive, trim whitespace, create tag with user_id, return 201 + tag object)
- [x] T107 [US5] Implement PUT /api/{user_id}/tags/{id} endpoint in phase-2/backend/src/api/routes/tags.py (rename tag, validate new name unique, update Tag.name, return 200 + updated tag object)
- [x] T108 [US5] Implement DELETE /api/{user_id}/tags/{id} endpoint in phase-2/backend/src/api/routes/tags.py (delete all TaskTag associations via ON DELETE CASCADE, delete tag, return 204)
- [x] T109 [US5] Update PUT /api/{user_id}/tasks/{id} endpoint to handle tags in phase-2/backend/src/api/routes/tasks.py (accept tags array in request, delete existing TaskTag associations, create new TaskTag associations, return task with populated tags)

**Frontend Organization Features**:

- [x] T110 [P] [US5] Create categories management page in phase-2/frontend/app/(dashboard)/categories/page.tsx (server component, fetch categories, render category list with create/delete actions)
- [x] T111 [P] [US5] Create tags management page in phase-2/frontend/app/(dashboard)/tags/page.tsx (server component, fetch tags, render tag list with create/rename/delete actions)
- [x] T112 [US5] Update task form component to include priority dropdown in phase-2/frontend/components/tasks/task-form.tsx (add priority select: Low/Medium/High/Urgent, default Medium)
- [x] T113 [US5] Update task form component to include category selector in phase-2/frontend/components/tasks/task-form.tsx (add category dropdown, fetch categories via API, allow null selection)
- [x] T114 [US5] Update task form component to include tag multi-selector in phase-2/frontend/components/tasks/task-form.tsx (add tag multi-select with autocomplete, fetch user tags via API, allow creating new tags inline)
- [x] T115 [US5] Update task card component to display priority badge in phase-2/frontend/components/tasks/task-card.tsx (color-coded priority badges: red=Urgent, orange=High, yellow=Medium, green=Low)
- [x] T116 [US5] Update task card component to display category badge in phase-2/frontend/components/tasks/task-card.tsx (display category name with category color)
- [x] T117 [US5] Update task card component to display tag badges in phase-2/frontend/components/tasks/task-card.tsx (display all tags as small chips)

**Checkpoint**: At this point, users can organize tasks with priorities, categories, and tags

---

## Phase 8: User Story 6 - Task Discovery (Search, Filter, Sort) (Priority: P6) ✅ COMPLETE

**Goal**: Enable full-text search, multi-field filtering (status, priority, category, tags, date ranges), sorting, and combined operations for efficient task discovery at scale

**Independent Test**: User has 50 tasks → enters search query "meeting" → system returns 8 tasks containing "meeting" in title or description → user adds filter "priority=High" → system narrows results to 3 high-priority meeting tasks → user sorts by created_at DESC → system displays 3 tasks newest first → user clears filters → applies tag filter "urgent" AND "q1-goals" → system returns only tasks with both tags

**Mapped Requirements**: FR-036 to FR-050 (Task Discovery), FR-051 (Task List Endpoint Query Parameters)

### Tests for User Story 6 (REQUIRED - TDD NON-NEGOTIABLE) ⚠️

- [x] T118 [P] [US6] Integration test for full-text search in phase-2/backend/tests/integration/test_task_search.py (test search by title, search by description, search with special characters, empty search returns all tasks, case-insensitive search)
- [x] T119 [P] [US6] Integration test for task filtering in phase-2/backend/tests/integration/test_task_filters.py (test filter by status, filter by priority (single + multiple), filter by category, filter by tags with AND logic, filter by date ranges created_after/before)
- [x] T120 [P] [US6] Integration test for task sorting in phase-2/backend/tests/integration/test_task_sorting.py (test sort by priority desc/asc, sort by title A-Z/Z-A, sort by created_at desc/asc, default sort is created_at desc)
- [x] T121 [P] [US6] Integration test for combined search+filter+sort in phase-2/backend/tests/integration/test_task_combined_query.py (test search "meeting" + priority=High + status=pending + sort=created_at desc)
- [x] T122 [P] [US6] Performance test for large dataset in phase-2/backend/tests/performance/test_task_performance.py (test search on 1000+ tasks completes in <2s p95, filter on 1000+ tasks completes in <1s p95, sort on 1000+ tasks completes in <500ms p95)

### Implementation for User Story 6

**Backend Search, Filter, Sort Logic**:

- [x] T123 [US6] Implement search query parameter parsing in phase-2/backend/src/api/routes/tasks.py (accept search query param, perform full-text search using GIN index: WHERE to_tsvector('english', title || ' ' || description) @@ plainto_tsquery('english', search), escape special characters)
- [x] T124 [US6] Implement status filter in phase-2/backend/src/api/routes/tasks.py (accept status query param {pending, complete, all}, add WHERE status=? clause if not "all")
- [x] T125 [US6] Implement priority filter in phase-2/backend/src/api/routes/tasks.py (accept priority query param comma-separated, add WHERE priority IN (?) clause with OR logic)
- [x] T126 [US6] Implement category filter in phase-2/backend/src/api/routes/tasks.py (accept category query param UUID, add WHERE category_id=? clause)
- [x] T127 [US6] Implement tags filter with AND logic in phase-2/backend/src/api/routes/tasks.py (accept tags query param comma-separated, JOIN task_tag, GROUP BY task.id, HAVING COUNT(DISTINCT tag_id) = number of requested tags for AND logic)
- [x] T128 [US6] Implement date range filters in phase-2/backend/src/api/routes/tasks.py (accept created_after/before, updated_after/before, completed_after/before as ISO 8601, add WHERE clauses with date comparisons, validate start ≤ end)
- [x] T129 [US6] Implement sorting in phase-2/backend/src/api/routes/tasks.py (accept sort_by {priority, created_at, updated_at, title} and order {asc, desc}, add ORDER BY clause, default: created_at DESC)
- [x] T130 [US6] Combine all filters+search+sort in single query in phase-2/backend/src/api/routes/tasks.py (build SQLAlchemy query progressively: search → filters → sort, return paginated results)

**Frontend Search & Filter UI**:

- [x] T131 [US6] Create task filters component in phase-2/frontend/components/tasks/task-filters.tsx (client component, search input, status dropdown, priority multi-select, category dropdown, tags multi-select, date range pickers, sort dropdown, clear filters button)
- [x] T132 [US6] Implement URL query parameter sync in phase-2/frontend/app/(dashboard)/tasks/page.tsx (update URL with ?search=...&status=...&priority=...&sort_by=...&order=... on filter changes, parse URL params on page load to restore filter state)
- [x] T133 [US6] Update task list page to apply filters in phase-2/frontend/app/(dashboard)/tasks/page.tsx (pass filter state to TanStack Query, call GET /api/{user_id}/tasks with query params, display filtered results)
- [x] T134 [US6] Implement empty state for no results in phase-2/frontend/components/tasks/task-list.tsx (display "No tasks found matching your filters. Try different filters or clear all." with "Clear Filters" button)

**Checkpoint**: At this point, users can efficiently find tasks using search, filters, and sorting (even with 100+ tasks)

---

## Phase 9: User Story 7 - Data Persistence & Integrity (Priority: P7) ✅ COMPLETE

**Goal**: Ensure data survives application restarts, reversible migrations, foreign key constraints, cascade deletes, and connection pool management

**Independent Test**: User creates 5 tasks with priorities, categories, and tags → stops backend server → restarts backend server → refreshes frontend → verifies all 5 tasks present with correct data (titles, descriptions, priorities, categories, tags) → deletes category assigned to 3 tasks → verifies tasks updated (category_id=null) → deletes tag assigned to 5 tasks → verifies all TaskTag associations removed

**Mapped Requirements**: FR-071 to FR-078 (Data Persistence)

### Tests for User Story 7 (REQUIRED - TDD NON-NEGOTIABLE) ⚠️

- [x] T135 [P] [US7] Integration test for data persistence across restarts in phase-2/backend/tests/integration/test_data_persistence.py (test create 10 tasks, shutdown db connection, reconnect, verify all 10 tasks present with correct data)
- [x] T136 [P] [US7] Integration test for cascade delete user→tasks in phase-2/backend/tests/integration/test_cascade_deletes.py (test delete user cascades to all user tasks via ON DELETE CASCADE)
- [x] T137 [P] [US7] Integration test for cascade delete tag→task_tag in phase-2/backend/tests/integration/test_cascade_deletes.py (test delete tag removes all TaskTag associations via ON DELETE CASCADE, tasks remain)
- [x] T138 [P] [US7] Integration test for SET NULL on category deletion in phase-2/backend/tests/integration/test_cascade_deletes.py (test delete category sets task.category_id=null for all tasks using category via ON DELETE SET NULL)
- [x] T139 [P] [US7] Integration test for unique constraints in phase-2/backend/tests/integration/test_unique_constraints.py (test duplicate email fails, duplicate tag name (case-insensitive) fails, duplicate TaskTag association fails)
- [x] T140 [P] [US7] Integration test for check constraints in phase-2/backend/tests/integration/test_check_constraints.py (test invalid status rejected, invalid priority rejected, empty title after trim rejected)
- [x] T141 [P] [US7] Integration test for connection pooling in phase-2/backend/tests/integration/test_connection_pooling.py (test 20 concurrent requests use pool connections, 21st request waits or times out per pool config)

### Implementation for User Story 7

**Backend Data Integrity Enhancements**:

- [x] T142 [US7] Configure database connection pool settings in phase-2/backend/src/database.py (set pool_size min=5 max=20, pool_timeout=30s, pool_recycle=3600s)
- [x] T143 [US7] Implement migration rollback testing in phase-2/backend/tests/integration/test_migrations.py (test upgrade→downgrade→upgrade for all migrations, verify schema state after rollback)
- [x] T144 [US7] Add database health check endpoint in phase-2/backend/src/main.py (GET /health: test database connection, return 200 if healthy, 503 if database unreachable)
- [x] T145 [US7] Implement connection retry logic in phase-2/backend/src/database.py (retry connection 3 times with exponential backoff 1s/2s/4s on connection failure, raise error after max retries)

**Frontend Data Integrity Features**:

- [x] T146 [US7] Implement optimistic update rollback in phase-2/frontend/components/tasks/task-actions.tsx (TanStack Query: onMutate sets optimistic update, onError rolls back to previous state, display error toast)
- [x] T147 [US7] Add network error handling to API client in phase-2/frontend/lib/api/client.ts (catch network errors, display user-friendly message "Network error. Check your connection.")

**Checkpoint**: At this point, all data integrity guarantees are enforced (cascade deletes, unique constraints, connection pooling, rollback capability)

---

## Phase 10: Polish & Cross-Cutting Concerns ⏳ PARTIALLY COMPLETE

**Purpose**: Final improvements affecting multiple user stories

- [x] T148 [P] Implement responsive design for mobile (320-767px) in phase-2/frontend/components/** (Tailwind responsive classes: sm/md/lg breakpoints, test on iPhone/Android simulators)
- [x] T149 [P] Implement loading states (spinners, skeleton screens) in phase-2/frontend/components/** (add loading prop to components, display spinner during async operations)
- [x] T150 [P] Implement accessibility features in phase-2/frontend/components/** (ARIA labels, keyboard navigation, focus management, screen reader support, color contrast WCAG 2.1 AA)
- [x] T151 [P] Add relative timestamps to task cards in phase-2/frontend/components/tasks/task-card.tsx (display "2 hours ago", "Yesterday", "Jan 11, 2026" using date-fns or similar)
- [ ] T152 Validate Phase 1 tests still pass in Phase-1/ (run pytest tests/ --cov=src, expect 91 tests green, 80%+ coverage)
- [ ] T153 Run backend unit tests with coverage in phase-2/backend/ (pytest tests/unit/ --cov=src, expect ≥80% coverage)
- [ ] T154 Run backend integration tests with coverage in phase-2/backend/ (pytest tests/integration/ --cov=src, expect ≥70% coverage)
- [ ] T155 [P] Run frontend component tests in phase-2/frontend/ (npm run test, expect ≥70% coverage if tests written)
- [ ] T156 Run Lighthouse performance audit on deployed frontend (expect Performance ≥90, Accessibility ≥90, Best Practices ≥90)
- [ ] T157 [P] Execute Python Backend Architect skill: validate-api-contracts (verify all endpoints match OpenAPI schema via contract testing)
- [ ] T158 [P] Execute Python Backend Architect skill: generate-api-documentation (auto-generate API docs from Pydantic models, verify /docs endpoint serves Swagger UI)
- [ ] T159 [P] Execute Python Backend Architect skill: check-authorization-coverage (verify all protected endpoints use get_current_user dependency, no unprotected endpoints)
- [ ] T160 [P] Execute Next.js Frontend Architect skill: verify-nextjs-16-patterns using Context7 MCP (/vercel/next.js/v16)
- [ ] T161 [P] Execute Better Auth Guardian skill: validate-better-auth-security using Context7 MCP (/better-auth/better-auth)
- [ ] T162 Execute Integration Orchestrator skill: validate-integration-points (verify contracts between frontend↔backend, backend↔database layers)
- [ ] T163 Execute Integration Orchestrator skill: execute-e2e-tests (run E2E tests for signup→signin→create task→filter→signout flow)
- [ ] T164 Execute Integration Orchestrator skill: validate-error-propagation (validate error handling across all layers: frontend→backend→database)
- [ ] T165 Execute Integration Orchestrator skill: validate-test-coverage (ensure 80% unit, 70% integration coverage met)
- [ ] T166 [P] Deploy backend to Railway/Render (configure environment variables, run migrations, health check endpoint)
- [ ] T167 [P] Deploy frontend to Vercel (configure environment variables, test API connection to deployed backend)
- [ ] T168 Execute smoke tests on deployed application (register user → signin → create task → search → filter → delete → signout, verify all flows work in production)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5 → P6 → P7)
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 (authentication required to access tasks) - Can start after US1 complete
- **User Story 3 (P3)**: Depends on US1 + US2 (validates security of auth + tasks) - Can start after US2 complete
- **User Story 4 (P4)**: Depends on US1 + US2 (documents auth + task endpoints) - Can start after US2 complete
- **User Story 5 (P5)**: Depends on US2 (extends task management with organization) - Can start after US2 complete
- **User Story 6 (P6)**: Depends on US2 + US5 (search/filter requires tasks + organization features) - Can start after US5 complete
- **User Story 7 (P7)**: Depends on US2 + US5 (validates persistence of tasks + categories + tags) - Can start in parallel with US3-US6

### Critical Blocking Points

1. **T016** (Execute migrations): Blocks all backend implementation
2. **T023-T024** (JWT validation dependencies): Blocks all protected endpoints
3. **T039-T045** (Auth endpoints): Blocks all user stories requiring authentication
4. **T064** (GET tasks endpoint): Blocks frontend task list implementation

### Parallel Opportunities

- **Phase 1 (Setup)**: All tasks T001-T008 can run in parallel (different files, no dependencies)
- **Phase 2 (Foundational)**: Migrations T010-T013 can run in parallel, Models T017-T021 can run in parallel after migrations
- **Within Each User Story**: All test tasks marked [P] can run in parallel, all model/component tasks marked [P] can run in parallel
- **User Stories**: After foundational phase, different user stories can be worked on in parallel by different team members (though dependencies listed above apply)

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
Task T058: Unit test for Task model validation
Task T059: Integration test for task creation
Task T060: Integration test for task list
Task T061: Integration test for task update
Task T062: Integration test for task completion
Task T063: Integration test for task deletion

# Launch all frontend components for User Story 2 together:
Task T072: Create task list component
Task T073: Create task card component
Task T074: Create task form component
Task T075: Create task detail modal component
Task T076: Create task actions component
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T033) - CRITICAL
3. Complete Phase 3: User Story 1 (T034-T057) - Authentication
4. Complete Phase 4: User Story 2 (T058-T077) - Core Task Management
5. **STOP and VALIDATE**: Test US1 + US2 independently
6. Deploy/demo if ready (MVP = authenticated task management)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Auth working)
3. Add User Story 2 → Test independently → Deploy/Demo (MVP: Task CRUD)
4. Add User Story 3 → Test independently → Deploy/Demo (Security hardened)
5. Add User Story 4 → Test independently → Deploy/Demo (API documented)
6. Add User Story 5 → Test independently → Deploy/Demo (Organization features)
7. Add User Story 6 → Test independently → Deploy/Demo (Search/filter)
8. Add User Story 7 → Test independently → Deploy/Demo (Full data integrity)
9. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T033)
2. Once Foundational is done:
   - Developer A: User Story 1 (T034-T057)
   - Developer B: User Story 2 (T058-T077) - starts after US1 auth endpoints ready
   - Developer C: User Story 5 (T099-T117) - starts after US2 task endpoints ready
3. Stories complete and integrate independently

---

## Summary

**Total Tasks**: 168 tasks
**Completed**: 77/168 (MVP Complete)

**Task Distribution**:
- Phase 1 (Setup): 8 tasks ✅ COMPLETE
- Phase 2 (Foundational): 25 tasks ✅ COMPLETE
- Phase 3 (US1 - Authentication): 24 tasks ✅ COMPLETE
- Phase 4 (US2 - Core Task Management): 20 tasks ✅ COMPLETE
- Phase 5 (US3 - User Isolation & Security): 13 tasks
- Phase 6 (US4 - API Contracts & Documentation): 8 tasks
- Phase 7 (US5 - Task Organization): 19 tasks
- Phase 8 (US6 - Task Discovery): 17 tasks
- Phase 9 (US7 - Data Persistence & Integrity): 13 tasks
- Phase 10 (Polish & Cross-Cutting): 21 tasks

**Parallelization**: 76 tasks marked [P] can run in parallel within their phase

**Test Coverage**: 37 test tasks (22% of total) ensuring TDD compliance
- Unit tests: 4 tasks
- Integration tests: 31 tasks
- Performance tests: 1 task
- E2E tests: 1 task

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (US1) + Phase 4 (US2) = 77 tasks ✅ COMPLETE (authenticated task CRUD)

**Functional Requirements Coverage**: All 100 FRs (FR-001 to FR-100) mapped to tasks

**User Stories Coverage**: All 7 user stories (US1-US7) have dedicated phases with independent test criteria

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD mandate)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Phase 1 tests MUST remain green after every Phase 2 task (91 tests in Phase-1/)
- Use Context7 MCP for Better Auth Guardian (/better-auth/better-auth) and Next.js Frontend Architect (/vercel/next.js/v16)
