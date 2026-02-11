# Feature Specification: Local Kubernetes Deployment — Cloud-Native Todo AI Chatbot

**Feature Branch**: `003-kubernetes-deployment`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Phase IV: Local Kubernetes deployment of the Phase III Todo AI Chatbot using Minikube, Helm Charts, Docker containerization, and AI-assisted DevOps tooling (Gordon, kubectl-ai, kagent)"

---

## Clarifications

### Session 2026-02-07

- Q: Should Phase IV use a single umbrella Helm chart or separate charts per service? -> A: Single umbrella chart. One chart deploys backend + frontend together. Simpler for Phase IV local deployment.
- Q: How many Kubernetes services should the spec define given MCP is embedded in the backend? -> A: 2 services (backend with embedded MCP + frontend). Matches current Phase III architecture. No code splitting.
- Q: How should the Next.js frontend be containerized? -> A: Next.js standalone mode with `output: "standalone"`. Keeps SSR and API routes working. Production-grade.

---

## User Scenarios & Testing *(mandatory)*

<!--
  NOTE: This is an INFRASTRUCTURE specification. User stories describe deployment
  operations from a DevOps/developer perspective, not end-user application features.
  The "actor" is a developer or DevOps engineer, not an application user.
  No new business features are added — Phase IV deploys the existing Phase III application.
-->

### User Story 1 - Docker Containerization (Priority: P1)

A developer must be able to build production-ready Docker images for both the backend (FastAPI + embedded MCP server) and frontend (Next.js standalone) services from the Phase III application code. Images must follow security best practices (non-root user, minimal base), include health check endpoints, and run locally with `docker run` before any Kubernetes deployment is attempted.

**Why this priority**: Foundation for all subsequent stories. Without working Docker images, Kubernetes deployment is impossible. This story validates that Phase III applications are container-compatible and produces the artifacts needed by P2-P6.

**Independent Test**: Developer runs `docker build` for both services, then `docker run` each container independently, verifies health check endpoints respond, and confirms the application serves traffic on expected ports.

**Acceptance Scenarios**:

1. **Given** Phase III backend source code with embedded MCP server, **When** developer builds the backend Docker image using the multi-stage Dockerfile, **Then** the build completes successfully, the final image is less than 500MB, and runs as non-root user (UID 1000)
2. **Given** the built backend image, **When** developer runs the container with required environment variables, **Then** the backend serves traffic on port 7860, the `/health` endpoint returns a healthy status, and the `/mcp` endpoint is accessible
3. **Given** Phase III frontend source code, **When** developer builds the frontend Docker image using Next.js standalone mode, **Then** the build completes successfully, the image is less than 300MB, and runs as non-root user
4. **Given** the built frontend image, **When** developer runs the container with the backend API URL configured, **Then** the frontend serves traffic on port 3000 and can communicate with the backend container
5. **Given** both containers running, **When** developer sends a chat message through the frontend, **Then** the message reaches the backend, the AI agent processes it, and the response is displayed in the chat UI
6. **Given** a backend container running, **When** the health check endpoint is called, **Then** it returns status "healthy" with service name and version within 2 seconds
7. **Given** Docker AI Agent (Gordon) is available, **When** developer asks Gordon to optimize the Dockerfile, **Then** Gordon suggests improvements for layer caching, image size reduction, or security hardening
8. **Given** Gordon is NOT available, **When** developer needs to build images, **Then** standard Docker CLI commands work without any dependency on Gordon

---

### User Story 2 - Minikube Deployment (Priority: P2)

A DevOps engineer must be able to deploy both containerized services to a local Minikube Kubernetes cluster using kubectl. All configuration must be externalized to ConfigMaps and Secrets. Services must be accessible from the host machine. The deployment must validate that the existing Phase III functionality works unchanged in a Kubernetes environment.

**Why this priority**: Proves Kubernetes compatibility. This is the MVP for Phase IV — the application runs on Kubernetes. Depends on P1 (working Docker images). All subsequent stories (Helm, probes, rollback) build on this foundation.

**Independent Test**: Engineer starts Minikube, applies Kubernetes manifests, all pods reach Running state, services are accessible via LoadBalancer, and a full chat conversation (create task, list tasks) works end-to-end through the Kubernetes-deployed application.

**Acceptance Scenarios**:

