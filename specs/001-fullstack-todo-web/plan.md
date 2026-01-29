# Phase II Technical Implementation Plan
## Full-Stack Todo Web Application

**Created**: 2026-01-11
**Status**: Ready for Implementation
**Phase**: II - Multi-User Web Application

---

## Executive Summary

This plan transforms the Phase I in-memory Python console Todo app into a production-grade, multi-user web application with secure authentication, persistent storage, and modern frontend/backend separation. The design **preserves Phase I's clean 3-layer architecture and all 10 Task domain invariants** while introducing multi-tenancy, RESTful API, and web UI.

**Key Deliverables**:
- Multi-user support with secure JWT authentication (Better Auth)
- RESTful API with 15+ endpoints (FastAPI)
- Modern web interface (Next.js 16 App Router)
- Persistent database storage (Neon PostgreSQL + SQLModel)
- Task organization (priorities, categories, tags)
- Full-text search, filtering, and sorting

---

## 1. Technology Stack Rationale

### Frontend: Next.js 16 App Router

**Why Next.js 16?**
- **Server Components by Default**: Reduces JavaScript bundle (<100KB), improves Lighthouse score (target: 90+)
- **Built-in Optimizations**: Code splitting, image optimization, font optimization
- **File-Based Routing**: Intuitive organization matching user flows (auth, dashboard, settings)
- **React Server Actions**: Simplifies form submissions without custom API routes

**Rejected Alternatives**:
- ~~Next.js Pages Router~~ (App Router provides better performance with server components)
- ~~Create React App~~ (Lacks SSR, routing, optimization features)

**Context7 Requirement**: Next.js Frontend Architect MUST use Context7 MCP (`/vercel/next.js`) for Next.js 16 best practices.

### Backend: FastAPI

**Why FastAPI?**
- **Async-First**: Native async/await for concurrent request handling (target: 50 concurrent users)
- **Auto OpenAPI Docs**: Generates Swagger UI at `/docs` (FR-069 requirement)
- **Pydantic Validation**: Type-safe request/response schemas with automatic validation
- **Performance**: Fastest Python web framework (p95 < 500ms target achievable)
- **Dependency Injection**: Built-in DI for database sessions, authentication

**Rejected Alternatives**:
- ~~Django REST Framework~~ (Synchronous, heavier ORM, slower)
- ~~Flask~~ (No async support, manual validation)
- ~~Express.js~~ (Would require rewriting Python domain logic)

### Database: SQLModel ORM + Neon Serverless PostgreSQL

**Why SQLModel + Neon?**
- **SQLModel = SQLAlchemy + Pydantic**: Single source of truth for domain models, database schemas, and API contracts
- **Type-Safe Queries**: Full type hints prevent runtime errors (mypy validation)
- **Async Engine**: Non-blocking database operations (SQLAlchemy 2.0)
- **Neon Serverless**: Auto-scaling connections, auto-pause (cost optimization), instant branching

**Rejected Alternatives**:
- ~~Django ORM~~ (Synchronous, tight Django coupling)
- ~~MongoDB~~ (Relational data model requires SQL JOIN queries)
- ~~AWS RDS~~ (Always-on pricing, no instant branching)

### Authentication: Better Auth + JWT

**Why Better Auth?**
- **Framework-Agnostic**: Works with any frontend + any backend (FastAPI via JWT validation)
- **Modern Auth Patterns**: Email/password, OAuth, magic links, email verification out-of-box
- **Secure by Default**: CSRF protection, secure cookies, bcrypt password hashing
- **Session Management**: Access tokens (1-hour) + refresh tokens (7-day) with automatic rotation
- **Minimal Backend Dependency**: Backend only validates JWT signature and claims

**Rejected Alternatives**:
- ~~NextAuth.js~~ (Tightly coupled to Next.js, hard to integrate with FastAPI)
- ~~Auth0/Clerk~~ (Third-party SaaS, vendor lock-in, cost)
- ~~Custom JWT~~ (Better Auth provides battle-tested security patterns)

**Context7 Requirement**: Better Auth Guardian MUST use Context7 MCP for latest Better Auth APIs.

---

## 2. Database Schema Design

### Schema Overview (5 Core Tables + 1 Join Table)

1. **users** - User accounts with authentication credentials
2. **tasks** - Extended Phase I Task entity with multi-user support
3. **categories** - Predefined system categories + user custom categories
4. **tags** - User-created tags for flexible organization
5. **task_tag** - Many-to-many join table for task-tag associations

### Table: users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt (10+ rounds)
    email_verified BOOLEAN DEFAULT FALSE NOT NULL,
    display_name VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_signin_at TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

**Key Design Decisions**:
- UUID primary key (prevents enumeration attacks, distributed-system-ready)
- Email unique constraint (single account per email)
- bcrypt password hashing (never store plain text)
- Email verification flag (prevents fake accounts)

### Table: tasks (Extended from Phase I)

