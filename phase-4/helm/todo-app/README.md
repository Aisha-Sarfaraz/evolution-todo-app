# Todo AI Chatbot - Helm Chart

**Chart Version:** 0.1.0 | **App Version:** 3.0.0

Local Kubernetes deployment of the Todo AI Chatbot with FastAPI backend (embedded MCP) and Next.js frontend.

## Prerequisites

- Docker Desktop (v29+)
- Minikube (v1.38+)
- Helm (v4+)
- kubectl (v1.35+)

## Quick Start

### 1. Build Docker Images

```bash
# Build both images
phase-4/scripts/build.sh

# Or build individually
docker build -t todo-backend:latest -f phase-4/docker/backend.Dockerfile phase-3/backend/
docker build -t todo-frontend:latest -f phase-4/docker/frontend.Dockerfile phase-2/frontend/
```

### 2. Start Minikube & Load Images

```bash
minikube start --driver=docker --memory=2048 --cpus=2
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
```

### 3. Deploy with Helm

```bash
helm install todo-app ./phase-4/helm/todo-app/ \
  --set secrets.databaseUrl="postgresql+asyncpg://..." \
  --set secrets.openrouterApiKey="sk-or-..." \
  --set secrets.betterAuthSecret="your-secret"
```

Or use the deploy script:

```bash
phase-4/scripts/deploy.sh \
  --database-url "postgresql+asyncpg://..." \
  --openrouter-api-key "sk-or-..." \
  --better-auth-secret "your-secret"
```

### 4. Access the Application

```bash
# In a separate terminal:
minikube tunnel

# Then visit:
# http://localhost:3000
```

### 5. Verify Health

```bash
kubectl get pods -n todo-app
kubectl exec -n todo-app deploy/todo-app-backend -- curl -s http://localhost:7860/health/ready
```

## Upgrade

```bash
# Scale backend
helm upgrade todo-app ./phase-4/helm/todo-app/ --set backend.replicaCount=2 --reuse-values

# Update image tag
helm upgrade todo-app ./phase-4/helm/todo-app/ --set backend.image.tag=v2.0.0 --reuse-values

# Atomic upgrade (auto-rollback on failure)
helm upgrade todo-app ./phase-4/helm/todo-app/ --atomic --timeout 60s --reuse-values
```

## Rollback

```bash
# View history
helm history todo-app

# Rollback to previous revision
helm rollback todo-app <REVISION>
```

## Teardown

```bash
phase-4/scripts/teardown.sh

# Or manually:
helm uninstall todo-app
kubectl delete namespace todo-app
```

## Configuration

### Environment Variables (ConfigMap)

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Application log level |
| `LOG_FORMAT` | `json` | Log format (json/text) |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | CORS allowed origins |
| `ENVIRONMENT` | `development` | Runtime environment |

### Secrets (passed via `--set`)

| Secret | Required | Description |
|--------|----------|-------------|
| `secrets.databaseUrl` | Yes | Neon PostgreSQL connection URL |
| `secrets.openrouterApiKey` | Yes | OpenRouter LLM API key |
| `secrets.betterAuthSecret` | Yes | Better Auth JWT signing secret |
| `secrets.vapidPrivateKey` | No | VAPID private key for web push |
| `secrets.vapidPublicKey` | No | VAPID public key for web push |

### Resource Limits

| Service | CPU Request/Limit | Memory Request/Limit |
|---------|-------------------|---------------------|
| Backend | 250m / 500m | 256Mi / 512Mi |
| Frontend | 100m / 250m | 128Mi / 256Mi |

### Health Probes

| Probe | Backend | Frontend |
|-------|---------|----------|
| Liveness | `/health/live` (10s interval) | `/api/health` (10s interval) |
| Readiness | `/health/ready` (5s interval) | N/A |
| Startup | `/health/live` (30s window) | N/A |

## Troubleshooting