1. **Given** Minikube is installed and running with Docker driver, **When** engineer applies backend Deployment manifest, **Then** the backend pod starts, reaches Running state, and logs show successful startup
2. **Given** Minikube cluster running, **When** engineer applies frontend Deployment manifest, **Then** the frontend pod starts, reaches Running state, and connects to the backend service
3. **Given** both deployments running, **When** engineer applies Service manifests (LoadBalancer type), **Then** services are accessible from the host machine via `minikube tunnel` or `minikube service` commands
4. **Given** a ConfigMap containing non-sensitive configuration (API URLs, log level, environment name), **When** pods start, **Then** pods read configuration from the ConfigMap environment variables, not hardcoded values
5. **Given** a Secret containing sensitive data (database URL, JWT secret, API keys), **When** pods start, **Then** pods read secrets from the Secret resource, and secret values are NOT visible in pod specs or logs
6. **Given** resource requests and limits are defined (CPU: 250m request/500m limit, Memory: 256Mi request/512Mi limit), **When** pods are scheduled, **Then** Kubernetes respects resource boundaries and pods operate within limits
7. **Given** both services deployed and accessible, **When** engineer sends a chat message to create a task via the frontend, **Then** the full conversation cycle works: message sent, AI processes via embedded MCP tools, task created in Neon DB, confirmation displayed
8. **Given** kubectl-ai is available, **When** engineer runs `kubectl-ai "deploy the todo backend with 1 replica"`, **Then** kubectl-ai generates valid Kubernetes manifests that can be reviewed and applied
9. **Given** all resources are in the `todo-app` namespace, **When** engineer lists resources, **Then** all pods, services, configmaps, and secrets are isolated in the dedicated namespace

---

### User Story 3 - Helm Chart Packaging (Priority: P3)

A platform engineer must be able to deploy the entire application stack using a single Helm chart with configurable values. The chart must support multiple environments through values overrides, enable repeatable deployments, and provide a single-command deployment experience.

**Why this priority**: Helm is the standard Kubernetes package manager. Charts enable repeatable, parameterized deployments and are required for Phase V cloud portability. Depends on P2 (working K8s manifests).

**Independent Test**: Engineer runs `helm install todo-app ./helm/todo-app` on a clean Minikube cluster, all services come up healthy, and the application is fully functional. Changing `values.yaml` replicas from 1 to 2 and running `helm upgrade` scales the deployment.

**Acceptance Scenarios**:

1. **Given** a clean Minikube cluster with no existing deployments, **When** engineer runs `helm install todo-app ./helm/todo-app`, **Then** all Kubernetes resources (Deployments, Services, ConfigMaps, Secrets) are created and pods reach Running state
2. **Given** the Helm chart is installed, **When** engineer runs `helm list`, **Then** the release is listed with status "deployed" and correct chart version
3. **Given** the default `values.yaml` with 1 replica per service, **When** engineer installs the chart, **Then** exactly 1 pod per service is created with default resource limits
4. **Given** a `values-staging.yaml` with 2 replicas and different resource limits, **When** engineer runs `helm install -f values-staging.yaml`, **Then** 2 pods per service are created with the overridden resource limits
5. **Given** an installed release, **When** engineer modifies image tag in values and runs `helm upgrade`, **Then** pods are updated with the new image via rolling update strategy
6. **Given** the chart, **When** engineer examines `Chart.yaml`, **Then** it contains name, version (semantic versioning), appVersion, and description
7. **Given** the chart, **When** engineer examines `values.yaml`, **Then** all configurable parameters are documented with comments explaining each value
8. **Given** kubectl-ai is available, **When** engineer asks kubectl-ai to help generate Helm template values, **Then** kubectl-ai suggests valid configuration that can be reviewed and incorporated

---

### User Story 4 - Health Checks and Probes (Priority: P4)

A developer must implement Kubernetes-compatible health check endpoints that enable the cluster to manage pod lifecycle automatically. Liveness probes detect crashed processes, readiness probes gate traffic routing, and startup probes handle slow initialization.

**Why this priority**: Health probes are essential for production Kubernetes deployments. Without them, K8s cannot detect failures or manage traffic correctly. Depends on P2 (pods running in K8s).

**Independent Test**: Developer kills the backend database connection (simulating failure). The readiness probe fails, Kubernetes stops routing traffic to the pod. Once the connection recovers, the readiness probe passes and traffic resumes automatically.

**Acceptance Scenarios**:

1. **Given** backend pod is running and healthy, **When** Kubernetes calls the liveness probe endpoint, **Then** it returns HTTP 200 within the configured timeout, confirming the process is alive
2. **Given** backend pod is running and the database connection is active, **When** Kubernetes calls the readiness probe endpoint, **Then** it returns HTTP 200, confirming the pod is ready to receive traffic
3. **Given** backend pod is running but the database connection is lost, **When** Kubernetes calls the readiness probe endpoint, **Then** it returns HTTP 503, and Kubernetes removes the pod from service endpoints (no traffic routed)
4. **Given** backend pod startup takes time to initialize AI agent configuration, **When** Kubernetes evaluates startup probe, **Then** the startup probe allows up to 30 seconds before declaring failure, preventing premature restarts
5. **Given** frontend pod is running, **When** Kubernetes calls the frontend health endpoint, **Then** it returns HTTP 200 confirming the Next.js server is serving requests
6. **Given** a backend pod's liveness probe fails 3 consecutive times, **When** Kubernetes evaluates the pod state, **Then** Kubernetes automatically restarts the pod and logs the restart event
7. **Given** probe configurations in the Helm chart, **When** engineer reviews values.yaml, **Then** probe paths, intervals, timeouts, and failure thresholds are configurable via Helm values

---

### User Story 5 - Rollback and Resilience (Priority: P5)

A DevOps engineer must be able to roll back a failed deployment to the previous working version using Helm. Additionally, the application must demonstrate stateless resilience — pods can be killed and restarted without data loss because all state is in the external Neon database.

**Why this priority**: Rollback is a safety net for production deployments. Stateless validation proves cloud readiness for Phase V. Depends on P3 (Helm chart working) and P4 (probes detecting failures).

**Independent Test**: Engineer deploys a bad image version via `helm upgrade`, observes pod failure, runs `helm rollback`, and the previous working version is restored. Separately, engineer kills a pod mid-conversation, and the user can continue chatting after the replacement pod starts.

**Acceptance Scenarios**:

1. **Given** a working Helm release (v1), **When** engineer upgrades to a broken image (v2) and the pods fail readiness probes, **Then** `helm rollback todo-app 1` restores the previous working version within 60 seconds
2. **Given** the Helm chart uses `--atomic` flag, **When** an upgrade fails (pods don't become ready within timeout), **Then** Helm automatically rolls back to the previous release without manual intervention
3. **Given** a user has an active conversation with 10 messages, **When** the backend pod is deleted (simulating crash), **Then** Kubernetes creates a replacement pod, and the user can continue the conversation after the new pod starts (conversation persists in Neon DB)
4. **Given** the frontend pod is killed, **When** Kubernetes restarts it, **Then** the frontend loads with the user's session intact (authenticated via Better Auth JWT) and conversation history is displayed
5. **Given** `helm history todo-app` shows 3 revisions, **When** engineer reviews the history, **Then** each revision shows the chart version, app version, status, and timestamp
6. **Given** kagent is available, **When** engineer asks kagent to analyze cluster health after a rollback, **Then** kagent provides insights about pod restarts, resource usage, and deployment status

---

### User Story 6 - AI-Assisted DevOps Operations (Priority: P6)

A DevOps engineer should be able to use AI-assisted tools (Docker AI Agent Gordon, kubectl-ai, kagent) to accelerate common Kubernetes operations including image optimization, deployment generation, scaling, debugging, and cluster health analysis. These tools are optional accelerators — all operations must have manual CLI fallbacks.

**Why this priority**: Demonstrates AIOps capabilities. Lowest priority because AI tools are enhancement, not requirement. All previous stories work without AI tools. This story validates boundaries and documents where AI assistance adds value.

**Independent Test**: Engineer uses kubectl-ai to scale the backend to 2 replicas, uses kagent to check cluster health, and uses Gordon to optimize a Dockerfile. All AI suggestions are reviewed before applying. When AI tools are unavailable, engineer completes all tasks using standard CLI commands.

**Acceptance Scenarios**:

1. **Given** Gordon is available and the backend Dockerfile exists, **When** engineer asks Gordon to analyze the Dockerfile for optimization opportunities, **Then** Gordon provides specific suggestions (layer caching, smaller base image, multi-stage improvements) that the engineer can review and accept or reject
2. **Given** kubectl-ai is installed, **When** engineer runs `kubectl-ai "scale the backend to 2 replicas"`, **Then** kubectl-ai generates a valid kubectl command or manifest, displays it for review, and applies only after engineer confirms
3. **Given** kubectl-ai is installed, **When** engineer runs `kubectl-ai "check why the pods are failing"`, **Then** kubectl-ai inspects pod events, logs, and status to provide a diagnostic summary
4. **Given** kagent is available, **When** engineer asks kagent to analyze cluster health, **Then** kagent reports on pod status, resource utilization, and any issues detected across the namespace
5. **Given** kagent is available, **When** engineer asks kagent to optimize resource allocation, **Then** kagent suggests resource request/limit adjustments based on actual usage patterns
6. **Given** an AI tool suggests a destructive operation (delete pod, force-restart), **When** the suggestion is presented, **Then** the engineer must explicitly confirm before execution — AI tools must NOT auto-execute destructive operations
7. **Given** Gordon, kubectl-ai, or kagent is NOT available in the engineer's environment, **When** engineer needs to perform the same operations, **Then** equivalent manual CLI commands (docker build, kubectl scale, kubectl describe) achieve the same result
8. **Given** any AI tool operation, **When** the command is executed, **Then** the command and its output are logged for audit purposes

---

### Edge Cases

- **Image pull failure**: Minikube cannot pull image from local Docker daemon; engineer must run `eval $(minikube docker-env)` or use `minikube image load` to make images available
- **Port conflict**: Port 7860 or 3000 already in use on the host; Kubernetes Service uses NodePort or LoadBalancer to map to different host ports
- **Neon DB unreachable**: External database is down or network restricted; readiness probe fails, pods marked as not-ready, no traffic routed, clear error in logs
- **OOM kill**: Pod exceeds memory limit (512Mi); Kubernetes kills the pod with OOMKilled status, pod restarts automatically, event logged
- **Minikube resource exhaustion**: Cluster runs out of CPU/memory for scheduling; pods stay in Pending state with "Insufficient cpu/memory" event, engineer must increase Minikube resources or reduce pod requests
- **Secret misconfiguration**: Required Secret key missing; pod fails to start with "CreateContainerConfigError", clear error message in pod events
- **ConfigMap change**: ConfigMap updated but pods still running with old values; rolling restart required (`kubectl rollout restart`) unless using file-mounted ConfigMaps with auto-reload
- **Helm upgrade partial failure**: One service upgrades successfully but another fails; `--atomic` flag ensures all-or-nothing upgrade behavior
- **Concurrent Helm operations**: Two engineers run `helm upgrade` simultaneously; Helm's release lock prevents concurrent modifications
- **Stale Docker image cache**: Minikube uses cached old image instead of newly built one; engineer must use unique image tags (git SHA) or `imagePullPolicy: Always`
- **DNS resolution inside cluster**: Frontend pod cannot resolve backend service name; verify Kubernetes DNS (CoreDNS) is running and service names follow `<name>.<namespace>.svc.cluster.local` pattern
- **Startup probe timeout**: AI agent initialization takes longer than 30s; startup probe fails, pod restarted; engineer must increase `failureThreshold * periodSeconds` in probe config
- **Minikube tunnel interruption**: `minikube tunnel` process killed; LoadBalancer services lose external IP; tunnel must be restarted

---

## Requirements *(mandatory)*

### Functional Requirements

**Containerization (FR-001 to FR-015)**

- **FR-001**: System MUST provide a multi-stage Dockerfile for the backend service using a minimal base image, with a build stage for dependency installation and a production stage for runtime
- **FR-002**: System MUST provide a Dockerfile for the frontend service using Next.js standalone output mode, producing a self-contained Node.js server image
- **FR-003**: All Docker images MUST run as a non-root user (UID 1000) for security compliance
- **FR-004**: All Docker images MUST include a `.dockerignore` file excluding node_modules, .git, .env files, test files, and build artifacts to minimize image size and prevent secret leakage
- **FR-005**: Backend Docker image MUST expose port 7860 and include the embedded MCP server at the `/mcp` path
- **FR-006**: Frontend Docker image MUST expose port 3000 and accept the backend API URL as an environment variable
- **FR-007**: Backend Docker image MUST include a health check instruction that validates the `/health` endpoint responds with HTTP 200
- **FR-008**: All Docker images MUST use deterministic base image tags (e.g., `python:3.11-slim`, not `python:latest`) for reproducible builds
- **FR-009**: Docker images MUST support tagging with both semantic version (e.g., `v4.0.0`) and git commit SHA for traceability
- **FR-010**: System MUST set `PYTHONUNBUFFERED=1` and `PYTHONDONTWRITEBYTECODE=1` environment variables in Python-based images for container-friendly logging
- **FR-011**: Backend Dockerfile MUST copy and install dependencies in a separate layer before copying application code, enabling Docker layer caching for faster rebuilds
- **FR-012**: System SHOULD support Docker AI Agent (Gordon) for Dockerfile optimization, image analysis, and build troubleshooting when available
- **FR-013**: System MUST provide standard Docker CLI build and run commands as the primary method, with Gordon as an optional enhancement
- **FR-014**: All Docker images MUST have total build time under 5 minutes on a standard development machine (assuming warm cache for base images)
- **FR-015**: Backend Docker image MUST include database migration tooling (Alembic) and migration files for schema management during deployment

**Kubernetes Deployment (FR-016 to FR-035)**

- **FR-016**: System MUST define a Kubernetes Deployment for the backend service with configurable replica count, defaulting to 1 replica
- **FR-017**: System MUST define a Kubernetes Deployment for the frontend service with configurable replica count, defaulting to 1 replica
- **FR-018**: All Deployments MUST specify resource requests (CPU: 250m, Memory: 256Mi) and limits (CPU: 500m, Memory: 512Mi) per the project constitution
- **FR-019**: All Deployments MUST use a rolling update strategy with maxUnavailable=0 and maxSurge=1 to ensure zero-downtime updates
- **FR-020**: System MUST define a Kubernetes Service of type LoadBalancer for the frontend, making it accessible from the host machine
- **FR-021**: System MUST define a Kubernetes Service of type ClusterIP for the backend, making it accessible only within the cluster (frontend-to-backend communication)
- **FR-022**: System MUST define a ConfigMap containing all non-sensitive configuration: backend API URL, log level, environment name, frontend public URL
- **FR-023**: System MUST define a Secret containing all sensitive configuration: database connection URL, JWT secret key, OpenAI/OpenRouter API key, Better Auth secret
- **FR-024**: All pod containers MUST reference configuration from ConfigMaps and Secrets via environment variable injection, with zero hardcoded configuration values
- **FR-025**: System MUST define a liveness probe for the backend checking an HTTP endpoint that validates the process is alive, with 10-second interval and 3-failure threshold
- **FR-026**: System MUST define a readiness probe for the backend checking an HTTP endpoint that validates database connectivity and service readiness, with 5-second interval
- **FR-027**: System MUST define a startup probe for the backend allowing up to 30 seconds for initial startup (AI agent configuration, database connection pooling)
- **FR-028**: System MUST define a liveness probe for the frontend checking an HTTP health endpoint, with 10-second interval
- **FR-029**: All Kubernetes resources MUST be deployed in a dedicated `todo-app` namespace, isolated from other workloads
- **FR-030**: System MUST include a Namespace manifest that creates the `todo-app` namespace if it does not exist
- **FR-031**: Container images MUST be accessible to Minikube either via `minikube image load`, the Minikube Docker daemon (`eval $(minikube docker-env)`), or a local registry
- **FR-032**: All Deployments MUST set `imagePullPolicy: IfNotPresent` for local development (avoiding unnecessary pulls) with the ability to override to `Always` for CI/CD
- **FR-033**: System MUST define pod labels including `app`, `component`, and `version` for service discovery and monitoring
- **FR-034**: System MUST support graceful shutdown with `terminationGracePeriodSeconds` of at least 10 seconds, allowing in-flight requests to complete
- **FR-035**: System SHOULD support kubectl-ai for generating and validating Kubernetes manifests when the tool is available

**Helm Charts (FR-036 to FR-055)**

- **FR-036**: System MUST provide a single umbrella Helm chart that deploys both backend and frontend services in one release
- **FR-037**: The Helm chart MUST include a `Chart.yaml` with chart name, semantic version, app version matching the application release, and a human-readable description
- **FR-038**: The Helm chart MUST include a `values.yaml` file with all configurable parameters documented with inline comments
- **FR-039**: The `values.yaml` MUST organize parameters into logical groups: `global`, `backend`, `frontend`, and `database` sections
- **FR-040**: The Helm chart MUST support configurable replica counts per service via `values.yaml` (e.g., `backend.replicaCount: 1`)
- **FR-041**: The Helm chart MUST support configurable Docker image repository and tag per service via `values.yaml`
- **FR-042**: The Helm chart MUST support configurable resource requests and limits per service via `values.yaml`
- **FR-043**: The Helm chart MUST support environment-specific values files (e.g., `values-dev.yaml`, `values-staging.yaml`) for multi-environment deployment
- **FR-044**: The Helm chart MUST include templates for: Namespace, Deployments (backend, frontend), Services (backend, frontend), ConfigMap, and Secret
- **FR-045**: All Helm templates MUST use the standard naming convention: `{{ include "todo-app.fullname" . }}` for resource names
- **FR-046**: The Helm chart MUST support `helm install` for initial deployment and `helm upgrade` for updates, both producing the same final state (idempotent)
- **FR-047**: The Helm chart MUST support `helm rollback` to restore any previous revision
- **FR-048**: The Helm chart MUST support the `--atomic` flag for upgrades, automatically rolling back if the upgrade fails (pods not ready within timeout)
- **FR-049**: The Helm chart MUST include a `NOTES.txt` template that displays post-install instructions including how to access the application
- **FR-050**: The Helm chart MUST include a `helpers.tpl` file with reusable template functions (fullname, labels, selectors)
- **FR-051**: The Helm chart MUST include a `README.md` documenting all configurable values, deployment instructions, and troubleshooting steps
- **FR-052**: Secret values in the Helm chart MUST be configurable via values.yaml with base64 encoding handled in templates, or via `--set` flags at install time
- **FR-053**: The Helm chart MUST set default health check probe paths that match the implemented endpoints, configurable via values
- **FR-054**: The Helm chart version MUST follow semantic versioning (MAJOR.MINOR.PATCH) starting at 0.1.0
- **FR-055**: The Helm chart MUST pass `helm lint` and `helm template` validation without errors

**Database Connectivity (FR-056 to FR-063)**

- **FR-056**: The application MUST connect to the external Neon Serverless PostgreSQL database — the database is NOT deployed within Kubernetes
- **FR-057**: The database connection URL MUST be stored in a Kubernetes Secret and injected as an environment variable into backend pods
- **FR-058**: The backend service MUST validate database connectivity during startup and report connection status via the readiness probe
- **FR-059**: The backend service MUST use connection pooling (pool size configurable via environment variable, default 5) for efficient database access from multiple pod replicas
- **FR-060**: The backend service MUST handle transient database connection failures with retry logic (3 retries with exponential backoff starting at 1 second)
- **FR-061**: The backend service MUST run Alembic database migrations as part of the deployment process, either via an init container or a Helm pre-install/pre-upgrade hook
- **FR-062**: Database migration execution MUST be idempotent — running migrations multiple times produces the same result
- **FR-063**: The system MUST support different database connection URLs per environment (dev, staging, production) via Helm values overrides

**AI-Assisted DevOps (FR-064 to FR-075)**

- **FR-064**: System SHOULD support Docker AI Agent (Gordon) for intelligent Docker operations including Dockerfile analysis, build optimization suggestions, and container debugging
- **FR-065**: System SHOULD support kubectl-ai for natural language Kubernetes operations including deployment generation, scaling commands, and pod failure diagnosis
- **FR-066**: System SHOULD support kagent for cluster-level intelligence including health analysis, resource optimization recommendations, and observability insights
- **FR-067**: All AI-assisted tool suggestions MUST be presented to the engineer for review before execution — no auto-execution of AI-generated commands
- **FR-068**: All AI tool operations MUST have equivalent manual CLI commands documented as fallback when AI tools are unavailable
- **FR-069**: AI tools MUST NOT have access to Secret values or credentials — they may reference Secret names but not decrypt or display Secret data
- **FR-070**: AI tool command history MUST be logged (command input, AI suggestion, engineer decision to accept/reject) for audit and learning purposes
- **FR-071**: Gordon SHOULD be used for initial Dockerfile generation and optimization, with generated Dockerfiles reviewed and potentially modified before use
- **FR-072**: kubectl-ai SHOULD be used for exploratory operations (checking pod status, diagnosing failures) where natural language queries accelerate troubleshooting
- **FR-073**: kagent SHOULD be used for cluster-wide health assessments and resource optimization recommendations
- **FR-074**: System MUST function fully without any AI DevOps tools installed — all tools are OPTIONAL accelerators, not dependencies
- **FR-075**: When AI tools are used, the specification MUST document which tool was used for which operation, creating a traceable record of AI-assisted decisions

### Key Entities

<!--
  NOTE: These are infrastructure entities (deployment artifacts), not data model entities.
  Phase IV does not modify the Phase III data model.
-->

- **DockerImage**: A container artifact produced by building a Dockerfile. Each service (backend, frontend) has one image. Key attributes: base image, build stages (builder, production), exposed port, health check command, non-root user configuration, image tag (semantic version or git SHA). Backend image includes FastAPI application with embedded MCP server. Frontend image includes Next.js standalone build.

- **KubernetesDeployment**: A stateless workload specification for running pod replicas. Key attributes: replica count, pod template (container image, ports, environment variables, resource requests/limits), rolling update strategy (maxUnavailable, maxSurge), probe configurations (liveness, readiness, startup), and label selectors. One Deployment per service (backend, frontend).

- **KubernetesService**: A stable network endpoint for accessing pods. Key attributes: service type (ClusterIP for internal backend access, LoadBalancer for external frontend access), port mapping (service port to container port), and label selector matching the corresponding Deployment. Provides DNS-based service discovery within the cluster.

- **HelmChart**: A packaged Kubernetes application containing templates, default values, and metadata. Key attributes: Chart.yaml (name, version, appVersion), values.yaml (configurable parameters organized by service), templates directory (Deployment, Service, ConfigMap, Secret, Namespace manifests), helpers template (reusable functions), and NOTES.txt (post-install instructions). Single umbrella chart deploys the entire application stack.

- **HealthCheckEndpoint**: An HTTP endpoint exposed by each service for Kubernetes probe consumption. Key attributes: endpoint path (liveness vs readiness), HTTP response code (200 for healthy, 503 for unhealthy), response payload (status, service name, version, optional dependency checks), and timeout behavior. Backend exposes both liveness (process alive) and readiness (database connected) endpoints. Frontend exposes a basic liveness endpoint.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Both Docker images (backend and frontend) build successfully from source code, with the backend image under 500MB and the frontend image under 300MB
- **SC-002**: All containers start and pass health checks within 30 seconds of creation, as mandated by the project constitution
- **SC-003**: 100% of application configuration is externalized to ConfigMaps and Secrets — zero hardcoded environment-specific values in Docker images or code
- **SC-004**: A developer can deploy the complete application to a clean Minikube cluster using a single `helm install` command, with all services reaching healthy state within 2 minutes
- **SC-005**: Helm rollback to any previous revision completes within 60 seconds and restores the application to a fully functional state
- **SC-006**: Pod restart (deletion and recreation) does not result in data loss — conversations and tasks persist in the external database, and users can resume without re-authentication beyond session expiry
- **SC-007**: The Helm chart passes `helm lint` validation with zero errors and zero warnings
- **SC-008**: All pods operate within constitution-mandated resource limits (CPU 500m, Memory 512Mi) under normal load
- **SC-009**: The readiness probe correctly detects database connectivity loss and removes the pod from service endpoints within 15 seconds
- **SC-010**: A developer new to the project can deploy the entire stack by following the Helm chart README within 15 minutes, starting from a running Minikube cluster
- **SC-011**: Graceful shutdown completes within 10 seconds, allowing in-flight requests to finish before pod termination
- **SC-012**: Zero secrets are visible in plain text across all artifacts: Docker images, Kubernetes manifests, Helm templates, pod logs, and version control
- **SC-013**: Rolling updates achieve zero-downtime deployment — at least one healthy pod serves traffic throughout the update process
- **SC-014**: The entire Minikube deployment (both services, 1 replica each) consumes less than 2GB RAM and 2 CPU cores, ensuring it runs on standard developer machines
- **SC-015**: AI DevOps tools (when available) reduce time for common operations (Dockerfile optimization, pod debugging, cluster health check) compared to manual CLI equivalents

---

## Spec-Driven Infrastructure Research

### Can Spec-Driven Development Extend to Infrastructure?

Traditional Spec-Driven Development (SDD) focuses on application features: specifications define WHAT users need, plans define HOW to implement, and tasks break work into atomic units. Phase IV tests whether this methodology applies to infrastructure.

**Thesis**: Infrastructure artifacts (Dockerfiles, Kubernetes manifests, Helm charts) are themselves specifications — they declaratively describe the desired state of the system. Helm charts in particular function as "executable specifications" that define, version, and reproduce deployment configurations.

**Evidence**:
- Kubernetes manifests are declarative — they describe WHAT should exist, not HOW to create it
- Helm values.yaml files separate configuration (WHAT varies) from structure (HOW it's organized)
- `helm template` renders the specification without applying it, enabling review before execution
- `helm diff` shows the gap between current state and desired state, similar to spec-vs-implementation analysis
- GitOps workflows treat infrastructure specs as the source of truth, just as SDD treats feature specs

**Conclusion**: SDD naturally extends to infrastructure when infrastructure is defined declaratively. Phase IV validates this by following the full SDD workflow (spec -> plan -> tasks -> implement) for infrastructure artifacts.

### Helm Charts as Executable Specifications

Helm charts serve dual purposes in Phase IV:
1. **Specification**: `values.yaml` defines the deployment contract (replicas, resources, configuration)
2. **Implementation**: Templates render Kubernetes manifests from the specification
3. **Validation**: `helm lint` and `helm test` verify the specification is valid and the deployment works

This mirrors the SDD pattern: spec.md (values.yaml) -> plan.md (chart structure) -> tasks.md (template files) -> implementation (helm install).

### AI Agents as Infrastructure Operators

Phase IV uses three AI agents for infrastructure operations:
- **Claude Code**: Generates all infrastructure artifacts (Dockerfiles, manifests, Helm charts) from specifications
- **Gordon (Docker AI)**: Optimizes containerization decisions, suggests improvements
- **kubectl-ai / kagent**: Translates natural language to Kubernetes operations, provides cluster intelligence

These agents function as "intelligent operators" that can read specifications (manifests, charts) and execute or optimize them. The human engineer retains approval authority — AI suggests, human decides.

### Blueprint-Style Specifications

Phase IV suggests that future phases could formalize infrastructure specifications as "blueprints":
- **Docker Blueprint**: Base image policy, security requirements, size budgets, health check contracts
- **Kubernetes Blueprint**: Resource limits, probe requirements, namespace policy, RBAC rules
- **Helm Blueprint**: Chart structure standards, values organization, versioning policy
- **CI/CD Blueprint** (Phase V): Pipeline stages, quality gates, deployment approval workflow

These blueprints would complement feature specifications, ensuring infrastructure decisions are documented with the same rigor as business requirements.

---

## Assumptions & Constraints

### Technology Constraints (Fixed for Phase IV)

- Docker Desktop installed and running on the developer's machine
- Minikube installed with Docker driver support
- Helm 3 CLI installed
- kubectl CLI installed
- Database: Neon Serverless PostgreSQL (external, not deployed in K8s)
- Application: Phase III Todo AI Chatbot (read-only, no modifications to business logic)

### Assumptions

- Phase III application is operational and tested before Phase IV begins
- The developer has Docker Desktop 4.53+ for Gordon support (optional)
- kubectl-ai and kagent are installable via standard package managers (optional)
- Minikube cluster has at least 2 CPU cores and 4GB RAM allocated
- The developer's machine can reach the Neon PostgreSQL database (internet connectivity)
- Phase III backend health check at `/health` is functional and returns HTTP 200
- Phase III frontend can be configured to point to a different backend URL via environment variable
- Better Auth JWT tokens work across container restarts (stateless validation)

### Non-Goals

- Cloud Kubernetes deployment (AKS, GKE, DOKS) — deferred to Phase V
- CI/CD pipeline implementation — deferred to Phase V
- Monitoring, logging, and observability stack (Prometheus, Grafana, Loki) — deferred to Phase V
- Horizontal Pod Autoscaler (HPA) or auto-scaling policies — deferred to Phase V
- Ingress controller or custom domain configuration — deferred to Phase V
- In-cluster database deployment (PostgreSQL StatefulSet) — external Neon DB is used
- Service mesh (Istio, Linkerd, Dapr) — deferred to Phase V
- Container registry setup (Docker Hub, GCR, ACR) — images loaded directly to Minikube
- Multi-cluster deployment — single Minikube cluster only
- Infrastructure as Code (Terraform, Pulumi) — deferred to Phase V
- Network policies or pod security policies — deferred to Phase V
- Any new business features, UI changes, or API modifications to the Phase III application

---

## Dependencies

- **Phase III Application Code**: Phase IV containers package the Phase III backend (FastAPI + embedded MCP + AI agent) and frontend (Next.js). Application code is used read-only — no modifications to business logic
- **Phase III Health Check**: Backend `/health` endpoint (main.py:83-94) is the foundation for Kubernetes liveness probes. May need to be extended to separate `/health/live` and `/health/ready` endpoints
- **Phase II Dockerfile Pattern**: Multi-stage build pattern from `phase-2/backend/Dockerfile` serves as the reference for Phase IV backend Dockerfile optimization
- **Neon PostgreSQL Database**: External dependency. Phase IV pods connect to Neon DB via connection URL stored in Kubernetes Secret. Database availability directly affects readiness probe status
- **Better Auth**: Authentication tokens issued by Better Auth must work when the application runs in Kubernetes containers (no IP-based session validation that would break in K8s)
- **Docker Desktop**: Required for building images and running Minikube with Docker driver
- **Minikube**: Required for local Kubernetes cluster. Must support LoadBalancer services (via `minikube tunnel`)
- **Helm 3**: Required for chart-based deployment. Must support `install`, `upgrade`, `rollback`, `lint` commands