```sql
CREATE TABLE tasks (
    -- Phase I fields (preserved)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,

    -- Phase II additions
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    priority VARCHAR(20) NOT NULL DEFAULT 'Medium',
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,

    -- Constraints
    CONSTRAINT tasks_status_valid CHECK (status IN ('pending', 'complete')),
    CONSTRAINT tasks_priority_valid CHECK (priority IN ('Low', 'Medium', 'High', 'Urgent')),
    CONSTRAINT tasks_title_not_empty CHECK (TRIM(title) <> ''),
    CONSTRAINT tasks_title_length CHECK (LENGTH(title) <= 200)
);

-- Performance Indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority);
CREATE INDEX idx_tasks_user_category ON tasks(user_id, category_id);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
CREATE INDEX idx_tasks_fulltext ON tasks USING GIN (to_tsvector('english', title || ' ' || description));
```

**Key Design Decisions**:
- **Phase I Preservation**: All 7 Phase I fields remain unchanged (`id`, `title`, `description`, `status`, `created_at`, `updated_at`, `completed_at`)
- **user_id Foreign Key**: Enforces user isolation, CASCADE DELETE removes user tasks when account deleted
- **priority Enum**: CHECK constraint enforces 4 valid values (Low/Medium/High/Urgent)
- **category_id Nullable**: Tasks can have 0 or 1 category, SET NULL prevents orphaned tasks
- **Full-Text Search Index (GIN)**: Enables sub-second search on 1000+ tasks (p95 < 2s target)
- **Composite Indexes**: `(user_id, status)` enables fast filtered queries without full table scans

### Table: categories

```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,  -- NULL for system categories
    name VARCHAR(100) NOT NULL,
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    color VARCHAR(7),  -- Hex color code
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT categories_name_unique_per_user UNIQUE (user_id, LOWER(name)),
    CONSTRAINT categories_system_no_user CHECK (NOT is_system OR user_id IS NULL)
);

CREATE INDEX idx_categories_user ON categories(user_id);
```

**Key Design Decisions**:
- **user_id Nullable**: `NULL` for system categories (Work, Personal, Shopping), `user_id` for custom categories
- **is_system Flag**: Prevents deletion of predefined categories
- **Case-Insensitive Uniqueness**: `UNIQUE (user_id, LOWER(name))` prevents "Work" and "work" duplicates

**Initial Data (8 System Categories)**:
```sql
INSERT INTO categories (user_id, name, is_system, color) VALUES
    (NULL, 'Work', TRUE, '#3B82F6'),
    (NULL, 'Personal', TRUE, '#10B981'),
    (NULL, 'Shopping', TRUE, '#F59E0B'),
    (NULL, 'Health', TRUE, '#EF4444'),
    (NULL, 'Fitness', TRUE, '#8B5CF6'),
    (NULL, 'Finance', TRUE, '#14B8A6'),
    (NULL, 'Education', TRUE, '#6366F1'),
    (NULL, 'Home', TRUE, '#EC4899');
```

### Table: tags

```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT tags_name_unique_per_user UNIQUE (user_id, LOWER(name))
);

CREATE INDEX idx_tags_user ON tags(user_id);
CREATE INDEX idx_tags_user_name ON tags(user_id, LOWER(name));
```

**Key Design Decisions**:
- **User-Scoped**: Each user has their own tag namespace
- **Case-Insensitive Uniqueness**: "urgent", "Urgent", "URGENT" are duplicates
- **50 Character Limit**: Shorter than categories (tags are quick labels)

### Table: task_tag (Join Table)

```sql
CREATE TABLE task_tag (
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    PRIMARY KEY (task_id, tag_id)
);

CREATE INDEX idx_task_tag_tag ON task_tag(tag_id);
```

**Key Design Decisions**:
- **Composite Primary Key**: Prevents duplicate associations
- **ON DELETE CASCADE**: Automatic cleanup when task or tag deleted
- **Reverse Index**: Enables fast "find all tasks with tag X" queries

### Row-Level Security (RLS)

**Defense-in-Depth Security**:
```sql
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

CREATE POLICY tasks_user_isolation ON tasks
    FOR ALL
    USING (user_id = current_setting('app.current_user_id')::UUID);
```

**Application Flow**:
1. Backend extracts `user_id` from JWT token
2. Backend sets PostgreSQL session variable: `SET SESSION app.current_user_id = <user_id>`
3. All queries automatically filtered by RLS policy
4. Even if application bug allows cross-user query, database blocks unauthorized access

---

## 3. API Endpoint Implementation Plan

### API Design Principles

- **RESTful Resource Organization**: Resources (`users`, `tasks`, `categories`, `tags`)
- **URL Structure**: `/api/{user_id}/{resource}[/{resource_id}][/action]`
- **User Isolation**: `{user_id}` in URL validated against JWT token `user_id` claim
- **Authentication**: All endpoints require `Authorization: Bearer <JWT>` header

