# Tasks: Local Kubernetes Deployment

**Input**: Design documents from `/specs/003-kubernetes-deployment/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/
**Branch**: `003-kubernetes-deployment`

**Tests**: Infrastructure testing via `helm lint`, `helm template`, `docker build`, health check endpoint verification, and `kubectl` validation. TDD for infrastructure means "validate before deploy" — lint before install, template before apply, health check contract before probe configuration.

**Organization**: Tasks are grouped by user story (P1-P6) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Infrastructure code**: `phase-4/` (Dockerfiles, Helm charts, scripts)
- **Phase III backend**: `phase-3/backend/` (health endpoint changes only)
- **Phase III frontend**: `phase-3/frontend/` (next.config.ts + health route only)
- **Helm chart**: `phase-4/helm/todo-app/`
- **Docker**: `phase-4/docker/`
- **Scripts**: `phase-4/scripts/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the phase-4/ directory structure and foundational files

- [x] T001 Create phase-4/ directory structure with docker/, helm/todo-app/templates/, and scripts/ subdirectories per plan.md project structure
- [x] T002 [P] Create phase-4/docker/backend.dockerignore excluding .git, node_modules, .env, __pycache__, tests/, .pytest_cache, .mypy_cache, *.pyc
- [x] T003 [P] Create phase-4/docker/frontend.dockerignore excluding .git, node_modules, .env, .next, out/, coverage/, *.test.*, .eslintcache
- [x] T004 [P] Create phase-4/helm/todo-app/.helmignore excluding .git, .gitignore, .DS_Store, *.swp, *.tmp

**Checkpoint**: Directory structure exists. All ignore files in place.

---

## Phase 2: Foundational (Blocking Prerequisites — Health Endpoints)

**Purpose**: Add health check endpoints to Phase III application code. These MUST exist before Docker images can be built with proper HEALTHCHECK instructions, and before Kubernetes probes can be configured.

**CRITICAL**: No Docker or Helm work can begin until health endpoints are functional.

### Validation for Phase 2

- [x] T005 [P] Validate backend health check contract: `/health/live` returns 200 with `{"status": "alive"}`, `/health/ready` returns 200/503 based on DB connectivity, `/health` legacy endpoint still works — per contracts/health-check-contract.md
- [x] T006 [P] Validate frontend health check contract: `/api/health` returns 200 with `{"status": "ok"}` — per contracts/health-check-contract.md

### Implementation for Phase 2

- [x] T007 Add `/health/live` liveness endpoint to phase-3/backend/src/main.py — returns `{"status": "alive", "service": "todo-chatbot-api", "version": "3.0.0"}` with HTTP 200 (no DB check) per R3 decision
- [x] T008 Add `/health/ready` readiness endpoint to phase-3/backend/src/main.py — executes `SELECT 1` against database, returns `{"status": "ready", "database": "connected"}` (200) or `{"status": "not_ready", "database": "disconnected"}` (503) per R3 decision
- [x] T009 [P] Add `output: "standalone"` to phase-3/frontend/next.config.ts for Next.js standalone build mode per R2 decision
- [x] T010 [P] Create frontend health route at phase-3/frontend/app/api/health/route.ts — returns `{"status": "ok", "service": "todo-frontend", "timestamp": "<ISO>"}` with HTTP 200

**Checkpoint**: All 4 health endpoints respond correctly. `next.config.ts` has `output: "standalone"`. Phase III code changes complete — no further modifications to Phase III.

---

## Phase 3: User Story 1 — Docker Containerization (Priority: P1) MVP

**Goal**: Build production-ready Docker images for both services with multi-stage builds, non-root user, health checks, and layer caching.

**Independent Test**: Run `docker build` for both services, then `docker run` each container independently. Verify health check endpoints respond and application serves traffic on expected ports.

**Depends on**: Phase 2 (health endpoints must exist)

### Validation for User Story 1

- [x] T011 [US1] Validate backend Docker image builds successfully, is under 500MB, runs as non-root (UID 1000), and `/health` endpoint returns 200 via `docker run`
- [x] T012 [US1] Validate frontend Docker image builds successfully, is under 300MB, runs as non-root (UID 1000), and `/api/health` endpoint returns 200 via `docker run`

### Implementation for User Story 1

