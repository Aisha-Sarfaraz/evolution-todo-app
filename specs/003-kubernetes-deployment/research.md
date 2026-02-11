# Phase IV Research: Local Kubernetes Deployment

**Feature Branch**: `003-kubernetes-deployment`
**Created**: 2026-02-07
**Sources**: Codebase analysis, Helm docs (Context7 /websites/helm_sh), Kubernetes docs (Context7 /websites/kubernetes_io), Phase II/III Dockerfiles
**Implementation Directory**: `phase-4/` (Helm charts, K8s manifests, scripts)

---

## Research Tasks

### R1: Backend Dockerfile Strategy (Multi-Stage Build)

**Decision**: Multi-stage build with `builder` and `production` stages using `python:3.11-slim`

**Rationale**:
- Phase III backend currently uses a single-stage Dockerfile with `python:3.11-slim` (31 lines)
- Phase II backend already demonstrates the multi-stage pattern (`python:3.13-slim as builder` -> `python:3.13-slim as production`)
- Multi-stage separates build dependencies (`gcc`, `libpq-dev`) from the production image, reducing final image size by 50-70%
- Phase III backend requires `psycopg2-binary` and `asyncpg` which need `libpq-dev` at build time

**Pattern** (adapted from Phase II `phase-2/backend/Dockerfile`):
```
Stage 1 (builder): python:3.11-slim
  - Install gcc, libpq-dev (build deps)
  - pip install from requirements.txt

Stage 2 (production): python:3.11-slim
  - Create non-root user (UID 1000)
  - Copy site-packages from builder
  - Copy src/, migrations/, alembic.ini
  - Set PYTHONUNBUFFERED=1, PYTHONDONTWRITEBYTECODE=1
  - HEALTHCHECK on /health
  - Expose port 7860
```

**File Location**: `phase-4/docker/backend.Dockerfile` (references `phase-3/backend/` as build context)

**Alternatives Considered**:
1. ~~Single-stage build~~ — Rejected: includes build tools in production image (200MB+ wasted)
2. ~~Alpine-based image~~ — Rejected: musl libc causes compatibility issues with asyncpg/psycopg2
3. ~~Python 3.13-slim~~ — Rejected: Phase III code tested on Python 3.11; version mismatch risk

**Key Insight**: The existing Phase III Dockerfile uses `requirements.txt`, not `pyproject.toml` for pip install. The multi-stage build must use `pip install -r requirements.txt` (not `pip install .`).

---

### R2: Frontend Dockerfile Strategy (Next.js Standalone)

**Decision**: Next.js `output: "standalone"` mode with multi-stage Node.js build

**Rationale**:
- Phase III frontend has no Dockerfile — this is a new artifact
- `next.config.ts` is currently empty (no `output` setting)
- Next.js standalone mode produces a self-contained `server.js` + minimal `node_modules`
- Standalone images are typically 100-200MB vs 1GB+ for full node_modules

**Pattern**:
```
Stage 1 (deps): node:20-alpine
  - Copy package.json, package-lock.json
  - npm ci (install deps)

Stage 2 (builder): node:20-alpine
  - Copy deps from stage 1
  - Copy source code
  - Set NEXT_PUBLIC_* env vars as build args
  - npm run build

Stage 3 (runner): node:20-alpine
  - Create non-root user (UID 1000)
  - Copy .next/standalone (server.js + minimal node_modules)
  - Copy .next/static to .next/static
  - Copy public/ to public/
  - Expose port 3000
  - CMD ["node", "server.js"]
```

**File Location**: `phase-4/docker/frontend.Dockerfile` (references `phase-3/frontend/` as build context)

**Critical Detail — NEXT_PUBLIC_* Environment Variables**:
- `NEXT_PUBLIC_API_URL` — Backend API URL (used in lib/api.ts, lib/push.ts, ChatContainer.tsx)
- `NEXT_PUBLIC_AUTH_URL` — Auth URL (used in lib/auth.ts, chat/page.tsx)
- `NEXT_PUBLIC_VAPID_PUBLIC_KEY` — Push notification key (used in lib/push.ts)
- `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` — ChatKit domain key (used in ChatContainer.tsx)