### Authentication Endpoints (6 endpoints)

| Method | Endpoint | Purpose | Request | Response |
|--------|----------|---------|---------|----------|
| POST | `/api/auth/signup` | User registration | `{ email, password, password_confirm }` | 201 Created `{ user_id, email, message }` |
| POST | `/api/auth/verify-email` | Verify email with token | `{ token }` | 200 OK `{ message }` |
| POST | `/api/auth/signin` | User signin | `{ email, password }` | 200 OK `{ access_token, refresh_token, user }` |
| POST | `/api/auth/refresh` | Refresh access token | Refresh token from cookie | 200 OK `{ access_token }` |
| POST | `/api/auth/signout` | Sign out user | No body | 204 No Content |
| POST | `/api/auth/reset-password-request` | Request password reset | `{ email }` | 200 OK `{ message }` |
| POST | `/api/auth/reset-password` | Complete password reset | `{ token, new_password, new_password_confirm }` | 200 OK `{ message }` |

### Task Endpoints (6 endpoints)

| Method | Endpoint | Purpose | Query Params | Response |
|--------|----------|---------|--------------|----------|
| GET | `/api/{user_id}/tasks` | List all tasks | `search`, `status`, `priority`, `category`, `tags`, `created_after/before`, `sort_by`, `order` | 200 OK `{ tasks: Task[] }` |
| POST | `/api/{user_id}/tasks` | Create new task | N/A | 201 Created `{ task: Task }` |
| GET | `/api/{user_id}/tasks/{id}` | Get task details | N/A | 200 OK `{ task: Task }` |
| PUT | `/api/{user_id}/tasks/{id}` | Update task | N/A | 200 OK `{ task: Task }` |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task | N/A | 204 No Content |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion | N/A | 200 OK `{ task: Task }` |

**Query Parameters for GET /tasks** (Search, Filter, Sort):
- **Search**: `search=meeting` (full-text across title + description)
- **Filters**: `status=pending`, `priority=High,Urgent`, `category=<uuid>`, `tags=urgent,meeting`
- **Date Ranges**: `created_after=2026-01-01`, `created_before=2026-01-31`, `completed_after`, `completed_before`
- **Sort**: `sort_by=priority&order=desc` (priority, created_at, updated_at, title)

### Category Endpoints (3 endpoints)

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| GET | `/api/{user_id}/categories` | List all categories | 200 OK `{ categories: Category[] }` |
| POST | `/api/{user_id}/categories` | Create custom category | 201 Created `{ category: Category }` |
| DELETE | `/api/{user_id}/categories/{id}` | Delete custom category | 204 No Content |

### Tag Endpoints (4 endpoints)

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| GET | `/api/{user_id}/tags` | List all tags | 200 OK `{ tags: Tag[] }` |
| POST | `/api/{user_id}/tags` | Create new tag | 201 Created `{ tag: Tag }` |
| PUT | `/api/{user_id}/tags/{id}` | Rename tag | 200 OK `{ tag: Tag }` |
| DELETE | `/api/{user_id}/tags/{id}` | Delete tag | 204 No Content |

### User Isolation Enforcement (Critical Security)

**URL Parameter Validation** (All protected endpoints):
```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Extract and validate JWT token, return user_id."""
    token = credentials.credentials
    payload = jwt.decode(token, key=settings.BETTER_AUTH_SECRET, algorithms=["HS256"])
    return payload.get("sub")  # user_id

@router.get("/api/{user_id}/tasks")
async def list_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user)
):
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Cannot access other users' resources")

    tasks = await task_service.list_tasks(user_id)
    return {"tasks": tasks}
```

### Error Response Format (Consistent Across All Endpoints)

```json
{
  "error_code": "VALIDATION_ERROR | AUTHENTICATION_REQUIRED | FORBIDDEN | NOT_FOUND | INTERNAL_ERROR",
  "detail": "Human-readable error message",
  "field": "field_name (optional, for validation errors)",
  "request_id": "uuid (for 500 errors)"
}
```

**HTTP Status Code Mapping**:
- 200 OK - Success
- 201 Created - Resource created
- 204 No Content - Success (no response body)
- 400 Bad Request - Malformed JSON, missing headers
- 401 Unauthorized - Missing/invalid/expired JWT
- 403 Forbidden - URL user_id mismatch, system category deletion
- 404 Not Found - Resource doesn't exist (or cross-user access blocked)
- 422 Unprocessable Entity - Validation errors
- 429 Too Many Requests - Rate limit exceeded
- 500 Internal Server Error - Unexpected errors

---

## 4. Frontend Component Architecture

### Project Directory Structure (Phase II)