```bash
# Check pod status
kubectl get pods -n todo-app

# View backend logs
kubectl logs -n todo-app -l app.kubernetes.io/component=backend -f

# View frontend logs
kubectl logs -n todo-app -l app.kubernetes.io/component=frontend -f

# Describe pod for events
kubectl describe pod -n todo-app -l app.kubernetes.io/component=backend

# Check service endpoints
kubectl get endpoints -n todo-app

# Enter pod shell
kubectl exec -it -n todo-app deploy/todo-app-backend -- /bin/bash
```

---

## AI-Assisted DevOps (AIOps)

The following AI tools are **optional accelerators** for DevOps operations. The application functions fully without them. All AI suggestions require human review before execution.

> **SAFETY NOTICE (FR-067, FR-069)**
>
> - All AI-generated commands MUST be reviewed by an engineer before execution
> - AI tools MUST NOT auto-execute destructive operations (delete pods, drop databases, scale to zero)
> - AI tools do NOT have access to Secret values or credentials
> - AI tools may reference Secret names but cannot decrypt or display Secret data
> - When AI tools are unavailable, use the manual CLI fallbacks documented below
> - All AI tool usage should be logged for audit and traceability (FR-070, FR-075)

### Gordon (Docker AI Agent)

Docker's built-in AI assistant for Dockerfile optimization, image analysis, and container debugging.

**Availability:** Included with Docker Desktop v29+ (`docker ai`)

#### Dockerfile Optimization (FR-064, FR-071)

```bash
# AI: Ask Gordon to analyze and optimize a Dockerfile
docker ai "Analyze phase-4/docker/backend.Dockerfile for optimization opportunities"

# AI: Ask about multi-stage build improvements
docker ai "How can I reduce the image size of my Python FastAPI backend?"

# AI: Debug a build failure
docker ai "My Docker build fails at the pip install step with psycopg2 error"
```

**Manual CLI Fallback:**

```bash
# Check image size
docker images todo-backend:latest --format "{{.Size}}"

# Inspect image layers
docker history todo-backend:latest

# Analyze image with dive (if installed)
dive todo-backend:latest

# Check for vulnerabilities
docker scout cves todo-backend:latest
```

#### Container Debugging (FR-064)

```bash
# AI: Debug a running container
docker ai "Why is my todo-backend container using high memory?"

# AI: Analyze container health
docker ai "My container health check is failing on port 7860"
```

**Manual CLI Fallback:**

```bash
# Check container resource usage
docker stats todo-backend

# View container logs
docker logs <container-id> --tail 50

# Inspect container config
docker inspect <container-id>

# Execute health check manually
docker exec <container-id> curl -s http://localhost:7860/health/live
```

### kubectl-ai (Kubernetes AI Assistant)

Natural language interface for Kubernetes operations — pod status, scaling, and failure diagnosis.

