---
id: 0003
title: Phase III Implementation Plan
stage: plan
date: 2026-01-31
surface: agent
model: claude-opus-4-5-20251101
feature: ai-chatbot
branch: 002-ai-chatbot
user: USER-PC
command: /sp.plan
labels: ["phase-iii", "ai-chatbot", "implementation-plan", "mcp", "openai-agents"]
links:
  spec: specs/002-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-ai-chatbot/plan.md
  - specs/002-ai-chatbot/research.md
  - specs/002-ai-chatbot/data-model.md
  - specs/002-ai-chatbot/quickstart.md
  - specs/002-ai-chatbot/contracts/chat-api.md
  - history/prompts/ai-chatbot/0003-phase-iii-implementation-plan.plan.prompt.md
tests:
  - null
---

## Prompt

/sp.plan — Create Phase III implementation plan based on approved specification at specs/002-ai-chatbot/spec.md. Phase III: Todo AI Chatbot - AI-powered conversational Todo system with stateless MCP architecture, OpenAI Agents SDK, OpenRouter API, and advanced features including recurring tasks and due date reminders. Must cover 10 sections: Architecture Overview, Agent Architecture & Skill Composition, MCP Server Plan, Backend Plan, Database Strategy, Frontend Plan, Advanced Features Plan, Testing Strategy, NFRs, and Risk Mitigation. Output to specs/002-ai-chatbot/plan.md. No tasks, no code.

## Response snapshot

Created complete Phase III implementation plan with 6 artifacts:

1. **research.md** (Phase 0): Technology research findings for 7 key decisions — OpenAI Agents SDK + OpenRouter integration pattern, standalone FastMCP server over Streamable HTTP, database-backed 7-message context window, ChatKit frontend with custom backend, APScheduler for background jobs, pywebpush for notifications, extended rate limiter for chat.

2. **data-model.md** (Phase 1): 5 new database tables (Conversation, Message, RecurrenceRule, ReminderMetadata, PushSubscription) + 1 column extension (tasks.due_date). Complete SQLModel definitions, constraints, indexes, and 6 Alembic migrations (009-014). Query patterns for context window, conversation listing, due recurrences, pending reminders, and overdue tasks.

3. **contracts/chat-api.md** (Phase 1): 6 REST API endpoints (chat, conversation list, messages, delete conversation, push subscribe, push unsubscribe) + 9 MCP tool contracts (create_task, list_tasks, update_task, complete_task, delete_task, create_recurrence, update_recurrence, remove_recurrence, set_due_date). Full request/response schemas with error codes.

4. **plan.md** (main deliverable): 10-section implementation plan covering architecture overview, agent architecture, MCP server plan, backend plan, database strategy, frontend (ChatKit) plan, advanced features plan, testing strategy, NFRs, and risk mitigation. Key decisions: standalone MCP server, OpenRouter via set_default_openai_client(), phase-3/ directory structure extending phase-2/, APScheduler in-process, ChatKit with custom backend proxy.

5. **quickstart.md** (Phase 1): Developer setup guide with env vars, dependencies, migration steps, start order (4 processes), test commands, and architecture quick reference.

6. **PHR** (this file): Plan stage prompt history record.

User clarification during planning:
- Architecture: Standalone MCP Server (user-selected over function tools and in-process options)
- Directory structure: phase-3/ extending phase-2/ (separate directory importing shared code)

## Outcome

- Impact: Complete implementation plan with 6 artifacts covering architecture, data model, API contracts, research, quickstart, and plan. All 60+ FRs traceable to implementation components.
- Tests: null (planning phase, no code)
- Files: 6 files created (plan.md, research.md, data-model.md, contracts/chat-api.md, quickstart.md, PHR)
- Next prompts: /sp.tasks (create dependency-ordered task breakdown)
- Reflection: Plan uses phase-3/ directory structure per user preference. Standalone MCP server adds complexity but provides full protocol compliance. All technology decisions documented with rationale and alternatives in research.md.

## Evaluation notes (flywheel)

- Failure modes observed: setup-plan.sh and update-agent-context.sh produced no output (Windows/bash compatibility, non-blocking)
- Graders run and results (PASS/FAIL): Constitution Check 8/8 PASS, all 10 plan sections completed
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
