# Phase IV Quickstart: Local Kubernetes Deployment

**Feature Branch**: `003-kubernetes-deployment`
**Created**: 2026-02-07

---

## Prerequisites

| Tool | Version | Purpose | Install |
|------|---------|---------|---------|
| Docker Desktop | 4.53+ | Build container images | [docker.com/desktop](https://www.docker.com/products/docker-desktop/) |
| Minikube | 1.32+ | Local Kubernetes cluster | `winget install minikube` or [minikube.sigs.k8s.io](https://minikube.sigs.k8s.io/docs/start/) |
| kubectl | 1.28+ | Kubernetes CLI | Bundled with Docker Desktop or `winget install kubectl` |
| Helm | 3.14+ | Kubernetes package manager | `winget install Helm.Helm` or [helm.sh/docs/intro/install](https://helm.sh/docs/intro/install/) |
| kubectl-ai | latest | AI-assisted K8s ops (optional) | [github.com/sozercan/kubectl-ai](https://github.com/sozercan/kubectl-ai) |
| kagent | latest | K8s cluster intelligence (optional) | [github.com/kagent-dev/kagent](https://github.com/kagent-dev/kagent) |

**System Requirements**:
- CPU: 2+ cores available for Minikube
- RAM: 4GB+ available for Minikube
- Disk: 10GB+ free for Docker images
- Network: Internet access for Neon PostgreSQL

---

## Step 1: Start Minikube

```bash
# Start Minikube with Docker driver and sufficient resources
minikube start --driver=docker --cpus=2 --memory=4096

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

---

## Step 2: Build Docker Images

```bash
# Build backend image (multi-stage)
docker build -t todo-backend:latest -f phase-4/docker/backend.Dockerfile phase-3/backend/

# Build frontend image (Next.js standalone)
docker build -t todo-frontend:latest -f phase-4/docker/frontend.Dockerfile phase-3/frontend/

# Verify images exist
docker images | grep todo-
```

---

## Step 3: Load Images into Minikube

```bash
# Load locally-built images into Minikube's container runtime
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# Verify images are available in Minikube
minikube image list | grep todo-
```

---

## Step 4: Deploy with Helm

```bash
# Deploy the application (replace placeholders with real values)
helm install todo-app phase-4/helm/todo-app/ \
  --set secrets.databaseUrl="YOUR_NEON_DATABASE_URL" \
  --set secrets.openrouterApiKey="YOUR_OPENROUTER_API_KEY" \
  --set secrets.betterAuthSecret="YOUR_BETTER_AUTH_SECRET" \
  --set secrets.vapidPrivateKey="YOUR_VAPID_PRIVATE_KEY" \
  --set secrets.vapidPublicKey="YOUR_VAPID_PUBLIC_KEY"

# Verify deployment
kubectl get all -n todo-app
```

---

## Step 5: Access the Application

```bash
# Start Minikube tunnel for LoadBalancer services (run in separate terminal)
minikube tunnel

# Get the frontend external URL
kubectl get svc -n todo-app todo-frontend

# Or use minikube service command
minikube service todo-frontend -n todo-app --url
```

Open the displayed URL in your browser to access the Todo AI Chatbot.

---

## Common Operations

### Scale backend replicas
```bash
helm upgrade todo-app phase-4/helm/todo-app/ --set backend.replicaCount=2
# Or with kubectl-ai:
# kubectl-ai "scale the todo backend to 2 replicas in todo-app namespace"
```

### Check pod status
```bash
kubectl get pods -n todo-app
# Or with kubectl-ai:
# kubectl-ai "show me all pods in todo-app namespace"
```

### View logs
```bash
kubectl logs -n todo-app -l component=backend --tail=50
kubectl logs -n todo-app -l component=frontend --tail=50
```

### Rollback a failed upgrade
```bash
helm rollback todo-app 1
```

### Tear down
```bash
helm uninstall todo-app
minikube stop
```

---

## Troubleshooting

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| Pod stuck in `Pending` | `kubectl describe pod <name> -n todo-app` | Increase Minikube resources: `minikube stop && minikube start --cpus=4 --memory=8192` |
| Pod in `CrashLoopBackOff` | `kubectl logs <pod> -n todo-app` | Check env vars (Secret/ConfigMap), verify DB connectivity |
| `ImagePullBackOff` | Image not loaded in Minikube | Run `minikube image load todo-backend:latest` |
| Service not accessible | `kubectl get svc -n todo-app` | Ensure `minikube tunnel` is running |
| DB connection timeout | Readiness probe failing | Verify Neon DB URL and network access from Minikube |
| OOMKilled | Pod exceeds memory limit | Increase `resources.limits.memory` in values.yaml |

---

## Environment Variables Reference

### Backend (via ConfigMap + Secret)

| Variable | Source | Value |
|----------|--------|-------|
| `DATABASE_URL` | Secret | Neon PostgreSQL connection URL |
| `OPENROUTER_API_KEY` | Secret | OpenRouter API key |
| `BETTER_AUTH_SECRET` | Secret | JWT signing secret |
| `VAPID_PRIVATE_KEY` | Secret | Web push private key |
| `VAPID_PUBLIC_KEY` | Secret | Web push public key |
| `LOG_LEVEL` | ConfigMap | `INFO` |
| `LOG_FORMAT` | ConfigMap | `json` |
| `ALLOWED_ORIGINS` | ConfigMap | `http://localhost:3000` |
| `ENVIRONMENT` | ConfigMap | `development` |

### Frontend (baked into image at build time)

| Variable | Docker Build Arg | Value |
|----------|-----------------|-------|
| `NEXT_PUBLIC_API_URL` | `--build-arg` | `http://todo-backend.todo-app.svc.cluster.local:7860/api` |
| `NEXT_PUBLIC_AUTH_URL` | `--build-arg` | `http://localhost:3000` |
| `NEXT_PUBLIC_VAPID_PUBLIC_KEY` | `--build-arg` | VAPID public key |
| `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` | `--build-arg` | ChatKit domain key |