```
todo-app/
├── Phase-1/                       # Existing Phase I implementation (unchanged)
│   ├── src/
│   ├── tests/
│   └── pyproject.toml
└── phase-2/                       # NEW: Phase II web application
    ├── backend/                   # FastAPI backend
    │   ├── src/
    │   │   ├── api/
    │   │   │   ├── dependencies.py
    │   │   │   └── routes/
    │   │   │       ├── tasks.py
    │   │   │       ├── categories.py
    │   │   │       ├── tags.py
    │   │   │       └── auth.py
    │   │   ├── models/
    │   │   │   ├── task.py
    │   │   │   ├── user.py
    │   │   │   ├── category.py
    │   │   │   └── tag.py
    │   │   ├── services/
    │   │   ├── database.py
    │   │   └── main.py
    │   ├── tests/
    │   ├── pyproject.toml
    │   └── .env
    └── frontend/                  # Next.js 16 frontend
        ├── app/
        │   ├── (auth)/                    # Route group (auth flows)
        │   │   ├── signin/page.tsx        # Server component: /signin
        │   │   ├── signup/page.tsx        # Server component: /signup
        │   │   ├── verify-email/page.tsx  # Server component: /verify-email
        │   │   ├── reset-password/page.tsx
        │   │   └── layout.tsx             # Auth layout (centered form)
        │   ├── (dashboard)/               # Route group (protected routes)
        │   │   ├── tasks/page.tsx         # Server component: /tasks (task list)
        │   │   ├── categories/page.tsx
        │   │   ├── tags/page.tsx
        │   │   ├── profile/page.tsx
        │   │   └── layout.tsx             # Dashboard layout (sidebar nav)
        │   ├── api/auth/[...betterauth]/route.ts  # Better Auth route handler
        │   ├── layout.tsx                 # Root layout (global styles)
        │   └── page.tsx                   # Homepage (redirect to /tasks or /signin)
        ├── components/
        │   ├── auth/
        │   │   ├── signin-form.tsx        # Client component (form interactions)
        │   │   ├── signup-form.tsx        # Client component
        │   │   └── auth-provider.tsx      # Client component (Better Auth context)
        │   ├── tasks/
        │   │   ├── task-list.tsx          # Server component (renders cards)
        │   │   ├── task-card.tsx          # Server component
        │   │   ├── task-form.tsx          # Client component (create/edit)
        │   │   ├── task-filters.tsx       # Client component (search/filter UI)
        │   │   └── task-actions.tsx       # Client component (delete, complete)
        │   ├── ui/ (shadcn/ui)
        │   │   ├── button.tsx
        │   │   ├── input.tsx
        │   │   ├── form.tsx
        │   │   └── dialog.tsx
        │   └── layout/
        │       ├── header.tsx             # Server component
        │       ├── sidebar.tsx            # Server component
        │       └── footer.tsx             # Server component
        ├── lib/
        │   ├── api/
        │   │   ├── client.ts              # Fetch wrapper with JWT injection
        │   │   └── tasks.ts               # Task API methods
        │   ├── auth/
        │   │   └── better-auth.ts         # Better Auth client config
        │   ├── utils/
        │   │   ├── cn.ts                  # Tailwind CSS class merging
        │   │   └── date.ts                # Date formatting
        │   └── types/
        │       ├── task.ts                # TypeScript types (match backend schema)
        │       ├── category.ts
        │       └── tag.ts
        ├── public/
        │   └── icons/
        ├── proxy.ts                       # Next.js 16: Auth proxy (NOT middleware.ts)
        ├── package.json
        ├── tsconfig.json
        └── .env.local
```

### Server vs Client Components Strategy

**Server Components (Default)** - Zero JavaScript to client:
- Pages: `app/(dashboard)/tasks/page.tsx`
- Layouts: `app/(dashboard)/layout.tsx`
- Static content: `components/tasks/task-list.tsx`
- **Benefits**: Fast initial page load, SEO-friendly, zero JS bundle

**Client Components (`'use client'`)** - Interactivity required:
- Forms: `components/tasks/task-form.tsx` (validation, submission)
- Filters: `components/tasks/task-filters.tsx` (search input, dropdowns)
- Actions: `components/tasks/task-actions.tsx` (delete, complete buttons)
- **Benefits**: Rich interactivity, optimistic updates, immediate feedback

**Optimization Result**: Minimal JavaScript bundle (<100KB), fast Time to Interactive (TTI)

### API Client Design (Centralized Fetch Wrapper)

**lib/api/client.ts** - JWT injection + token refresh:
```typescript
export async function apiClient<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const session = await getSession();
  const token = session?.accessToken;

  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "Authorization": token ? `Bearer ${token}` : "",
      ...options?.headers,
    },
  });

  if (response.status === 401) {
    await fetch("/api/auth/refresh");  // Attempt token refresh
    // Retry original request (production: add retry logic)
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "API request failed");
  }

  return response.json();
}
```

