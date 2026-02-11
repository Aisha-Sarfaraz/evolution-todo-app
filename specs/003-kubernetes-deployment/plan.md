# Implementation Plan: Local Kubernetes Deployment

**Branch**: `003-kubernetes-deployment` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-kubernetes-deployment/spec.md`

## Summary

Deploy the Phase III Todo AI Chatbot (FastAPI backend + Next.js frontend) to a local Minikube Kubernetes cluster using Docker multi-stage builds, a single umbrella Helm chart, and AI-assisted DevOps tooling (Gordon, kubectl-ai, kagent). No new business features — focus is containerization, orchestration, and operability. All infrastructure artifacts live in `phase-4/`.

## Technical Context

**Language/Version**: Python 3.11 (backend), Node.js 20 (frontend), Go templates (Helm)
**Primary Dependencies**: Docker Desktop 4.53+, Minikube 1.32+, Helm 3.14+, kubectl 1.28+
**Storage**: External Neon Serverless PostgreSQL (NOT deployed in K8s)
**Testing**: `helm lint`, `helm template`, `kubectl get pods`, manual E2E via browser
**Target Platform**: Local Minikube cluster (Docker driver, Windows/macOS/Linux)
**Project Type**: Infrastructure/DevOps (containerization + orchestration of existing web application)
**Performance Goals**: Container startup < 30s, graceful shutdown < 10s, zero-downtime rolling updates
**Constraints**: CPU 500m limit, Memory 512Mi limit per pod (constitution-mandated)
**Scale/Scope**: 2 services (backend, frontend), 1 replica each (configurable), single Minikube cluster

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-Driven Development | PASS | spec.md created and approved before planning |
| II. No Manual Coding | PASS | All artifacts generated via Claude Code |
| III. Test-Driven Development | PASS | Health check tests before endpoints; `helm lint` before deploy |
| IV. Clean Separation of Concerns | PASS | Docker (container), K8s (orchestration), Helm (packaging) — clear boundaries |
| V. Code Modularity & Reusability | PASS | Helm chart parameterized, reusable for Phase V cloud |
| VI. Security, Isolation & Observability | PASS | Non-root users, K8s Secrets, namespace isolation, structured logging |
| VII. Code Quality | PASS | Multi-stage Dockerfiles, .dockerignore, deterministic image tags |
| VIII. Performance | PASS | Startup < 30s, shutdown < 10s, resource limits enforced |

**Gate Result**: PASS — All 8 principles satisfied. No violations.

---

## Project Structure

### Documentation (this feature)

```text
specs/003-kubernetes-deployment/
├── spec.md              # Feature specification (75 FRs, 6 stories)
├── plan.md              # This file
├── research.md          # 8 research decisions (R1-R8)
├── data-model.md        # 6 infrastructure entities
├── quickstart.md        # Deployment guide (5 steps)
├── contracts/
│   ├── helm-values-contract.md   # Helm values schema
│   └── health-check-contract.md  # Probe endpoint contracts
├── checklists/
│   └── requirements.md           # Spec quality validation
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (implementation directory)

```text
phase-4/
├── docker/
│   ├── backend.Dockerfile          # Multi-stage Python 3.11-slim build
│   ├── frontend.Dockerfile         # Next.js standalone + node:20-alpine
│   ├── backend.dockerignore        # Backend ignore patterns
│   └── frontend.dockerignore       # Frontend ignore patterns
├── helm/
│   └── todo-app/
│       ├── Chart.yaml              # Chart metadata (v0.1.0, appVersion 3.0.0)
│       ├── values.yaml             # Default values (documented)
│       ├── values-dev.yaml         # Development overrides
│       ├── README.md               # Deployment instructions
│       ├── .helmignore             # Ignore patterns
│       └── templates/
│           ├── _helpers.tpl        # fullname, labels, selectorLabels
│           ├── NOTES.txt           # Post-install instructions
│           ├── namespace.yaml
│           ├── configmap.yaml
│           ├── secret.yaml
│           ├── backend-deployment.yaml
│           ├── backend-service.yaml
│           ├── frontend-deployment.yaml
│           ├── frontend-service.yaml
│           └── migration-job.yaml  # Alembic migration Helm hook
└── scripts/
    ├── build.sh                    # Build Docker images
    ├── deploy.sh                   # Deploy to Minikube
    └── teardown.sh                 # Remove deployment
```

### Phase III Code Changes (minimal, infrastructure-only)

```text
phase-3/backend/src/main.py         # Add /health/live and /health/ready endpoints
phase-3/frontend/next.config.ts     # Add output: "standalone"
phase-3/frontend/app/api/health/route.ts  # New: frontend health check endpoint
```

**Structure Decision**: Infrastructure code lives in `phase-4/` (consistent with `Phase-1/`, `phase-2/`, `phase-3/`). Dockerfiles reference `phase-3/` as build context. Minimal changes to Phase III code (health endpoints only, no business logic changes).

---

## Architecture Decisions

### AD-1: Service Architecture (2 Services)

```
[Browser] → LoadBalancer:3000 → [Frontend Pod] → ClusterIP:7860 → [Backend Pod] → [Neon DB]
```

- **Backend pod**: FastAPI + embedded MCP server + AI agent (single process, port 7860)
- **Frontend pod**: Next.js standalone server (port 3000)
- **Database**: External Neon PostgreSQL (NOT in K8s)

**Rationale**: Matches Phase III architecture. MCP embedded in backend = no code splitting needed. External DB simplifies K8s (no StatefulSet, no PV).

### AD-2: Docker Strategy