These are **baked into the JavaScript bundle at build time** (not runtime). For Kubernetes deployment:
- Backend URL must point to the K8s backend Service: `http://todo-backend.todo-app.svc.cluster.local:7860/api`
- Auth URL can be the frontend itself: `http://localhost:3000` (or the LoadBalancer IP)
- These must be set as Docker build args, not runtime env vars

**Alternatives Considered**:
1. ~~Static export + nginx~~ — Rejected: loses SSR, API routes (/api/chat/route.ts is critical)
2. ~~Full node_modules copy~~ — Rejected: 1GB+ image, unnecessary dependencies

**Configuration Change Required**: Add `output: "standalone"` to `phase-3/frontend/next.config.ts`

---

### R3: Health Check Endpoint Design

**Decision**: Split existing `/health` into `/health/live` (liveness) and `/health/ready` (readiness)

**Rationale**:
- Current `/health` endpoint (`phase-3/backend/src/main.py:83-94`) returns basic status without checking dependencies
- Kubernetes requires separate probe semantics:
  - **Liveness**: "Is the process alive?" — Should NOT check database (avoids cascade restarts)
  - **Readiness**: "Can I serve traffic?" — MUST check database connectivity
- Constitution mandates separate `/health/live` and `/health/ready` endpoints (lines 1460-1462)

**Liveness Probe Design** (`/health/live`):
```python
@app.get("/health/live")
async def health_live():
    return {"status": "alive", "service": "todo-chatbot-api", "version": "3.0.0"}
```
- Returns 200 if the FastAPI process is running
- No dependency checks (avoids false positives from transient DB issues)
- Timeout: 2s, Interval: 10s, Failure threshold: 3

**Readiness Probe Design** (`/health/ready`):
```python
@app.get("/health/ready")
async def health_ready():
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not_ready", "database": "disconnected"})
```
- Returns 200 if the database is reachable
- Returns 503 if the database is down (K8s removes pod from Service endpoints)
- Timeout: 5s, Interval: 5s, Failure threshold: 3

**Startup Probe Design**:
- Path: `/health/live` (same as liveness)
- `failureThreshold: 6`, `periodSeconds: 5` -> allows 30s startup window
- Disables liveness/readiness probes until startup succeeds