**lib/api/tasks.ts** - Task API methods:
```typescript
export const taskApi = {
  async getTasks(userId: string, filters?: TaskFilters): Promise<Task[]>,
  async createTask(userId: string, data: CreateTaskRequest): Promise<Task>,
  async updateTask(userId: string, taskId: string, data: UpdateTaskRequest): Promise<Task>,
  async deleteTask(userId: string, taskId: string): Promise<void>,
  async toggleComplete(userId: string, taskId: string): Promise<Task>,
};
```

### State Management Strategy

**Approach**: Server State (TanStack Query) + Local State (React.useState)

**TanStack Query** - Data fetching, caching, optimistic updates:
```typescript
const { data: tasks } = useQuery({
  queryKey: ["tasks", userId],
  queryFn: () => taskApi.getTasks(userId),
});

const completeMutation = useMutation({
  mutationFn: (taskId: string) => taskApi.toggleComplete(userId, taskId),
  onMutate: async (taskId) => {
    // Optimistic update: UI changes immediately
    queryClient.setQueryData(["tasks", userId], (old: Task[]) =>
      old.map(task => task.id === taskId ? { ...task, status: "complete" } : task)
    );
  },
  onError: (err, taskId, context) => {
    // Rollback on error
    queryClient.setQueryData(["tasks", userId], context?.previousTasks);
  },
});
```

**Benefits**:
- Automatic caching (instant repeat visits)
- Optimistic updates (immediate UI feedback)
- Background refetching (data stays fresh)
- No custom Redux/Zustand needed

---

## 5. Authentication Flow Implementation

### Better Auth Configuration

**Backend JWT Validation Dependency** (`backend/src/api/dependencies.py`):
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Extract and validate JWT token, return user_id."""
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            key=settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"],
            issuer=settings.BETTER_AUTH_ISSUER,
        )

        if datetime.fromtimestamp(payload["exp"]) < datetime.now():
            raise HTTPException(status_code=401, detail="Token has expired")

        return payload.get("sub")  # user_id

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Endpoint Protection**:
```python
@router.get("/api/{user_id}/tasks")
async def list_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user)
):
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Cannot access other users' resources")

    tasks = await task_service.list_tasks(user_id)
    return {"tasks": tasks}
```

### Token Lifecycle

**Access Token (1-hour expiration)**:
- Short-lived token for API requests
- Storage: HTTP-only cookie or Authorization header
- Refresh: Frontend auto-refreshes using refresh token when expired

**Refresh Token (7-day expiration)**:
- Long-lived token for generating new access tokens
- Storage: HTTP-only cookie (XSS-safe, SameSite=Strict)
- Revocation: Invalidated on password change, signout

**Token Refresh Flow**:
1. Frontend makes API request with expired access token
2. Backend returns 401 with `error_code: TOKEN_EXPIRED`
3. Frontend calls `/api/auth/refresh` with refresh token cookie
4. Backend validates refresh token, issues new access token
5. Frontend retries original request with new access token

### Security Measures

**CSRF Protection**:
- SameSite cookies (`SameSite=Strict`)
- Better Auth auto-generated CSRF tokens
- Double Submit Cookie Pattern

**Password Hashing** (bcrypt, 10+ rounds):
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

**Token Invalidation on Password Change**:
- Update `users.password_hash`
- Invalidate all refresh tokens (add to blacklist or use token version field)
- Force re-authentication on all devices

**Rate Limiting** (100 requests/minute per user):
- FastAPI middleware with Redis cache
- Response: 429 Too Many Requests with `Retry-After` header

**Account Lockout** (5 failed signin attempts in 10 minutes):
- 15-minute lockout
- Redis counter with TTL
- Response: 403 Forbidden with lockout message

---

## 6. Test Strategy Definition

### Test Distribution

**Unit Tests** (80% coverage minimum):
- **Domain Layer**: Task entity invariants, validation, state transitions
- **Application Layer**: Service methods (CRUD, category/tag management)
- **Infrastructure Layer**: Repository implementations (database queries)
- **Examples**:
  - `test_task_title_validation()` (Phase I preserved)
  - `test_task_priority_enum_validation()` (New Phase II)
  - `test_category_name_uniqueness_case_insensitive()` (New Phase II)

**Integration Tests** (70% coverage minimum):
- **API Endpoints**: HTTP request/response contract testing
- **Database Operations**: Multi-table queries, foreign key constraints, cascade deletes
- **Authentication**: JWT validation, user isolation enforcement
- **Examples**:
  - `test_create_task_api_endpoint()` (Full request → database → response)
  - `test_cross_user_access_blocked()` (Security: User A cannot access User B's tasks)
  - `test_delete_category_sets_task_category_null()` (Cascade behavior)

**End-to-End Tests** (Critical user flows):
- Registration → verify email → signin → dashboard
- Create task → update → mark complete → delete
- Multi-user scenarios (User A and User B isolated task lists)
- Search & filter (create 20 tasks → search → filter → sort)
- **Framework**: Playwright (browser automation)

### Multi-User Testing Scenarios

**Scenario 1: Cross-User Access Blocked (Integration Test)**:
```python
@pytest.mark.integration
async def test_cross_user_task_access_blocked(db_session, auth_client):
    """Verify User B cannot access User A's tasks."""
    user_a = await create_user(db_session, email="user_a@example.com")
    user_b = await create_user(db_session, email="user_b@example.com")

    task_a = await create_task(db_session, user_id=user_a.id, title="User A Task")

    # User B attempts cross-user access via URL
    response = await auth_client.get(
        f"/api/{user_a.id}/tasks/{task_a.id}",
        headers={"Authorization": f"Bearer {user_b_jwt_token}"}
    )
    assert response.status_code == 403
    assert response.json()["error_code"] == "FORBIDDEN"
