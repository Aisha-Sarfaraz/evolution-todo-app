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

### Agent Categories

Agents are classified into four categories with distinct authorities:

**Governance Agents (Blocking Authority):**
- **Spec Governance Enforcer:** Blocks if no approved specification exists
- **Test Strategy Architect:** Blocks if TDD cycle not followed or coverage insufficient

**Domain Agents (Blocking Authority):**
- **Domain Guardian (Generic):** Blocks if domain boundaries violated (domain-agnostic, configurable)
- **Core Todo Domain:** Blocks if Task domain invariants broken (Todo-specific enforcement)

**Design/Guidance Agents (Advisory):**
- **Error & Reliability Architect:** Advises on error handling, resilience patterns (no blocking authority)
- **Better Auth Guardian:** Blocks if security requirements not met (authentication/authorization only)

**Operational Agents (Variable Authority):**
- **Python Backend Architect:** Implements application services (can be blocked by governance/domain agents)
- **Next.js Frontend Architect:** Implements UI components (can be blocked by governance agents)
- **Data & Schema Guardian:** Blocks if schema conflicts with domain model or migration lacks rollback
- **Integration Orchestrator:** Blocks if integration tests fail or cross-layer contracts violated

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
- **Data & Schema Guardian:** 4 skills
  - generate-migration (Alembic migrations from domain changes)
  - execute-migration-rollback (safe rollback with data preservation)
  - validate-schema-alignment (verify schema aligns with domain model)
  - verify-data-integrity (validate data consistency after migrations)

- **Integration Orchestrator:** 4 skills
  - coordinate-agent-sequence (execute multi-agent workflows in correct order)
  - validate-integration-points (verify contracts between system layers)
  - execute-e2e-tests (run integration and E2E tests)
  - aggregate-workflow-results (collect and summarize workflow results)

- **All Other Agents:** 0 skills (reasoning/coordination only, no operational workflows)

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

**Version:** 1.0.0 | **Ratified:** 2025-01-02 | **Last Amended:** 2025-01-02
