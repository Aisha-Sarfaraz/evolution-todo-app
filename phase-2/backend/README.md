---
title: Todo API
emoji: ✅
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# Todo API - FastAPI Backend

A production-ready REST API for task management with authentication and user isolation.

## Features

- **Authentication**: JWT-based auth with Better Auth integration
- **User Isolation**: Each user can only access their own data
- **Task Management**: Full CRUD with search, filtering, sorting, and pagination
- **Categories**: Predefined system categories + custom user categories
- **Tags**: User-defined tags with many-to-many task relationships
- **Security**: Rate limiting, account lockout, audit logging

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API information |
| `GET /health` | Health check |
| `GET /docs` | Swagger UI documentation |
| `GET /redoc` | ReDoc documentation |
| `POST /api/auth/signup` | User registration |
| `POST /api/auth/signin` | User login |
| `GET /api/tasks` | List user tasks |
| `POST /api/tasks` | Create task |
| `GET /api/categories` | List categories |
| `GET /api/tags` | List user tags |

## Environment Variables

Configure these in Space Settings > Repository secrets:

- `DATABASE_URL` - PostgreSQL connection string
- `BETTER_AUTH_SECRET` - Auth secret (32+ chars)
- `BETTER_AUTH_URL` - Frontend URL
- `CORS_ORIGINS` - Allowed CORS origins

## Tech Stack

- **Framework**: FastAPI 0.115+
- **Database**: PostgreSQL with SQLModel ORM
- **Auth**: Better Auth / JWT
- **Server**: Uvicorn ASGI

## Local Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run with hot reload
python -c "from dotenv import load_dotenv; load_dotenv(); import uvicorn; uvicorn.run('src.main:app', host='0.0.0.0', port=8000, reload=True)"
```

## License

MIT