- [x] T013 [P] [US1] Create phase-4/docker/backend.Dockerfile — multi-stage build (builder + production) using python:3.11-slim base, install deps from requirements.txt in builder stage, copy site-packages to production stage, create non-root user UID 1000, set PYTHONUNBUFFERED=1 and PYTHONDONTWRITEBYTECODE=1, copy src/ + migrations/ + alembic.ini, HEALTHCHECK on /health, EXPOSE 7860 — per R1 decision
- [x] T014 [P] [US1] Create phase-4/docker/frontend.Dockerfile — 3-stage build (deps + builder + runner) using node:20-alpine base, npm ci in deps stage, set NEXT_PUBLIC_* build args and npm run build in builder stage, copy .next/standalone + .next/static + public/ to runner stage, create non-root user UID 1000, EXPOSE 3000, CMD ["node", "server.js"] — per R2 decision
- [x] T015 [US1] Create phase-4/scripts/build.sh — builds both Docker images with configurable tags (default: latest), supports --backend-only and --frontend-only flags, prints image sizes after build

**Checkpoint**: Both images build. `docker run -p 7860:7860 todo-backend:latest` serves `/health`. `docker run -p 3000:3000 todo-frontend:latest` serves `/api/health`. Images under size limits. User Story 1 is independently functional.

---

## Phase 4: User Story 2 — Minikube Deployment (Priority: P2)

**Goal**: Deploy both containerized services to Minikube via Helm chart with ConfigMaps, Secrets, namespace isolation, and resource limits.

**Independent Test**: Start Minikube, load images, run `helm install`, all pods reach Running state, services accessible via `minikube tunnel`, full chat conversation works end-to-end.

**Depends on**: Phase 3/US1 (working Docker images required)

**Note**: US2 (Minikube Deployment) and US3 (Helm Chart Packaging) are implemented together since the deployment mechanism IS the Helm chart. Tasks are labeled [US2] for manifest content and [US3] for Helm-specific packaging.

### Validation for User Story 2

- [x] T016 [US2] Validate `helm lint phase-4/helm/todo-app/` passes with zero errors and zero warnings (FR-055, SC-007)
- [x] T017 [US2] Validate `helm template todo-app phase-4/helm/todo-app/` renders all manifests without errors and all resource names use `{{ include "todo-app.fullname" . }}` pattern (FR-045)

### Implementation for User Story 2

- [x] T018 [US2] Create phase-4/helm/todo-app/Chart.yaml — name: todo-app, version: 0.1.0, appVersion: 3.0.0, apiVersion: v2, description, type: application — per FR-037, FR-054
- [x] T019 [US2] Create phase-4/helm/todo-app/values.yaml — all configurable parameters organized into global, backend, frontend, database, config, secrets sections with inline comments documenting each value — per helm-values-contract.md, FR-038, FR-039
- [x] T020 [US2] Create phase-4/helm/todo-app/templates/_helpers.tpl — define template functions: todo-app.name, todo-app.fullname, todo-app.chart, todo-app.labels (app.kubernetes.io/name, instance, version, managed-by), todo-app.selectorLabels — per FR-050
- [x] T021 [P] [US2] Create phase-4/helm/todo-app/templates/namespace.yaml — creates todo-app namespace with labels — per FR-029, FR-030
- [x] T022 [P] [US2] Create phase-4/helm/todo-app/templates/configmap.yaml — non-sensitive config (LOG_LEVEL, LOG_FORMAT, ALLOWED_ORIGINS, ENVIRONMENT) from values.config — per FR-022, R6 decision
- [x] T023 [P] [US2] Create phase-4/helm/todo-app/templates/secret.yaml — sensitive credentials (DATABASE_URL, OPENROUTER_API_KEY, BETTER_AUTH_SECRET, VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY) with base64 encoding from values.secrets — per FR-023, FR-052, R6 decision
- [x] T024 [US2] Create phase-4/helm/todo-app/templates/backend-deployment.yaml — Deployment with configurable replicas, image from values, resource requests/limits (250m/256Mi to 500m/512Mi), rolling update strategy (maxUnavailable=0, maxSurge=1), liveness/readiness/startup probes from values, env vars from ConfigMap + Secret, terminationGracePeriodSeconds=10, pod labels (app, component, version) — per FR-016, FR-018, FR-019, FR-024, FR-025, FR-026, FR-027, FR-032, FR-033, FR-034
- [x] T025 [P] [US2] Create phase-4/helm/todo-app/templates/backend-service.yaml — ClusterIP service on port 7860 with selector matching backend Deployment labels — per FR-021
- [x] T026 [US2] Create phase-4/helm/todo-app/templates/frontend-deployment.yaml — Deployment with configurable replicas, image from values, resource requests/limits (100m/128Mi to 250m/256Mi), rolling update strategy, liveness probe for /api/health, env vars from ConfigMap, terminationGracePeriodSeconds=10, pod labels — per FR-017, FR-018, FR-019, FR-028, FR-032, FR-033, FR-034
- [x] T027 [P] [US2] Create phase-4/helm/todo-app/templates/frontend-service.yaml — LoadBalancer service on port 3000 with selector matching frontend Deployment labels — per FR-020
- [x] T028 [US2] Create phase-4/helm/todo-app/templates/migration-job.yaml — Helm pre-install/pre-upgrade hook Job running `alembic upgrade head` using backend image, DATABASE_URL from Secret, restartPolicy: Never, backoffLimit: 3, hook-delete-policy: hook-succeeded — per FR-061, FR-062, R8 decision
- [x] T029 [US2] Create phase-4/helm/todo-app/templates/NOTES.txt — post-install instructions showing how to access the application, check pod status, view logs, and tear down — per FR-049

