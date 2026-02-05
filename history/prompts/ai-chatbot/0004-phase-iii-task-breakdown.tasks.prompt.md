---
id: 0004
title: Phase III Task Breakdown
stage: tasks
date: 2026-01-31
surface: agent
model: claude-opus-4-5-20251101
feature: ai-chatbot
branch: 002-ai-chatbot
user: USER-PC
command: /sp.tasks
labels: ["phase-iii", "ai-chatbot", "tasks", "tdd", "task-breakdown"]
links:
  spec: specs/002-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-ai-chatbot/tasks.md
  - history/prompts/ai-chatbot/0004-phase-iii-task-breakdown.tasks.prompt.md
tests:
  - null
---

## Prompt

/sp.tasks — Generate an actionable, dependency-ordered tasks.md for Phase III AI Chatbot based on approved design artifacts (spec.md, plan.md, research.md, data-model.md, contracts/chat-api.md, quickstart.md). Tasks organized by user story (P1-P5), following TDD mandate with tests before implementation. Include parallel execution opportunities and MVP scope.

## Response snapshot

Generated comprehensive tasks.md with 108 tasks organized across 8 phases:

**Phase 1: Setup** (8 tasks) — Project initialization, directory structure, dependency management for phase-3/backend and phase-3/frontend, test configuration (Vitest, Playwright, pytest).

**Phase 2: Foundational** (13 tasks) — Phase II import strategy, MCP database sessions, Agent+OpenRouter config, system prompt, Alembic migrations 009-010 (conversations, messages), SQLModels, FastAPI app entry point.

**Phase 3: US1 NL Task CRUD** (24 tasks, MVP) — 8 test tasks + 16 implementation tasks. MCP task tools (create/list/update/complete/delete), FastMCP server, chat service, chat API route, rate limiting, ChatKit integration, ChatContainer and ToolCallDisplay frontend components.

**Phase 4: US2 Conversation Persistence** (13 tasks) — 5 test + 8 impl. Conversation list/messages/delete routes, ConversationList sidebar, conversation switching, lazy loading.

**Phase 5: US3 Recurring Tasks** (12 tasks) — 4 test + 8 impl. Migration 011, RecurrenceRule model, recurrence calculation, MCP tools, APScheduler job, NL patterns.

**Phase 6: US4 Due Dates & Reminders** (22 tasks) — 6 test + 16 impl. Migrations 012-014, ReminderMetadata/PushSubscription models, set_due_date tool, reminder service, push routes, Service Worker, notification banner.

**Phase 7: US5 Advanced NL** (6 tasks) — 3 test + 3 impl. System prompt enhancements for batch/compound/contextual operations.

**Phase 8: Polish** (10 tasks) — Logging, token tracking, E2E tests, catch-up logic, health check, code quality validation.

Key metrics:
- 108 total tasks, 60+ parallelizable
- MVP scope: 45 tasks (Phase 1+2+3)
- 5 user stories independently testable
- Cross-story parallelism: US3 || US4 after foundational phase

## Outcome

- Impact: Complete dependency-ordered task breakdown with 108 tasks across 8 phases, TDD-compliant, organized by user story for independent delivery
- Tests: null (task generation, no code)
- Files: 2 files created (tasks.md, PHR)
- Next prompts: /sp.implement (begin TDD implementation starting with Phase 1 Setup)
- Reflection: Tasks follow strict checklist format with IDs, [P] markers, [US] labels, and file paths. MVP scope (45 tasks for US1) is achievable. US3 and US4 can run in parallel for team efficiency.

## Evaluation notes (flywheel)

- Failure modes observed: check-prerequisites.sh produced no output (Windows/bash compatibility, non-blocking)
- Graders run and results (PASS/FAIL): Format validation PASS — all 108 tasks follow checklist format with checkbox, ID, labels, file paths
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
