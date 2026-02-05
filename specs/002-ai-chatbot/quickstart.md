# Quickstart Guide — Phase III: AI-Powered Conversational Todo

**Feature Branch**: `002-ai-chatbot`
**Prerequisites**: Phase II backend and frontend operational

---

## Environment Variables

Create `.env` files for Phase III:

### Backend (`phase-3/backend/.env`)

```bash
# Phase II shared (copy from phase-2/backend/.env)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
BETTER_AUTH_SECRET=your-better-auth-secret
BETTER_AUTH_URL=http://localhost:3000

# Phase III specific
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-api-key
OPENROUTER_MODEL=openai/gpt-4o-mini
MCP_PORT=8001
MCP_URL=http://localhost:8001/mcp

# Push notifications (generate with: python -c "from py_vapid import Vapid; v=Vapid(); v.generate_keys(); print(v.private_pem(), v.public_key)")
VAPID_PRIVATE_KEY=your-vapid-private-key
VAPID_PUBLIC_KEY=your-vapid-public-key
VAPID_MAILTO=mailto:admin@example.com
```

### Frontend (`phase-3/frontend/.env.local`)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_VAPID_PUBLIC_KEY=your-vapid-public-key
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

---

## Installation

### 1. Backend Dependencies

```bash
cd phase-3/backend
uv sync  # or: pip install -r requirements.txt
```

**Key new dependencies** (beyond Phase II):
- `openai-agents` — OpenAI Agents SDK
- `mcp` — Official MCP SDK (includes FastMCP)
- `apscheduler` — Background job scheduler
- `pywebpush` — Web Push notification library
- `py-vapid` — VAPID key generation

### 2. Frontend Dependencies

```bash
cd phase-3/frontend
npm install
```

**Key new dependencies** (beyond Phase II):
- `@openai/chatkit` — Chat UI components

### 3. Database Migrations

Run from Phase II backend (migrations are shared):

```bash
cd phase-2/backend
alembic upgrade head
```

This applies migrations 009–014:
- 009: `conversations` table
- 010: `messages` table
- 011: `recurrence_rules` table
- 012: `reminder_metadata` table
- 013: `push_subscriptions` table
- 014: `due_date` column on `tasks`

---

## Running the Application

### Start Order

1. **Phase II Backend** (if not already running — provides database and auth):
   ```bash
   cd phase-2/backend
   uvicorn src.main:app --reload --port 8000
   ```

2. **MCP Server** (standalone process):
   ```bash
   cd phase-3/backend
   python -m src.mcp.server
   ```
   Runs on port 8001 by default.

3. **Phase III Backend** (chat API):
   ```bash
   cd phase-3/backend
   uvicorn src.main:app --reload --port 8002
   ```

4. **Phase III Frontend**:
   ```bash
   cd phase-3/frontend
   npm run dev
   ```
   Runs on port 3001 by default.

### Verify Health

```bash
# Phase II backend
curl http://localhost:8000/health

# MCP server (Streamable HTTP)
curl http://localhost:8001/mcp

# Phase III backend (enhanced: returns component status)
curl http://localhost:8002/health

# Frontend
open http://localhost:3001
```

---

## Development Workflow

### Running Tests

**Backend (pytest)**:
```bash
cd phase-3/backend

# All tests
pytest tests/

# Unit tests only
pytest tests/unit/ -m unit

# Integration tests
pytest tests/integration/ -m integration

# With coverage
pytest tests/ --cov=src --cov-report=term
```

**Frontend (Vitest + Playwright)**:
```bash
cd phase-3/frontend

# Unit tests (Vitest)
npm run test

# Unit tests with coverage
npm run test:coverage

# E2E tests (Playwright)
npm run test:e2e

# E2E tests UI mode
npx playwright test --ui
```

### Code Quality

```bash
# Backend
cd phase-3/backend
ruff check src/
black src/
mypy src/

# Frontend
cd phase-3/frontend
npm run lint
npm run type-check
```

---

## Logging

Phase III uses structured JSON logging by default. Configure via env vars:

```bash
LOG_LEVEL=INFO       # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json      # json or text
```

Logs include `user_id`, `conversation_id`, `duration_ms`, and `tokens_used` fields for observability.

---

## Architecture Quick Reference

| Component | Port | Technology |
|-----------|------|-----------|
| Phase II Backend | 8000 | FastAPI (auth, task CRUD) |
| MCP Server | 8001 | FastMCP (Streamable HTTP) |
| Phase III Backend | 8002 | FastAPI (chat, conversations, push) |
| Phase III Frontend | 3001 | Next.js 16 + ChatKit |
| Database | 5432 | Neon PostgreSQL |
| OpenRouter | — | External API |