**Checkpoint**: `helm lint` passes. `helm template` renders all 9 manifests. All resources use `todo-app` namespace. ConfigMap and Secret contain correct keys. Deployments reference correct probe paths. Services have correct types (ClusterIP/LoadBalancer).

---

## Phase 5: User Story 3 — Helm Chart Packaging (Priority: P3)

**Goal**: Parameterized Helm chart with environment overrides, versioning, and single-command deployment.

**Independent Test**: `helm install todo-app phase-4/helm/todo-app/ --set secrets.databaseUrl=... ` deploys the full stack on a clean Minikube cluster. `helm upgrade` with changed replicas scales the deployment.

**Depends on**: Phase 4/US2 (Helm templates must exist)

### Implementation for User Story 3

- [x] T030 [P] [US3] Create phase-4/helm/todo-app/values-dev.yaml — development overrides (reduced resource limits, debug log level, 1 replica) — per FR-043
- [x] T031 [US3] Validate Helm chart supports full lifecycle: `helm install` creates all resources, `helm upgrade --set backend.replicaCount=2` scales backend, `helm upgrade --atomic` auto-rolls-back on failure — per FR-046, FR-047, FR-048
- [x] T032 [US3] Create phase-4/scripts/deploy.sh — deploys to Minikube via helm install/upgrade with --atomic flag, accepts secret values as arguments or from env vars, validates pods reach Running state — per plan.md Phase C step 19
- [x] T033 [US3] Create phase-4/scripts/teardown.sh — runs `helm uninstall todo-app`, optionally deletes namespace, prints confirmation — per plan.md Phase D step 26

**Checkpoint**: `helm install` deploys full stack. `helm upgrade` applies changes. `values-dev.yaml` overrides work. Deploy/teardown scripts function correctly.

---

## Phase 6: User Story 4 — Health Checks and Probes (Priority: P4)

**Goal**: Kubernetes probes correctly manage pod lifecycle — liveness detects crashes, readiness gates traffic, startup handles slow initialization.

**Independent Test**: Kill backend database connection — readiness probe fails, K8s stops routing traffic. Restore connection — readiness passes, traffic resumes. Restart pod — startup probe allows 30s initialization window.

**Depends on**: Phase 4/US2 (Deployments with probes must be deployed to cluster)

### Validation for User Story 4

- [x] T034 [US4] Validate liveness probe: backend pod running → `kubectl exec` curl `/health/live` returns 200 within 2s timeout — per health-check-contract.md
- [x] T035 [US4] Validate readiness probe: backend pod running with DB connected → `kubectl exec` curl `/health/ready` returns 200; simulate DB failure → returns 503, pod removed from service endpoints within 15 seconds — per SC-009
- [x] T036 [US4] Validate startup probe: fresh pod startup → startup probe allows 30s window (failureThreshold=6 * periodSeconds=5) before declaring failure — per FR-027

### Implementation for User Story 4

- [x] T037 [US4] Verify Kubernetes probe configurations in deployed cluster match health-check-contract.md values: liveness (path=/health/live, interval=10s, timeout=2s, failureThreshold=3), readiness (path=/health/ready, interval=5s, timeout=5s, failureThreshold=3), startup (path=/health/live, period=5s, failureThreshold=6) — adjust values.yaml if needed
- [x] T038 [US4] Verify frontend liveness probe: `/api/health` returns 200, probe interval=10s, timeout=2s — per health-check-contract.md frontend section