**Backward Compatibility**: Keep existing `/health` endpoint (it's referenced in the existing Dockerfile HEALTHCHECK) — delegates to `/health/live`.

---

### R4: Helm Chart Architecture

**Decision**: Single umbrella chart at `phase-4/helm/todo-app/` with service-specific templates

**Rationale**:
- User chose single umbrella chart (clarification Q1)
- Simpler for Phase IV local deployment; can evolve to sub-charts in Phase V
- Helm docs (Context7) confirm this is the standard approach for small applications

**Chart Directory Structure**:
```
phase-4/
├── helm/
│   └── todo-app/
│       ├── Chart.yaml              # Chart metadata (name: todo-app, version: 0.1.0, appVersion: 3.0.0)
│       ├── values.yaml             # Default values (all parameters documented)
│       ├── values-dev.yaml         # Development overrides
│       ├── README.md               # Deployment instructions
│       ├── .helmignore             # Ignore patterns
│       └── templates/
│           ├── _helpers.tpl        # Template functions (fullname, labels, selectorLabels)
│           ├── NOTES.txt           # Post-install instructions
│           ├── namespace.yaml      # Namespace (todo-app)
│           ├── configmap.yaml      # Non-sensitive configuration
│           ├── secret.yaml         # Sensitive credentials
│           ├── backend-deployment.yaml
│           ├── backend-service.yaml
│           ├── frontend-deployment.yaml
│           ├── frontend-service.yaml
│           └── migration-job.yaml  # Alembic migration Helm hook
├── docker/
│   ├── backend.Dockerfile          # Multi-stage backend build
│   ├── frontend.Dockerfile         # Next.js standalone build
│   ├── backend.dockerignore        # Backend ignore patterns
│   └── frontend.dockerignore       # Frontend ignore patterns
└── scripts/
    ├── build.sh                    # Build Docker images
    ├── deploy.sh                   # Deploy to Minikube via Helm
    └── teardown.sh                 # Remove deployment
```

**values.yaml Organization** (per Helm best practices):
```yaml
global:
  namespace: todo-app
  environment: development

backend:
  replicaCount: 1
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 7860
  resources:
    requests: { cpu: 250m, memory: 256Mi }
    limits: { cpu: 500m, memory: 512Mi }
  probes:
    liveness: { path: /health/live, port: 7860 }
    readiness: { path: /health/ready, port: 7860 }
    startup: { path: /health/live, port: 7860 }

frontend:
  replicaCount: 1
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: LoadBalancer
    port: 3000
  resources:
    requests: { cpu: 100m, memory: 128Mi }
    limits: { cpu: 250m, memory: 256Mi }

database:
  external: true
  # Connection URL provided via Secret, not here
```

**Alternatives Considered**:
1. ~~Separate charts per service~~ — Rejected: over-engineering for 2 services
2. ~~Umbrella with sub-charts~~ — Rejected: adds `charts/` directory complexity, better for Phase V
3. ~~Kustomize instead of Helm~~ — Rejected: Helm required by hackathon spec; Helm provides rollback

---

### R5: Kubernetes Service Architecture

**Decision**: ClusterIP for backend, LoadBalancer for frontend, dedicated `todo-app` namespace

**Rationale**:
- Backend only needs internal access (frontend -> backend within cluster)
- Frontend needs external access from developer's browser
- Minikube supports LoadBalancer via `minikube tunnel`
- Namespace isolation is a Kubernetes best practice for multi-tenant clusters

**Service Topology**:
```
[Developer Browser] -> LoadBalancer:3000 -> [Frontend Pod] -> ClusterIP:7860 -> [Backend Pod] -> [External Neon DB]
```

**Frontend-to-Backend Communication**:
- Inside K8s cluster, frontend pods reach backend via DNS: `http://todo-backend.todo-app.svc.cluster.local:7860`
- Next.js API routes (`/api/chat/route.ts`) proxy requests server-side — browser never needs direct backend access
- `NEXT_PUBLIC_API_URL` is used server-side in Next.js API routes — K8s ClusterIP DNS works here
- Browser calls frontend `/api/chat`, which server-side proxies to backend ClusterIP

**Alternatives Considered**:
1. ~~Ingress controller~~ — Rejected: adds nginx-ingress dependency, over-engineering for local dev
2. ~~NodePort~~ — Rejected: less production-like than LoadBalancer, port range limitations

---

### R6: Secret Management Strategy

**Decision**: Kubernetes Secrets with base64 encoding, values injected via `--set` or `values.yaml` (not committed to Git)

**Rationale**:
- Constitution mandates zero plaintext secrets in Git/images/logs
- K8s Secrets are base64-encoded (not encrypted, but separate from manifests)
- For Phase IV (local dev), `--set` or `values-local.yaml` (gitignored) is sufficient
- Phase V would use cloud secret managers (Azure Key Vault, GCP Secret Manager)

**Required Secrets** (from Phase III codebase analysis):
| Key | Source | Used By |
|-----|--------|---------|
| `DATABASE_URL` | `database.py:11` (os.getenv) | Backend — Neon DB connection |
| `OPENROUTER_API_KEY` | Agent config | Backend — LLM API access |
| `BETTER_AUTH_SECRET` | Auth config | Backend — JWT signing |
| `VAPID_PRIVATE_KEY` | Push config | Backend — Web push encryption |
| `VAPID_PUBLIC_KEY` | Push config | Backend — Web push (also in frontend build) |

**Required ConfigMap Values** (non-sensitive):
| Key | Default | Used By |
|-----|---------|---------|
| `LOG_LEVEL` | `INFO` | Backend — `main.py:31` |
| `LOG_FORMAT` | `json` | Backend — `main.py:32` |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | Backend — CORS `main.py:60-66` |
| `ENVIRONMENT` | `development` | Backend — runtime mode |

---

### R7: Minikube Image Loading Strategy

**Decision**: Use `minikube image load` for loading locally-built images

**Rationale**:
- Three approaches exist for making local images available to Minikube:
  1. `eval $(minikube docker-env)` — Builds directly in Minikube's Docker daemon
  2. `minikube image load <image>` — Copies image from host to Minikube
  3. Local registry (localhost:5000) — Adds complexity
- Option 2 (`minikube image load`) is simplest and works consistently across platforms (Windows, Mac, Linux)
- Combined with `imagePullPolicy: IfNotPresent` (or `Never`), avoids external registry dependency

**Workflow**:
```bash
# Build images on host
docker build -t todo-backend:latest -f phase-4/docker/backend.Dockerfile phase-3/backend/
docker build -t todo-frontend:latest -f phase-4/docker/frontend.Dockerfile phase-3/frontend/

# Load into Minikube
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# Deploy with Helm
helm install todo-app phase-4/helm/todo-app/
```

**Alternatives Considered**:
1. ~~eval $(minikube docker-env)~~ — Platform-specific issues on Windows (Docker Desktop vs Minikube Docker)
2. ~~Local registry~~ — Over-engineering for local development

---

### R8: Database Migration Strategy in Kubernetes

**Decision**: Helm pre-install/pre-upgrade hook with Job for Alembic migrations

**Rationale**:
- Alembic migrations must run BEFORE the application starts (schema must exist)
- Two K8s patterns: init container vs Helm hook Job
- Helm hook Job runs as a separate pod, completes before main deployment, and can be debugged independently
- Init container approach couples migration lifecycle to every pod restart

**Pattern**:
```yaml
# templates/migration-job.yaml (Helm hook)
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "todo-app.fullname" . }}-migrate
  annotations:
    "helm.sh/hook": pre-install,pre-upgrade
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  template:
    spec:
      containers:
      - name: migrate
        image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
        command: ["alembic", "upgrade", "head"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {{ include "todo-app.fullname" . }}-secret
              key: database-url
      restartPolicy: Never
  backoffLimit: 3
```

**Alternatives Considered**:
1. ~~Init container~~ — Rejected: runs on EVERY pod restart, not just deployments
2. ~~Manual migration before deploy~~ — Rejected: violates automation principle
3. ~~Application-startup migration~~ — Rejected: race condition with multiple replicas

---

## Summary of All Decisions

| # | Decision | Choice | Alternatives Rejected |
|---|----------|--------|----------------------|
| R1 | Backend Dockerfile | Multi-stage python:3.11-slim | Single-stage, Alpine, Python 3.13 |
| R2 | Frontend Dockerfile | Next.js standalone + node:20-alpine | Static export + nginx, full node_modules |
| R3 | Health Checks | Separate /health/live + /health/ready | Single /health endpoint |
| R4 | Helm Chart | Single umbrella at phase-4/helm/todo-app/ | Separate charts, sub-charts, Kustomize |
| R5 | K8s Services | ClusterIP (backend) + LoadBalancer (frontend) | Ingress, NodePort |
| R6 | Secrets | K8s Secrets via --set, gitignored values | Hardcoded, vault (Phase V) |
| R7 | Image Loading | minikube image load | docker-env, local registry |
| R8 | Migrations | Helm hook Job (pre-install/pre-upgrade) | Init container, manual, app-startup |
