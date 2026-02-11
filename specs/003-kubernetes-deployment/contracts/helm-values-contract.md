# Helm Values Contract: todo-app Chart

**Feature Branch**: `003-kubernetes-deployment`
**Chart Location**: `phase-4/helm/todo-app/`
**Version**: 0.1.0

---

## values.yaml Schema

This contract defines all configurable parameters for the `todo-app` Helm chart.

### Global Configuration

| Key | Type | Default | Required | Description |
|-----|------|---------|----------|-------------|
| `global.namespace` | string | `todo-app` | Yes | Kubernetes namespace for all resources |
| `global.environment` | string | `development` | Yes | Deployment environment (development, staging, production) |

### Backend Configuration

| Key | Type | Default | Required | Description |
|-----|------|---------|----------|-------------|
| `backend.replicaCount` | integer | `1` | Yes | Number of backend pod replicas |
| `backend.image.repository` | string | `todo-backend` | Yes | Docker image repository |
| `backend.image.tag` | string | `latest` | Yes | Docker image tag |
| `backend.image.pullPolicy` | string | `IfNotPresent` | Yes | Image pull policy |
| `backend.service.type` | string | `ClusterIP` | Yes | K8s Service type |
| `backend.service.port` | integer | `7860` | Yes | Service port |
| `backend.resources.requests.cpu` | string | `250m` | Yes | CPU request |
| `backend.resources.requests.memory` | string | `256Mi` | Yes | Memory request |
| `backend.resources.limits.cpu` | string | `500m` | Yes | CPU limit |
| `backend.resources.limits.memory` | string | `512Mi` | Yes | Memory limit |
| `backend.probes.liveness.path` | string | `/health/live` | Yes | Liveness probe path |
| `backend.probes.liveness.port` | integer | `7860` | Yes | Liveness probe port |
| `backend.probes.liveness.initialDelaySeconds` | integer | `5` | No | Delay before first liveness probe |
| `backend.probes.liveness.periodSeconds` | integer | `10` | No | Interval between liveness probes |
| `backend.probes.liveness.timeoutSeconds` | integer | `2` | No | Liveness probe timeout |
| `backend.probes.liveness.failureThreshold` | integer | `3` | No | Liveness failures before restart |
| `backend.probes.readiness.path` | string | `/health/ready` | Yes | Readiness probe path |
| `backend.probes.readiness.port` | integer | `7860` | Yes | Readiness probe port |
| `backend.probes.readiness.initialDelaySeconds` | integer | `5` | No | Delay before first readiness probe |
| `backend.probes.readiness.periodSeconds` | integer | `5` | No | Interval between readiness probes |
| `backend.probes.readiness.timeoutSeconds` | integer | `5` | No | Readiness probe timeout |
| `backend.probes.readiness.failureThreshold` | integer | `3` | No | Readiness failures before removal |
| `backend.probes.startup.path` | string | `/health/live` | Yes | Startup probe path |
| `backend.probes.startup.port` | integer | `7860` | Yes | Startup probe port |
| `backend.probes.startup.periodSeconds` | integer | `5` | No | Interval between startup probes |
| `backend.probes.startup.failureThreshold` | integer | `6` | No | Startup failures (6 * 5s = 30s window) |
| `backend.terminationGracePeriodSeconds` | integer | `10` | No | Graceful shutdown window |

### Frontend Configuration

| Key | Type | Default | Required | Description |
|-----|------|---------|----------|-------------|
| `frontend.replicaCount` | integer | `1` | Yes | Number of frontend pod replicas |
| `frontend.image.repository` | string | `todo-frontend` | Yes | Docker image repository |
| `frontend.image.tag` | string | `latest` | Yes | Docker image tag |
| `frontend.image.pullPolicy` | string | `IfNotPresent` | Yes | Image pull policy |
| `frontend.service.type` | string | `LoadBalancer` | Yes | K8s Service type |
| `frontend.service.port` | integer | `3000` | Yes | Service port |
| `frontend.resources.requests.cpu` | string | `100m` | Yes | CPU request |
| `frontend.resources.requests.memory` | string | `128Mi` | Yes | Memory request |
| `frontend.resources.limits.cpu` | string | `250m` | Yes | CPU limit |
| `frontend.resources.limits.memory` | string | `256Mi` | Yes | Memory limit |
| `frontend.probes.liveness.path` | string | `/api/health` | Yes | Liveness probe path |
| `frontend.probes.liveness.port` | integer | `3000` | Yes | Liveness probe port |

### Database Configuration

| Key | Type | Default | Required | Description |
|-----|------|---------|----------|-------------|
| `database.external` | boolean | `true` | Yes | Database is external (Neon), not deployed in K8s |

### Secrets Configuration (NOT in values.yaml — passed via --set)

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `secrets.databaseUrl` | string | Yes | Neon PostgreSQL connection URL |
| `secrets.openrouterApiKey` | string | Yes | OpenRouter LLM API key |
| `secrets.betterAuthSecret` | string | Yes | Better Auth JWT signing secret |
| `secrets.vapidPrivateKey` | string | Yes | VAPID private key for web push |
| `secrets.vapidPublicKey` | string | Yes | VAPID public key for web push |

### ConfigMap Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `config.logLevel` | string | `INFO` | Application log level |
| `config.logFormat` | string | `json` | Log format (json or text) |
| `config.allowedOrigins` | string | `http://localhost:3000` | CORS allowed origins |
| `config.environment` | string | `development` | Runtime environment name |

---

## Installation Examples

### Minimal (defaults):
```bash
helm install todo-app phase-4/helm/todo-app/ \
  --set secrets.databaseUrl="postgresql://..." \
  --set secrets.openrouterApiKey="sk-..." \
  --set secrets.betterAuthSecret="..." \
  --set secrets.vapidPrivateKey="..." \
  --set secrets.vapidPublicKey="..."
```

### With overrides:
```bash
helm install todo-app phase-4/helm/todo-app/ \
  -f phase-4/helm/todo-app/values-dev.yaml \
  --set secrets.databaseUrl="postgresql://..." \
  --set backend.replicaCount=2
```

### Upgrade:
```bash
helm upgrade --atomic todo-app phase-4/helm/todo-app/ \
  --set backend.image.tag=v3.1.0
```

### Rollback:
```bash
helm rollback todo-app 1
```