**Checkpoint**: All probes functioning. Readiness correctly detects DB failure. Startup allows 30s window. Liveness restarts crashed processes.

---

## Phase 7: User Story 5 — Rollback and Resilience (Priority: P5)

**Goal**: Helm rollback restores previous working version. Stateless resilience — pod kill/restart preserves data in external Neon DB.

**Independent Test**: Deploy bad image via `helm upgrade`, observe failure, run `helm rollback`, previous version restored. Kill pod mid-conversation, replacement pod starts, user resumes conversation.

**Depends on**: Phase 5/US3 (Helm lifecycle must work) and Phase 6/US4 (probes must detect failures)

### Validation for User Story 5

- [x] T039 [US5] Validate rollback: deploy working release (v1), upgrade to broken image (v2), pods fail readiness, run `helm rollback todo-app 1`, previous version restored within 60 seconds — per SC-005
- [x] T040 [US5] Validate --atomic flag: `helm upgrade --atomic` with bad image auto-rolls-back without manual intervention — per FR-048
- [x] T041 [US5] Validate stateless resilience: create a task via chat, kill backend pod (`kubectl delete pod`), wait for replacement, verify conversation continues with history intact from Neon DB — per SC-006

### Implementation for User Story 5

- [x] T042 [US5] Verify `helm history todo-app` shows revision history with chart version, app version, status, and timestamp — per acceptance scenario 5
- [x] T043 [US5] Verify zero-downtime rolling update: with 1 replica, `helm upgrade` creates new pod before terminating old (maxSurge=1, maxUnavailable=0) — at least one healthy pod serves traffic throughout — per SC-013

**Checkpoint**: Rollback works within 60s. Atomic flag auto-rolls-back. Pod restart doesn't lose data. Rolling updates maintain availability.

---

## Phase 8: User Story 6 — AI-Assisted DevOps Operations (Priority: P6)

**Goal**: Document AI tool usage (Gordon, kubectl-ai, kagent) as optional accelerators with manual CLI fallbacks.

**Independent Test**: When AI tools are available, they provide valid suggestions. When unavailable, manual CLI commands achieve the same result. All operations documented.

**Depends on**: Phase 5/US3 (deployed application to operate on)

### Implementation for User Story 6

- [x] T044 [P] [US6] Document Gordon usage examples (Dockerfile optimization, image analysis) in phase-4/helm/todo-app/README.md — include manual Docker CLI fallbacks — per FR-064, FR-068, FR-071
- [x] T045 [P] [US6] Document kubectl-ai usage examples (pod status, scaling, debugging) in phase-4/helm/todo-app/README.md — include manual kubectl fallbacks — per FR-065, FR-068, FR-072
- [x] T046 [P] [US6] Document kagent usage examples (cluster health, resource optimization) in phase-4/helm/todo-app/README.md — include manual kubectl fallbacks — per FR-066, FR-068, FR-073
- [x] T047 [US6] Add AI tool safety notice to README: all AI suggestions require human review before execution, no auto-execute of destructive operations — per FR-067, FR-069

**Checkpoint**: README documents all 3 AI tools with examples. Each AI operation has manual CLI fallback. Safety notice present.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and cleanup across all stories

- [x] T048 [P] Create phase-4/helm/todo-app/README.md — complete deployment instructions covering prerequisites, build, deploy, upgrade, rollback, teardown, troubleshooting, environment variables reference, and AIOps documentation (from T044-T047) — per FR-051
- [x] T049 [P] Run quickstart.md validation — follow the 5-step guide from specs/003-kubernetes-deployment/quickstart.md end-to-end on a clean Minikube cluster, verify all steps work as documented
- [x] T050 Validate all success criteria (SC-001 through SC-015) pass — check image sizes, startup times, resource limits, probe behavior, rollback timing, zero secrets in plaintext, zero-downtime updates
- [x] T051 Validate zero secrets in plain text across all artifacts: Docker images (`docker history`), Helm templates (`helm template`), pod specs (`kubectl get pod -o yaml`), pod logs — per SC-012

