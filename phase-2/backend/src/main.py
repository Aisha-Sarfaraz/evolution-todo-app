"""FastAPI application entry point.

Phase 2 Backend - Full-Stack Todo Application.
"""

# Load environment variables before any other imports
from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from src.api.routes import (
    auth_router,
    profile_router,
    tasks_router,
    categories_router,
    tags_router,
)
from src.middleware import RateLimitMiddleware
from src.database import init_db, close_db


# OpenAPI tags with descriptions
OPENAPI_TAGS = [
    {
        "name": "authentication",
        "description": "User authentication endpoints: signup, signin, signout, token refresh, password reset.",
    },
    {
        "name": "profile",
        "description": "User profile management: view and update profile information.",
    },
    {
        "name": "tasks",
        "description": "Task management: create, read, update, delete tasks with filtering and search.",
    },
    {
        "name": "categories",
        "description": "Category management: system and custom categories for organizing tasks.",
    },
    {
        "name": "tags",
        "description": "Tag management: user-defined tags for labeling tasks.",
    },
    {
        "name": "health",
        "description": "Health check endpoint for monitoring.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="Todo API",
    description="""
## Full-Stack Todo Application API

A production-ready REST API for task management with authentication and user isolation.

### Features
- **Authentication**: JWT-based auth with access (1h) and refresh (7d) tokens
- **User Isolation**: Each user can only access their own tasks, categories, and tags
- **Task Management**: Full CRUD with search, filtering, sorting, and pagination
- **Categories**: Predefined system categories + custom user categories
- **Tags**: User-defined tags with many-to-many task relationships
- **Security**: Rate limiting (100 req/min), account lockout (5 attempts), audit logging

### Authentication
All endpoints except `/api/auth/signup`, `/api/auth/signin`, `/api/auth/verify-email`,
`/api/auth/reset-password-request`, and `/api/auth/reset-password` require authentication.

Include the JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### Error Responses
All errors follow a consistent format:
```json
{
  "error_code": "ERROR_CODE",
  "detail": "Human-readable message",
  "field": "field_name"  // optional, for validation errors
}
```
""",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=OPENAPI_TAGS,
    license_info={
        "name": "MIT",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware (100 requests/minute per user)
app.add_middleware(
    RateLimitMiddleware,
    window_seconds=60,
    max_requests=100,
    exclude_paths=["/health", "/docs", "/openapi.json", "/redoc", "/"],
)

# Include routers
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(tasks_router)
app.include_router(categories_router)
app.include_router(tags_router)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint (T144).

    Returns database connection status and application version.
    Returns 200 if healthy, 503 if database unreachable.
    """
    from fastapi.responses import JSONResponse
    from src.database import get_session

    health_status = {
        "status": "healthy",
        "version": "2.0.0",
        "database": "connected",
    }

    # Check database connection
    try:
        from sqlalchemy import text
        async for session in get_session():
            # Simple query to verify connection
            result = await session.execute(text("SELECT 1"))
            await session.close()
            break
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"
        health_status["error"] = str(e)
        return JSONResponse(content=health_status, status_code=503)

    return health_status


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Todo API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
    }


def custom_openapi():
    """Generate custom OpenAPI schema with security schemes."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=OPENAPI_TAGS,
    )

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT access token. Get token from /api/auth/signin endpoint.",
        }
    }

    # Add global security requirement (can be overridden per-endpoint)
    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
