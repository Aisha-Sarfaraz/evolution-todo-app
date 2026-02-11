# Health Check Contract: Kubernetes Probes

**Feature Branch**: `003-kubernetes-deployment`
**Created**: 2026-02-07

---

## Backend Health Endpoints

### GET /health/live (Liveness Probe)

**Purpose**: Tells Kubernetes the process is alive. If this fails, K8s restarts the pod.

**Request**: `GET /health/live`
**Response (200)**:
```json
{
  "status": "alive",
  "service": "todo-chatbot-api",
  "version": "3.0.0"
}
```

**Behavior**:
- Does NOT check database connectivity
- Does NOT check external services (OpenRouter, Neon)
- Returns 200 if the FastAPI process is running
- Timeout: 2 seconds max

**Kubernetes Config**:
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 7860
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 2
  failureThreshold: 3
```

---

### GET /health/ready (Readiness Probe)

**Purpose**: Tells Kubernetes the pod is ready to serve traffic. If this fails, K8s removes the pod from Service endpoints.

**Request**: `GET /health/ready`

**Response (200 — Ready)**:
```json
{
  "status": "ready",
  "database": "connected"
}
```

**Response (503 — Not Ready)**:
```json
{
  "status": "not_ready",
  "database": "disconnected"
}
```

**Behavior**:
- Executes `SELECT 1` against the database to verify connectivity
- Returns 200 if database is reachable
- Returns 503 if database connection fails
- Timeout: 5 seconds max (includes DB round-trip)

**Kubernetes Config**:
```yaml
readinessProbe:
  httpGet:
    path: /health/ready
    port: 7860
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 5
  failureThreshold: 3
```

---

### GET /health (Legacy — Backward Compatibility)

**Purpose**: Existing endpoint from Phase III. Kept for backward compatibility with existing Docker HEALTHCHECK.

**Request**: `GET /health`
**Response (200)**:
```json
{
  "status": "healthy",
  "service": "todo-chatbot-api",
  "version": "3.0.0",
  "timestamp": "2026-02-07T12:00:00Z",
  "mcp": "embedded"
}
```

**Note**: Not used by Kubernetes probes. Used only by Docker HEALTHCHECK instruction.

---

## Frontend Health Endpoint

### GET /api/health (Liveness Probe)

**Purpose**: Next.js API route for frontend health check.

**Request**: `GET /api/health`
**Response (200)**:
```json
{
  "status": "ok",
  "service": "todo-frontend",
  "timestamp": "2026-02-07T12:00:00Z"
}
```

**Behavior**:
- Returns 200 if the Next.js server is running
- No backend or database dependency checks
- This is a new API route to be created at `phase-3/frontend/app/api/health/route.ts`

**Kubernetes Config**:
```yaml
livenessProbe:
  httpGet:
    path: /api/health
    port: 3000
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 2
  failureThreshold: 3
```

---

## Startup Probe (Backend Only)

**Purpose**: Allows slow startup (AI agent initialization, database connection pooling).

**Kubernetes Config**:
```yaml
startupProbe:
  httpGet:
    path: /health/live
    port: 7860
  periodSeconds: 5
  failureThreshold: 6  # 6 * 5s = 30s startup window
```

**Behavior**:
- Disables liveness and readiness probes until startup succeeds
- Prevents premature restarts during initialization
- After startup succeeds, liveness and readiness probes take over