| Service | Base Image | Build Stages | Final Size Target |
|---------|-----------|-------------|-------------------|
| Backend | python:3.11-slim | builder → production | < 500MB |
| Frontend | node:20-alpine | deps → builder → runner | < 300MB |

**Key patterns**:
- Non-root user (UID 1000) in both images
- Layer caching: dependencies installed before source code
- `.dockerignore`: exclude .git, node_modules, .env, tests
- Deterministic base image tags (no `:latest` for base)

### AD-3: Helm Chart Design

**Single umbrella chart** at `phase-4/helm/todo-app/` deploying both services in one release.

**values.yaml sections**: `global`, `backend`, `frontend`, `database`, `config`, `secrets`

**Key features**:
- Environment overrides via `-f values-dev.yaml`
- Secret injection via `--set secrets.databaseUrl=...`
- Probe paths configurable
- Replica counts configurable
- Resource limits configurable
- `--atomic` upgrade support (auto-rollback on failure)

### AD-4: Health Check Design

| Endpoint | Type | Checks DB | Response |
|----------|------|-----------|----------|
| `/health/live` | Liveness | No | 200 {"status": "alive"} |
| `/health/ready` | Readiness | Yes | 200/503 {"status": "ready/not_ready"} |
| `/health` | Legacy | No | 200 {"status": "healthy"} (backward compat) |
| `/api/health` (frontend) | Liveness | No | 200 {"status": "ok"} |

### AD-5: Database Migration Strategy

Helm pre-install/pre-upgrade hook Job runs `alembic upgrade head` before main deployment. Idempotent, debuggable, decoupled from pod lifecycle.

### AD-6: Image Loading Strategy

`minikube image load` for loading locally-built images. Cross-platform compatible. Combined with `imagePullPolicy: IfNotPresent`.

---

## Non-Functional Requirements

### Performance Budget

| Metric | Target | Source |
|--------|--------|--------|
| Container startup | < 30s | Constitution Phase IV |
| Graceful shutdown | < 10s | Constitution Phase IV |
| Liveness probe response | < 2s | Health check contract |
| Readiness probe response | < 5s | Health check contract |
| Helm install (cold) | < 2 min | SC-004 |
| Helm rollback | < 60s | SC-005 |
| Total cluster RAM (2 pods) | < 2GB | SC-014 |
| Total cluster CPU (2 pods) | < 2 cores | SC-014 |

### Resource Limits

| Service | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|------------|-----------|----------------|--------------|
| Backend | 250m | 500m | 256Mi | 512Mi |
| Frontend | 100m | 250m | 128Mi | 256Mi |
| Migration Job | 100m | 250m | 128Mi | 256Mi |

### Security

- All containers run as non-root (UID 1000)
- Secrets stored in K8s Secrets (base64), injected as env vars
- No secrets in Docker images, Git, or logs
- `.dockerignore` excludes .env files
- Helm chart `secret.yaml` values via `--set` (not committed)

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| NEXT_PUBLIC_* vars baked at build time wrong URL | Medium | High (frontend can't reach backend) | Document build args clearly; test with curl inside pod |
| Minikube tunnel drops on Windows | Medium | Medium (services become inaccessible) | Document restart procedure; NodePort as fallback |
| Neon DB connection fails from Minikube | Low | High (backend unusable) | Readiness probe detects; verify DNS/network from pod |

---

## Implementation Order

### Phase A: Foundation (Dockerfiles + Health Checks)
1. Add `/health/live` and `/health/ready` to Phase III backend (`main.py`)
2. Add `/api/health` route to Phase III frontend
3. Add `output: "standalone"` to `next.config.ts`
4. Create `phase-4/docker/backend.Dockerfile` (multi-stage)
5. Create `phase-4/docker/frontend.Dockerfile` (standalone)
6. Create `.dockerignore` files
7. Build and test images locally with `docker run`

### Phase B: Kubernetes Manifests (via Helm)
8. Create Helm chart structure at `phase-4/helm/todo-app/`
9. Write `Chart.yaml` and `values.yaml`
10. Write `_helpers.tpl` template functions
11. Write `namespace.yaml` template
12. Write `configmap.yaml` and `secret.yaml` templates
13. Write `backend-deployment.yaml` and `backend-service.yaml`
14. Write `frontend-deployment.yaml` and `frontend-service.yaml`
15. Write `migration-job.yaml` (Helm hook)
16. Write `NOTES.txt` post-install instructions
17. Run `helm lint` and `helm template` validation

### Phase C: Deploy and Validate
18. Create `phase-4/scripts/build.sh` (build + load images)
19. Create `phase-4/scripts/deploy.sh` (helm install)
20. Deploy to Minikube and validate all pods healthy
21. Test end-to-end (create task via chat, verify persistence)
22. Test rollback (upgrade to bad image, rollback)
23. Test stateless resilience (kill pod, resume conversation)

### Phase D: Documentation and AIOps
24. Write `phase-4/helm/todo-app/README.md`
25. Document AIOps usage (Gordon, kubectl-ai, kagent examples)
26. Create `phase-4/scripts/teardown.sh`

---

## Complexity Tracking

No constitution violations. No complexity justifications needed.

| Concern | Resolution |
|---------|-----------|
| Phase III code changes | Minimal: 2 health endpoints + 1 config change. No business logic modified. |
| NEXT_PUBLIC_* build-time vars | Documented in research R2. Build args required, not runtime env vars. |
| External DB from Minikube | Neon DB accessible via internet from Minikube pods. Readiness probe validates. |
