# Phase IV Data Model: Infrastructure Entities

**Feature Branch**: `003-kubernetes-deployment`
**Created**: 2026-02-07

---

## Overview

Phase IV does not modify the Phase III application data model. These entities represent **infrastructure artifacts** — the deployment objects that Phase IV creates and manages.

---

## Entity: DockerImage

**Purpose**: Container artifact produced by building a Dockerfile

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | string | Image name (e.g., `todo-backend`, `todo-frontend`) |
| `tag` | string | Version identifier (semantic version or git SHA) |
| `baseImage` | string | Base image used in production stage (e.g., `python:3.11-slim`, `node:20-alpine`) |
| `stages` | list | Build stages (e.g., `[builder, production]` or `[deps, builder, runner]`) |
| `exposedPort` | integer | Port exposed by the container (backend: 7860, frontend: 3000) |
| `healthCheckPath` | string | HTTP path for Docker HEALTHCHECK (e.g., `/health`) |
| `user` | string | Non-root user (UID 1000) |
| `sizeLimit` | string | Maximum image size (backend: 500MB, frontend: 300MB) |

**Relationships**:
- One DockerImage per service (backend, frontend)
- Referenced by KubernetesDeployment (image repository + tag)

**Validation Rules**:
- `name` must be lowercase alphanumeric with hyphens
- `tag` must not be `latest` in production (Phase V)
- `exposedPort` must match the application's listening port
- `user` must be non-root (UID >= 1000)

---

## Entity: KubernetesDeployment

**Purpose**: Stateless workload specification for running pod replicas

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | string | Deployment name (e.g., `todo-backend`, `todo-frontend`) |
| `namespace` | string | K8s namespace (`todo-app`) |
| `replicaCount` | integer | Number of pod replicas (default: 1) |
| `image` | DockerImage | Container image reference |
| `imagePullPolicy` | enum | `IfNotPresent` (dev), `Always` (CI/CD) |
| `containerPort` | integer | Port the container listens on |
| `resources.requests.cpu` | string | CPU request (e.g., `250m`) |
| `resources.requests.memory` | string | Memory request (e.g., `256Mi`) |
| `resources.limits.cpu` | string | CPU limit (e.g., `500m`) |
| `resources.limits.memory` | string | Memory limit (e.g., `512Mi`) |
| `strategy.type` | string | `RollingUpdate` |
| `strategy.maxUnavailable` | integer | `0` (zero-downtime) |
| `strategy.maxSurge` | integer | `1` |
| `terminationGracePeriodSeconds` | integer | `10` |
| `livenessProbe` | ProbeConfig | Liveness probe configuration |
| `readinessProbe` | ProbeConfig | Readiness probe configuration |
| `startupProbe` | ProbeConfig | Startup probe configuration |
| `envFrom` | list | ConfigMap and Secret references |
| `labels` | map | `app`, `component`, `version` |

**Relationships**:
- References one DockerImage
- Referenced by one KubernetesService (via label selector)
- Reads from ConfigMap and Secret resources

**State Transitions**:
```
Pending -> Running -> Succeeded (for Jobs)
Pending -> Running -> Failed -> Running (restart on probe failure)
```

---

## Entity: ProbeConfig

**Purpose**: Health check probe configuration for Kubernetes

| Attribute | Type | Description |
|-----------|------|-------------|
| `type` | enum | `liveness`, `readiness`, `startup` |
| `httpGet.path` | string | HTTP endpoint path |
| `httpGet.port` | integer | Container port |
| `initialDelaySeconds` | integer | Delay before first probe |
| `periodSeconds` | integer | Probe interval |
| `timeoutSeconds` | integer | Probe timeout |
| `failureThreshold` | integer | Failures before action |
| `successThreshold` | integer | Successes to recover |

**Default Values by Probe Type**:

| Probe | Path | Interval | Timeout | Failure Threshold |
|-------|------|----------|---------|-------------------|
| Liveness | `/health/live` | 10s | 2s | 3 |
| Readiness | `/health/ready` | 5s | 5s | 3 |
| Startup | `/health/live` | 5s | 2s | 6 (= 30s window) |

---

## Entity: KubernetesService

**Purpose**: Stable network endpoint for accessing pods

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | string | Service name (e.g., `todo-backend`, `todo-frontend`) |
| `namespace` | string | K8s namespace (`todo-app`) |
| `type` | enum | `ClusterIP` (backend) or `LoadBalancer` (frontend) |
| `port` | integer | Service port (external-facing) |
| `targetPort` | integer | Container port |
| `selector` | map | Label selector matching Deployment pods |

**Relationships**:
- Points to one KubernetesDeployment via label selector
- Provides DNS name: `<name>.<namespace>.svc.cluster.local`

**Service Mapping**:

| Service | Type | Port | Target Port | DNS |
|---------|------|------|-------------|-----|
| `todo-backend` | ClusterIP | 7860 | 7860 | `todo-backend.todo-app.svc.cluster.local` |
| `todo-frontend` | LoadBalancer | 3000 | 3000 | `todo-frontend.todo-app.svc.cluster.local` |

---

## Entity: HelmChart

**Purpose**: Packaged Kubernetes application with parameterized templates

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | string | Chart name (`todo-app`) |
| `version` | string | Chart version (semantic, starting at `0.1.0`) |
| `appVersion` | string | Application version (`3.0.0` from Phase III) |
| `description` | string | Human-readable description |
| `templates` | list | K8s manifest templates |
| `values` | map | Configurable parameters |
| `location` | string | `phase-4/helm/todo-app/` |

**Template Files**:
- `namespace.yaml` — Namespace
- `configmap.yaml` — Non-sensitive configuration
- `secret.yaml` — Sensitive credentials
- `backend-deployment.yaml` — Backend Deployment
- `backend-service.yaml` — Backend Service
- `frontend-deployment.yaml` — Frontend Deployment
- `frontend-service.yaml` — Frontend Service
- `migration-job.yaml` — Alembic migration (Helm hook)
- `_helpers.tpl` — Reusable template functions
- `NOTES.txt` — Post-install instructions

**Relationships**:
- Contains templates for all KubernetesDeployment, KubernetesService entities
- References ConfigMap and Secret
- Manages migration Job via Helm hooks

---

## Entity: HealthCheckEndpoint

**Purpose**: HTTP endpoint consumed by Kubernetes probes

| Attribute | Type | Description |
|-----------|------|-------------|
| `path` | string | URL path (e.g., `/health/live`) |
| `method` | string | HTTP method (`GET`) |
| `service` | string | Which service exposes it (`backend`, `frontend`) |
| `successCode` | integer | HTTP 200 |
| `failureCode` | integer | HTTP 503 (readiness only) |
| `checksDatabase` | boolean | Whether it validates DB connectivity |
| `responseFields` | list | Response JSON keys (status, service, version, database) |

**Endpoint Catalog**:

| Service | Path | Purpose | Checks DB | Response |
|---------|------|---------|-----------|----------|
| Backend | `/health/live` | Liveness (process alive) | No | `{"status": "alive", "service": "todo-chatbot-api", "version": "3.0.0"}` |
| Backend | `/health/ready` | Readiness (ready for traffic) | Yes | `{"status": "ready", "database": "connected"}` or `503 {"status": "not_ready", "database": "disconnected"}` |
| Backend | `/health` | Legacy (backward compat) | No | `{"status": "healthy", ...}` |
| Frontend | `/api/health` | Liveness (Next.js alive) | No | `{"status": "ok"}` |