**Checkpoint**: All success criteria validated. Documentation complete. Quickstart guide verified. No security violations.

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup ──────────────────────────────────→ No dependencies
Phase 2: Foundational (Health Endpoints) ────────→ Depends on Phase 1
Phase 3: US1 — Docker Containerization (P1) MVP ─→ Depends on Phase 2
Phase 4: US2 — Minikube/Helm Manifests (P2) ─────→ Depends on Phase 3 (images)
Phase 5: US3 — Helm Packaging (P3) ──────────────→ Depends on Phase 4 (templates)
Phase 6: US4 — Health Checks & Probes (P4) ──────→ Depends on Phase 4 (deployed cluster)
Phase 7: US5 — Rollback & Resilience (P5) ───────→ Depends on Phase 5 + Phase 6
Phase 8: US6 — AI-Assisted DevOps (P6) ──────────→ Depends on Phase 5 (deployed app)
Phase 9: Polish ──────────────────────────────────→ Depends on all prior phases
```

### User Story Dependencies

- **US1 (Docker)**: Can start after Phase 2 — no dependency on other stories
- **US2 (Minikube/Helm)**: Depends on US1 (needs built images)
- **US3 (Helm Packaging)**: Depends on US2 (needs Helm templates)
- **US4 (Probes)**: Depends on US2 (needs deployed cluster), can parallel with US3
- **US5 (Rollback)**: Depends on US3 + US4 (needs Helm lifecycle + working probes)
- **US6 (AIOps)**: Depends on US3 (needs deployed app to operate on), can parallel with US4/US5

### Within Each User Story

- Validation tasks define expected outcomes (infrastructure TDD)
- Template/manifest creation before deployment
- Configuration before deployment validation
- Core infrastructure before integration

### Parallel Opportunities

**Phase 1** — T002, T003, T004 can all run in parallel (different files)
**Phase 2** — T005+T006 (validation), T009+T010 (frontend changes) can run in parallel; T007+T008 are sequential (same file)
**Phase 3/US1** — T013+T014 can run in parallel (different Dockerfiles)
**Phase 4/US2** — T021+T022+T023 can run in parallel (different template files); T025+T027 can run in parallel (different service files)
**Phase 8/US6** — T044+T045+T046 can all run in parallel (different README sections)
**Cross-story** — US4 and US6 can start in parallel once US2/US3 dependencies met

---

## Parallel Example: Phase 4 (User Story 2 — Helm Templates)

```bash
# After Chart.yaml, values.yaml, _helpers.tpl are created (T018-T020):

# Launch these 3 template files in parallel (different files, no dependencies):
Task T021: "Create namespace.yaml"
Task T022: "Create configmap.yaml"
Task T023: "Create secret.yaml"

# Then launch these 2 service files in parallel:
Task T025: "Create backend-service.yaml"
Task T027: "Create frontend-service.yaml"

# Deployment files depend on services for selector consistency:
Task T024: "Create backend-deployment.yaml"
Task T026: "Create frontend-deployment.yaml"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (directory structure, ignore files)
2. Complete Phase 2: Foundational (health endpoints in Phase III code)
3. Complete Phase 3: US1 — Docker Containerization
4. **STOP AND VALIDATE**: Both images build, run, and pass health checks
5. This proves Phase III application is container-compatible

### Incremental Delivery

1. Setup + Foundational → Health endpoints working
2. US1 (Docker) → Images build and run locally (MVP!)
3. US2 (Helm Manifests) → Templates lint and render
4. US3 (Helm Packaging) → Full Helm lifecycle works on Minikube
5. US4 (Probes) → K8s manages pod lifecycle automatically
6. US5 (Rollback) → Safety net validated
7. US6 (AIOps) → Optional tooling documented
8. Polish → All SCs validated, docs complete

### Key Risk Points

- **T009**: Adding `output: "standalone"` to next.config.ts — may affect existing frontend behavior; validate build still works
- **T013/T014**: Docker builds — first time containerizing Phase III; expect iterative debugging
- **T028**: Migration Job — Alembic must be correctly configured in Docker image with proper DB URL
- **T032**: deploy.sh — first real Minikube deployment; network/DNS issues likely

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [USn] label maps task to specific user story for traceability
- Infrastructure TDD: validation tasks define expected outcomes before implementation
- Phase III code changes are MINIMAL: 2 health endpoints + 1 config change + 1 new route
- All implementation happens in phase-4/ directory except health endpoints
- Commit after each phase completion for safe rollback points
- Total: 51 tasks across 9 phases covering 6 user stories