**Installation:** `kubectl krew install ai` (requires [krew](https://krew.sigs.k8s.io/))

#### Pod Status & Debugging (FR-065, FR-072)

```bash
# AI: Check pod status in natural language
kubectl ai "Show me all pods in the todo-app namespace that are not ready"

# AI: Diagnose pod failure
kubectl ai "Why is the todo-app-backend pod in CrashLoopBackOff?"

# AI: Get resource usage
kubectl ai "Which pods in todo-app are using the most memory?"
```

**Manual CLI Fallback:**

```bash
# List pods with status
kubectl get pods -n todo-app -o wide

# Describe pod for events and probe failures
kubectl describe pod -n todo-app -l app.kubernetes.io/component=backend

# View recent logs
kubectl logs -n todo-app deploy/todo-app-backend --tail=50

# Check resource consumption
kubectl top pods -n todo-app
```

#### Scaling Operations (FR-065)

```bash
# AI: Scale deployment
kubectl ai "Scale the todo-app backend to 3 replicas"

# AI: Autoscaling advice
kubectl ai "Should I add an HPA for the todo-app backend?"
```

**Manual CLI Fallback:**

```bash
# Scale manually
kubectl scale deployment/todo-app-backend -n todo-app --replicas=3

# Or via Helm
helm upgrade todo-app ./phase-4/helm/todo-app/ --set backend.replicaCount=3 --reuse-values
```

#### Debugging Network Issues (FR-065)

```bash
# AI: Diagnose connectivity
kubectl ai "The frontend can't reach the backend service on port 7860"
```

**Manual CLI Fallback:**

```bash
# Check services
kubectl get svc -n todo-app

# Check endpoints
kubectl get endpoints -n todo-app

# Test connectivity from frontend pod
kubectl exec -n todo-app deploy/todo-app-frontend -- wget -qO- http://todo-app-backend.todo-app.svc.cluster.local:7860/health/live
```

### kagent (Cluster Intelligence Agent)

Cluster-level health analysis, resource optimization, and observability insights.

**Installation:** See [kagent documentation](https://github.com/kagent-dev/kagent)

#### Cluster Health Assessment (FR-066, FR-073)

```bash
# AI: Overall cluster health
kagent "Give me a health summary of the todo-app namespace"

# AI: Resource optimization
kagent "Are my resource limits appropriate for the todo-app backend?"

# AI: Identify potential issues
kagent "What problems do you see in the todo-app deployment?"
```

**Manual CLI Fallback:**

```bash
# Cluster-wide resource usage
kubectl top nodes
kubectl top pods -n todo-app

# Check events for warnings
kubectl get events -n todo-app --sort-by='.lastTimestamp' --field-selector type=Warning

# Verify resource limits vs actual usage
kubectl describe deployment -n todo-app todo-app-backend | grep -A 6 "Limits:"
```

#### Resource Optimization (FR-066)

```bash
# AI: Right-sizing recommendations
kagent "Analyze CPU and memory usage patterns for todo-app pods and suggest optimized resource limits"
```

**Manual CLI Fallback:**

```bash
# Check current resource requests/limits
kubectl get deployment -n todo-app todo-app-backend -o jsonpath='{.spec.template.spec.containers[0].resources}'

# Monitor real usage over time
kubectl top pods -n todo-app --containers

# Compare limits vs values.yaml
helm get values todo-app
```

#### Observability Insights (FR-066)

```bash
# AI: Log analysis
kagent "Summarize the error patterns in todo-app backend logs from the last hour"
```

**Manual CLI Fallback:**

```bash
# Stream all backend logs
kubectl logs -n todo-app -l app.kubernetes.io/component=backend -f

# Filter for errors
kubectl logs -n todo-app deploy/todo-app-backend --since=1h | grep -i error

# Check probe failures in events
kubectl get events -n todo-app --field-selector reason=Unhealthy
```

---

## Architecture

```
                    ┌─────────────────────────────┐
                    │       minikube cluster       │
                    │                              │
  minikube tunnel   │  ┌────────────────────────┐  │
  ───────────────►  │  │  todo-app namespace     │  │
  http://localhost   │  │                        │  │
  :3000             │  │  ┌──────────────────┐  │  │
                    │  │  │ frontend (Next.js)│  │  │
                    │  │  │ LoadBalancer:3000 │  │  │
                    │  │  └──────────────────┘  │  │
                    │  │           │             │  │
                    │  │  ┌──────────────────┐  │  │       ┌──────────────┐
                    │  │  │ backend (FastAPI) │──┼──┼──────►│ Neon         │
                    │  │  │ ClusterIP:7860   │  │  │       │ PostgreSQL   │
                    │  │  │ + embedded MCP   │──┼──┼──────►│ (external)   │
                    │  │  └──────────────────┘  │  │       └──────────────┘
                    │  │                        │  │
                    │  │  ConfigMap + Secret     │  │
                    │  └────────────────────────┘  │
                    └─────────────────────────────┘
```
