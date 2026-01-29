---
id: 0001
title: Phase II Full-Stack Architecture Plan
stage: plan
date: 2026-01-11
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-fullstack-todo-web
branch: 001-fullstack-todo-web
user: USER-PC
command: planning
labels: ["architecture", "phase-2", "full-stack", "nextjs-16", "fastapi", "better-auth"]
links:
  spec: specs/001-fullstack-todo-web/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-fullstack-todo-web/plan.md
tests:
  - N/A (planning phase)
---

## Prompt

User requested creation of a comprehensive technical implementation plan for Phase II: Full-Stack Todo Web Application.

**Original Request**: "You are a Senior Agentic System Planner and Software Architect. Produce a high-level technical plan covering the core system design areas listed below. This is a planning exercise only — no code, no task breakdown, no implementation."

**Planning Scope Required**:
1. Technology stack selection rationale (Next.js 16, FastAPI, SQLModel, Neon PostgreSQL, Better Auth)
2. Database schema design (5 core tables + 1 join table)
3. API endpoint implementation plan (15+ REST endpoints)
4. Frontend component architecture (App Router structure, server vs client components)
5. Authentication flow implementation (Better Auth JWT configuration)
6. Test strategy definition (unit, integration, E2E)

**Context**: Transform Phase I in-memory Python console app into production-grade, multi-user web application with persistent storage and secure authentication, while preserving all 10 Phase I Task domain invariants.

## Response snapshot

Created comprehensive 43KB technical architecture plan covering:

**1. Technology Stack Rationale**:
- Next.js 16 App Router (server components, zero-JS bundle optimization)
- FastAPI (async-first, auto OpenAPI docs, Pydantic validation)
- SQLModel + Neon Serverless PostgreSQL (type-safe ORM, auto-scaling)
- Better Auth + JWT (framework-agnostic, secure by default)
- Context7 MCP integration requirements for Next.js and Better Auth agents

**2. Database Schema Design**:
- 5 core tables: users, tasks (extended from Phase I), categories, tags, task_tag
- Row-Level Security (RLS) for defense-in-depth user isolation
- Full-text search indexes (GIN), composite indexes for filtering/sorting
- CASCADE DELETE and SET NULL constraints for referential integrity
- 8 predefined system categories seeded on deployment

**3. API Endpoint Implementation**:
- 6 authentication endpoints (signup, verify-email, signin, refresh, signout, reset-password)
- 6 task endpoints (list with search/filter/sort, create, get, update, delete, toggle complete)
- 3 category endpoints (list, create, delete)
- 4 tag endpoints (list, create, rename, delete)
- Consistent error response format across all endpoints
- JWT validation and URL parameter user_id enforcement

**4. Frontend Architecture**:
- Next.js 16 App Router directory structure (phase-2/frontend/)
- Server components (default) vs client components strategy
- TanStack Query for state management with optimistic updates
- API client with JWT injection and automatic token refresh
- proxy.ts (NOT middleware.ts) for Next.js 16 authentication routing

**5. Authentication Flow**:
- Backend JWT validation dependency (dependencies.py)
- Access tokens (1-hour) + refresh tokens (7-day) lifecycle
- bcrypt password hashing (10+ rounds)
- Rate limiting (100 req/min), account lockout (5 failed attempts)
- CSRF protection (SameSite cookies, Better Auth tokens)

**6. Test Strategy**:
- Unit tests: 80% coverage (domain, application, infrastructure layers)
- Integration tests: 70% coverage (API endpoints, multi-user isolation, auth)
- E2E tests: Critical flows (registration, CRUD, search/filter, token refresh)
- Multi-user isolation scenarios, JWT expiration handling, cascade delete verification

**Critical Files Identified**:
1. phase-2/backend/src/api/dependencies.py (JWT validation)
2. phase-2/backend/src/models/task.py (SQLModel schema)
3. phase-2/backend/src/api/routes/tasks.py (complex query logic)
4. phase-2/frontend/lib/api/client.ts (centralized API client)
5. phase-2/frontend/components/tasks/task-form.tsx (primary interaction component)
6. phase-2/frontend/proxy.ts (Next.js 16 auth routing)

**Project Structure**:
```
todo-app/
├── Phase-1/ (unchanged)
└── phase-2/
    ├── backend/ (FastAPI + SQLModel + Neon)
    └── frontend/ (Next.js 16 App Router + Better Auth)
```

**Performance Targets Defined**:
- API reads: p95 < 500ms (1000+ tasks)
- Search: p95 < 2s (GIN index)
- Filter/Sort: p95 < 1s / 500ms
- 50+ concurrent users supported
- Lighthouse score ≥ 90

**Verification Strategy**: End-to-end testing flows for registration, task CRUD, multi-user isolation, search/filter, and token refresh.

## Outcome

- ✅ Impact: Comprehensive Phase II technical architecture plan created (43KB), covering all 6 required design areas with detailed rationale and implementation guidance
- 🧪 Tests: Test strategy defined (unit 80%, integration 70%, E2E critical flows) - tests to be written during implementation
- 📁 Files: 1 file created - specs/001-fullstack-todo-web/plan.md
- 🔁 Next prompts: Task decomposition using /sp.tasks to generate atomic, testable tasks in tasks.md
- 🧠 Reflection: Successfully preserved Phase I foundation (10 Task invariants unchanged) while designing scalable, secure, production-ready web architecture. Context7 MCP integration required for Next.js 16 and Better Auth agents to ensure latest best practices.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning phase completed successfully
- Graders run and results (PASS/FAIL): N/A (planning phase, no automated grading)
- Prompt variant (if applicable): Standard planning workflow
- Next experiment (smallest change to try): Proceed with /sp.tasks for task decomposition and atomic task generation
