# Database Migrations

This directory contains Alembic migrations for the Todo application database schema.

## Setup

1. **Configure Database Connection**:
   - Copy `.env.example` to `.env`
   - Set `DATABASE_URL` to your PostgreSQL connection string:
     ```
     DATABASE_URL=postgresql+asyncpg://username:password@host:port/database
     ```

2. **Run Migrations**:
   ```bash
   cd phase-2/backend
   alembic upgrade head
   ```

3. **Rollback Migrations** (if needed):
   ```bash
   alembic downgrade -1  # Rollback one migration
   alembic downgrade base  # Rollback all migrations
   ```

## Migration Files

| Revision | Description | Tables Created |
|----------|-------------|----------------|
| 001 | Create users table | users |
| 002 | Create categories table | categories |
| 003 | Create tags table | tags |
| 004 | Create tasks table | tasks |
| 005 | Create task_tag join table | task_tag |
| 006 | Create indexes | N/A (indexes only) |
| 007 | Insert system categories | N/A (data only) |

## Schema Overview

### Tables
- **users**: User accounts with authentication
- **categories**: Predefined system + user-created categories
- **tags**: User-created tags for task organization
- **tasks**: Main task entity (extended from Phase I)
- **task_tag**: Many-to-many relationship between tasks and tags

### Foreign Keys
- `tasks.user_id` → `users.id` (CASCADE on delete)
- `tasks.category_id` → `categories.id` (SET NULL on delete)
- `categories.user_id` → `users.id` (CASCADE on delete)
- `tags.user_id` → `users.id` (CASCADE on delete)
- `task_tag.task_id` → `tasks.id` (CASCADE on delete)
- `task_tag.tag_id` → `tags.id` (CASCADE on delete)

### Indexes
- Full-text search (GIN) on tasks.title + tasks.description
- Composite indexes on (user_id, status), (user_id, priority), (user_id, created_at)
- Single-column indexes on frequently filtered fields

## Prerequisites

- PostgreSQL 13+
- Python 3.13+
- Alembic 1.13+

## Note

**T016**: Migrations are ready for execution. Run `alembic upgrade head` once DATABASE_URL is configured.