```

**Scenario 2: Data Isolation (Integration Test)**:
```python
@pytest.mark.integration
async def test_task_list_user_isolation(db_session, auth_client):
    """Verify GET /api/{user_id}/tasks returns only user's tasks."""
    user_a = await create_user(db_session, email="user_a@example.com")
    user_b = await create_user(db_session, email="user_b@example.com")

    for i in range(5):
        await create_task(db_session, user_id=user_a.id, title=f"User A Task {i}")

    for i in range(3):
        await create_task(db_session, user_id=user_b.id, title=f"User B Task {i}")

    # User A fetches tasks
    response = await auth_client.get(
        f"/api/{user_a.id}/tasks",
        headers={"Authorization": f"Bearer {user_a_jwt_token}"}
    )
    tasks = response.json()["tasks"]
    assert len(tasks) == 5
    assert all(task["user_id"] == user_a.id for task in tasks)
```

### Authentication Testing Scenarios

**Scenario: JWT Expiration Handling (Integration Test)**:
```python
@pytest.mark.integration
async def test_expired_jwt_token_rejected(auth_client):
    """Verify backend rejects expired access tokens."""
    expired_token = generate_jwt(
        user_id="user_123",
        exp=datetime.now() - timedelta(hours=1)
    )

    response = await auth_client.get(
        "/api/user_123/tasks",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    assert response.status_code == 401
    assert response.json()["error_code"] == "TOKEN_EXPIRED"
```

**Scenario: Password Change Invalidates Tokens (Integration Test)**:
```python
@pytest.mark.integration
async def test_password_change_invalidates_refresh_tokens(db_session, auth_client):
    """Verify password change invalidates all refresh tokens."""
    user = await create_user(db_session, email="user@example.com", password="OldPassword123!")

    # Sign in
    signin_response = await auth_client.post(
        "/api/auth/signin",
        json={"email": "user@example.com", "password": "OldPassword123!"}
    )
    old_refresh_token = signin_response.cookies.get("refresh_token")

    # Change password
    await auth_client.post(
        "/api/auth/reset-password",
        json={"token": "valid_reset_token", "new_password": "NewPassword456!"}
    )

    # Attempt token refresh with old refresh token
    response = await auth_client.post(
        "/api/auth/refresh",
        cookies={"refresh_token": old_refresh_token}
    )

    assert response.status_code == 401
```

### Data Integrity Validation

**Scenario: Cascade Delete Verification (Integration Test)**:
```python
@pytest.mark.integration
async def test_delete_user_cascades_to_tasks(db_session):
    """Verify deleting user cascades to all user's tasks."""
    user = await create_user(db_session, email="user@example.com")

    task_ids = []
    for i in range(10):
        task = await create_task(db_session, user_id=user.id, title=f"Task {i}")
        task_ids.append(task.id)

    # Delete user
    await db_session.delete(user)
    await db_session.commit()

    # Verify all tasks deleted (ON DELETE CASCADE)
    for task_id in task_ids:
        task = await db_session.get(Task, task_id)
        assert task is None
```

**Scenario: Tag Deletion Removes Associations (Integration Test)**:
```python
@pytest.mark.integration
async def test_delete_tag_removes_task_associations(db_session):
    """Verify deleting tag removes all task_tag associations."""
    user = await create_user(db_session, email="user@example.com")
    tag = await create_tag(db_session, user_id=user.id, name="urgent")

    task_ids = []
    for i in range(5):
        task = await create_task(db_session, user_id=user.id, title=f"Task {i}")
        await assign_tag_to_task(db_session, task_id=task.id, tag_id=tag.id)
        task_ids.append(task.id)

    # Delete tag
    await db_session.delete(tag)
    await db_session.commit()

    # Verify all task_tag associations deleted
    associations = await db_session.execute(
        select(TaskTag).where(TaskTag.tag_id == tag.id)
    )
    assert len(associations.scalars().all()) == 0

    # Verify tasks still exist
    for task_id in task_ids:
        task = await db_session.get(Task, task_id)
        assert task is not None
```

---

## Critical Files for Implementation

Based on this architectural design, the following files are **most critical** for Phase II implementation:

### 1. `phase-2/backend/src/api/dependencies.py`
**Reason**: Core authentication dependency - JWT validation, user_id extraction, URL parameter validation. All protected endpoints depend on this module. Incorrect implementation breaks security (user isolation).

**Key Responsibilities**:
- `get_current_user()` dependency (JWT validation)
- `validate_user_id_match()` dependency (URL user_id vs JWT user_id)
- Database session injection
- Rate limiting middleware integration

### 2. `phase-2/backend/src/models/task.py` (SQLModel)
**Reason**: Database schema definition for Task entity. Defines relationships (user, category, tags), constraints (CHECK, FOREIGN KEY), indexes (full-text search, composite). Schema correctness critical for data integrity and query performance.

**Key Responsibilities**:
- SQLModel class definition (matches Phase I domain model + new fields)
- Foreign key relationships (user_id, category_id)
- Many-to-many relationship with tags (via `task_tag` join table)
- Database indexes for performance

### 3. `phase-2/backend/src/api/routes/tasks.py`
**Reason**: Implements 6 task endpoints (list, create, get, update, delete, complete). Handles search, filter, sort query parameters. Contains most complex business logic (full-text search, multi-field filtering).

**Key Responsibilities**:
- Query parameter parsing (search, filters, sort)
- Database query construction (JOIN with categories/tags, WHERE clauses, ORDER BY)
- Response serialization (include nested category and tags)
- Error handling (validation, not found, unauthorized)

### 4. `phase-2/frontend/lib/api/client.ts`
**Reason**: Centralized API client with JWT token injection, automatic token refresh, error handling. All frontend API calls depend on this module. Incorrect implementation breaks authentication or causes silent failures.

**Key Responsibilities**:
- Authorization header injection (`Bearer <JWT>`)
- Token refresh on 401 Unauthorized
- Error parsing (extract `error_code`, `detail`)
- TypeScript type safety (generic `apiClient<T>`)

### 5. `phase-2/frontend/components/tasks/task-form.tsx`
**Reason**: Primary user interaction component - create and edit tasks. Implements form validation, category/tag selection, optimistic updates, error handling. Pattern to follow for other forms (category, tag, profile).

**Key Responsibilities**:
- React Hook Form integration (validation, submission)
- TanStack Query mutation (optimistic update, rollback on error)
- Category dropdown + tag multi-select
- Loading states, error messages, success feedback

### 6. `phase-2/frontend/proxy.ts` (Next.js 16 Authentication Proxy)
**Reason**: Handles authentication routing for protected routes. Redirects unauthenticated users to signin page. Critical for preventing unauthorized access to dashboard.

**Key Responsibilities**:
- Session validation using Better Auth
- Protected route detection (dashboard routes)
- Redirect logic for unauthenticated users
- **Note**: Next.js 16 uses `proxy.ts` (not `middleware.ts`)

---

## Verification Strategy (End-to-End Testing)

After implementation, verify the system works correctly by testing these critical user flows:

### Flow 1: User Registration & Authentication
1. Navigate to `/signup`
2. Enter email `test@example.com` and password `TestPassword123!`
3. Submit form → receive "Verification email sent" message
4. Click verification link in email → redirected to `/signin` with "Email verified" message
5. Sign in with credentials → redirected to `/tasks` dashboard
6. Verify JWT token stored in HTTP-only cookie (DevTools → Application → Cookies)

### Flow 2: Task Management (CRUD)
1. Authenticated user on `/tasks` dashboard
2. Click "Add Task" → modal opens
3. Enter title "Buy groceries", description "Get milk, eggs", priority "Medium", category "Shopping"
4. Submit → task appears at top of list with [  ] pending indicator
5. Click task → detail modal opens showing full information
6. Click "Edit" → update title to "Buy organic groceries", save → title updates in list
7. Click checkbox → task status changes to [✓] complete, completed_at timestamp displayed
8. Click "Delete" → confirmation dialog appears → confirm → task removed from list

### Flow 3: Multi-User Isolation
1. Open two browsers (Chrome + Firefox)
2. **Browser 1**: Sign in as User A (`user_a@example.com`)
3. **Browser 2**: Sign in as User B (`user_b@example.com`)
4. **Browser 1**: Create task "User A's private task"
5. **Browser 2**: Verify task list does NOT show User A's task
6. **Browser 2**: Open DevTools → Network tab → inspect `/api/{user_b_id}/tasks` response → verify only User B's tasks returned
7. **Browser 2**: Manually construct request to `GET /api/{user_a_id}/tasks` with User B's JWT → verify 403 Forbidden response

### Flow 4: Search, Filter, Sort
1. Create 20 tasks with varying priorities, categories, tags
2. Enter search query "meeting" → verify only tasks with "meeting" in title/description displayed
3. Apply filter "Priority: High" → verify only high-priority tasks displayed
4. Add filter "Category: Work" → verify only high-priority work tasks displayed
5. Select sort "Created: Newest First" → verify tasks ordered by created_at DESC
6. Clear filters → verify all 20 tasks displayed again

### Flow 5: Token Refresh
1. Sign in → note access token expiration time (1 hour from now)
2. Wait 1 hour (or manually modify token expiration in backend to 1 minute for faster testing)
3. Make API request (e.g., refresh task list)
4. Verify frontend automatically calls `/api/auth/refresh` (DevTools → Network tab)
5. Verify new access token received and original request retried successfully
6. Verify user remains signed in without interruption

---

## Performance Targets

Based on Phase II specification (SC-006 through SC-012):

| Operation | Target Latency (p95) | Notes |
|-----------|----------------------|-------|
| **API Read** (GET /tasks, GET /tasks/{id}) | < 500ms | For task lists up to 1000 items |
| **API Write** (POST/PUT/DELETE tasks) | < 1s | Including database commits and associations |
| **Search** | < 2s | Full-text search on 1000+ tasks (GIN index) |
| **Filter** | < 1s | Any filter combination on 1000+ tasks |
| **Sort** | < 500ms | 1000+ tasks (indexed columns) |
| **Concurrent Users** | 50+ | Mixed read/write operations without degradation |
| **Lighthouse Score** | ≥ 90 | Performance, Accessibility, Best Practices |

**Performance Optimization Strategies**:
- **Database Indexes**: GIN (full-text search), composite (user_id + status/priority), B-tree (sorting)
- **Async Operations**: FastAPI async + SQLAlchemy async engine (non-blocking I/O)
- **Server Components**: Next.js server components reduce client JS bundle (<100KB)
- **Caching**: TanStack Query client-side cache (instant repeat visits)
- **Connection Pooling**: Min 5, max 20 connections (prevents pool exhaustion)

---

## Migration from Phase I to Phase II

**Zero-Breaking-Change Migration Path**:

1. **Create PostgresRepository** implementing `RepositoryInterface`
2. **Update main.py** (ONE-LINE CHANGE):
   ```python
   # Phase I
   repository = MemoryRepository()

   # Phase II
   repository = PostgresRepository(db_session)
   ```
3. **Domain layer remains unchanged** (all 10 Task invariants preserved)
4. **Add user_id column** in persistence layer only (domain layer still single-user logic)
5. **No CLI or domain logic modifications required**

**Phase I Preservation Guarantee**:
- All 7 Phase I Task fields remain unchanged
- All 10 domain invariants enforced
- Phase I tests continue to pass (91 tests remain valid)
- Phase I domain model compatible with Phase II schema

---

## Out of Scope (Phase III+)

**Explicitly Deferred Features** (FR-096 to FR-100):
- ❌ Task due dates (deadline tracking)
- ❌ Recurring tasks (daily, weekly, monthly patterns)
- ❌ Task attachments (file uploads)
- ❌ Task collaboration (sharing, assignments, comments)
- ❌ Real-time sync (WebSockets, push notifications)

**Phase II Focus**: Multi-user support, authentication, task organization (priorities, categories, tags), search/filter/sort, persistent storage.

---

## Architectural Decision Summary

**Why This Architecture?**

1. **Preserves Phase I Foundation**: Task domain model unchanged (10 invariants preserved), clean 3-layer architecture extends to web stack
2. **Modern Best Practices**: Next.js 16 App Router (server components), FastAPI async, SQLModel (type-safe ORM), Better Auth (secure authentication)
3. **Performance-Optimized**: GIN indexes, composite indexes, async operations, server components
4. **Security-First**: JWT validation, row-level security (RLS), bcrypt hashing, rate limiting, CSRF protection, user isolation
5. **Scalable**: Stateless backend (horizontal scaling), serverless database (auto-scaling), event-driven architecture ready (Phase V)

**Trade-offs Acknowledged**:
- Better Auth (no vendor lock-in) vs Auth0/Clerk (more manual setup)
- SQLModel (Python backend preserved) vs Prisma (manual frontend types)
- Next.js App Router (performance) vs Pages Router (learning curve)
- Neon (serverless auto-scaling) vs AWS RDS (vendor dependency mitigated by PostgreSQL compatibility)

**Constitution Compliance**:
- ✅ Principle I (SDD): Plan follows spec.md (all 100 functional requirements)
- ✅ Principle III (TDD): Test strategy defined (unit 80%, integration 70%, E2E critical flows)
- ✅ Principle IV (Clean Separation): Frontend ↔ Backend (API contracts), Backend ↔ Domain (repository pattern)
- ✅ Principle VI (Security): Multi-user isolation (JWT + RLS), password hashing, rate limiting, CSRF, audit logging
- ✅ Principle VII (Code Quality): Type hints (mypy, TypeScript strict), docstrings, PEP 8 (ruff + black)
- ✅ Principle VIII (Performance): Async patterns, indexes, N+1 prevention, resource cleanup

---

**End of Plan**
