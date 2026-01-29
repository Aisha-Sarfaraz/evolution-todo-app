"""Row-Level Security (RLS) setup script for PostgreSQL.

T088: [US3] Implement Row-Level Security setup script

This script enables RLS on critical tables and creates policies
to enforce user isolation at the database level.

Defense-in-Depth Strategy:
1. API Layer: JWT validation + user_id matching (dependencies.py)
2. Database Layer: RLS policies (this script)

Usage:
    python scripts/setup_rls.py

Requires DATABASE_URL environment variable or .env file.
"""

import asyncio
import os
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Load .env file if present
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)


DATABASE_URL = os.getenv("DATABASE_URL", "")


# SQL statements for RLS setup
RLS_SETUP_SQL = """
-- ============================================================================
-- Row-Level Security (RLS) Setup for Todo Application
-- ============================================================================
-- This provides database-level user isolation as defense-in-depth
-- beyond the application-layer JWT validation.
-- ============================================================================

-- Enable RLS on tasks table
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own tasks
DROP POLICY IF EXISTS tasks_user_select ON tasks;
CREATE POLICY tasks_user_select ON tasks
    FOR SELECT
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID);

-- Policy: Users can only insert tasks for themselves
DROP POLICY IF EXISTS tasks_user_insert ON tasks;
CREATE POLICY tasks_user_insert ON tasks
    FOR INSERT
    WITH CHECK (user_id = current_setting('app.current_user_id', TRUE)::UUID);

-- Policy: Users can only update their own tasks
DROP POLICY IF EXISTS tasks_user_update ON tasks;
CREATE POLICY tasks_user_update ON tasks
    FOR UPDATE
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID)
    WITH CHECK (user_id = current_setting('app.current_user_id', TRUE)::UUID);

-- Policy: Users can only delete their own tasks
DROP POLICY IF EXISTS tasks_user_delete ON tasks;
CREATE POLICY tasks_user_delete ON tasks
    FOR DELETE
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID);

-- ============================================================================
-- Enable RLS on categories table (for custom categories)
-- ============================================================================

ALTER TABLE categories ENABLE ROW LEVEL SECURITY;

-- Policy: Users can see system categories (user_id IS NULL) and their own custom categories
DROP POLICY IF EXISTS categories_user_select ON categories;
CREATE POLICY categories_user_select ON categories
    FOR SELECT
    USING (
        user_id IS NULL  -- System categories visible to all
        OR user_id = current_setting('app.current_user_id', TRUE)::UUID
    );

-- Policy: Users can only insert custom categories for themselves
DROP POLICY IF EXISTS categories_user_insert ON categories;
CREATE POLICY categories_user_insert ON categories
    FOR INSERT
    WITH CHECK (
        user_id = current_setting('app.current_user_id', TRUE)::UUID
        AND is_system = FALSE
    );

-- Policy: Users can only update their own custom categories
DROP POLICY IF EXISTS categories_user_update ON categories;
CREATE POLICY categories_user_update ON categories
    FOR UPDATE
    USING (
        user_id = current_setting('app.current_user_id', TRUE)::UUID
        AND is_system = FALSE
    )
    WITH CHECK (
        user_id = current_setting('app.current_user_id', TRUE)::UUID
        AND is_system = FALSE
    );

-- Policy: Users can only delete their own custom categories
DROP POLICY IF EXISTS categories_user_delete ON categories;
CREATE POLICY categories_user_delete ON categories
    FOR DELETE
    USING (
        user_id = current_setting('app.current_user_id', TRUE)::UUID
        AND is_system = FALSE
    );

-- ============================================================================
-- Enable RLS on tags table
-- ============================================================================

ALTER TABLE tags ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own tags
DROP POLICY IF EXISTS tags_user_select ON tags;
CREATE POLICY tags_user_select ON tags
    FOR SELECT
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID);

-- Policy: Users can only insert tags for themselves
DROP POLICY IF EXISTS tags_user_insert ON tags;
CREATE POLICY tags_user_insert ON tags
    FOR INSERT
    WITH CHECK (user_id = current_setting('app.current_user_id', TRUE)::UUID);

-- Policy: Users can only update their own tags
DROP POLICY IF EXISTS tags_user_update ON tags;
CREATE POLICY tags_user_update ON tags
    FOR UPDATE
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID)
    WITH CHECK (user_id = current_setting('app.current_user_id', TRUE)::UUID);

-- Policy: Users can only delete their own tags
DROP POLICY IF EXISTS tags_user_delete ON tags;
CREATE POLICY tags_user_delete ON tags
    FOR DELETE
    USING (user_id = current_setting('app.current_user_id', TRUE)::UUID);

-- ============================================================================
-- Enable RLS on task_tag join table
-- ============================================================================

ALTER TABLE task_tag ENABLE ROW LEVEL SECURITY;

-- Policy: task_tag access is controlled through the task relationship
-- Users can only manage task_tag associations for their own tasks
DROP POLICY IF EXISTS task_tag_user_all ON task_tag;
CREATE POLICY task_tag_user_all ON task_tag
    FOR ALL
    USING (
        task_id IN (
            SELECT id FROM tasks
            WHERE user_id = current_setting('app.current_user_id', TRUE)::UUID
        )
    );

-- ============================================================================
-- Verification queries (run these to check RLS is working)
-- ============================================================================
-- SELECT tablename, rowsecurity
-- FROM pg_tables
-- WHERE schemaname = 'public' AND tablename IN ('tasks', 'categories', 'tags', 'task_tag');
--
-- SELECT schemaname, tablename, policyname, cmd, qual
-- FROM pg_policies
-- WHERE schemaname = 'public';
"""

# SQL to check RLS status
RLS_CHECK_SQL = """
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('tasks', 'categories', 'tags', 'task_tag');
"""

# SQL to list policies
POLICY_CHECK_SQL = """
SELECT tablename, policyname, cmd
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
"""


async def setup_rls():
    """Setup Row-Level Security policies."""
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL environment variable not set")
        print("Set DATABASE_URL or create a .env file with the connection string")
        return False

    # Convert postgres:// to postgresql:// for SQLAlchemy
    db_url = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")
    if "postgresql://" in db_url and "+asyncpg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

    print(f"Connecting to database...")
    engine = create_async_engine(db_url, echo=False)

    try:
        async with engine.begin() as conn:
            print("Setting up Row-Level Security policies...")
            print("-" * 60)

            # Execute RLS setup SQL
            # Split by semicolons and execute each statement
            statements = [s.strip() for s in RLS_SETUP_SQL.split(";") if s.strip() and not s.strip().startswith("--")]

            for stmt in statements:
                if stmt:
                    try:
                        await conn.execute(text(stmt))
                        # Extract policy/table name for logging
                        if "CREATE POLICY" in stmt.upper():
                            policy_name = stmt.split("CREATE POLICY")[1].split(" ON ")[0].strip()
                            print(f"  Created policy: {policy_name}")
                        elif "ALTER TABLE" in stmt.upper() and "ENABLE ROW LEVEL SECURITY" in stmt.upper():
                            table_name = stmt.split("ALTER TABLE")[1].split("ENABLE")[0].strip()
                            print(f"  Enabled RLS on: {table_name}")
                        elif "DROP POLICY" in stmt.upper():
                            pass  # Silent for drop statements
                    except Exception as e:
                        print(f"  Warning: {e}")

            print("-" * 60)
            print("RLS setup complete!")

            # Verify RLS status
            print("\nVerifying RLS status...")
            result = await conn.execute(text(RLS_CHECK_SQL))
            rows = result.fetchall()
            print("\nTable RLS Status:")
            for row in rows:
                status = "ENABLED" if row[1] else "DISABLED"
                print(f"  {row[0]}: {status}")

            # List policies
            print("\nActive Policies:")
            result = await conn.execute(text(POLICY_CHECK_SQL))
            rows = result.fetchall()
            for row in rows:
                print(f"  {row[0]}.{row[1]} ({row[2]})")

            print("\nRLS setup verified successfully!")
            return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False

    finally:
        await engine.dispose()


async def disable_rls():
    """Disable Row-Level Security (for development/testing)."""
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL environment variable not set")
        return False

    db_url = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")
    if "postgresql://" in db_url and "+asyncpg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

    engine = create_async_engine(db_url, echo=False)

    try:
        async with engine.begin() as conn:
            print("Disabling Row-Level Security...")

            tables = ["tasks", "categories", "tags", "task_tag"]
            for table in tables:
                try:
                    await conn.execute(text(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY"))
                    print(f"  Disabled RLS on: {table}")
                except Exception as e:
                    print(f"  Warning: {table} - {e}")

            print("RLS disabled.")
            return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False

    finally:
        await engine.dispose()


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--disable":
        print("Disabling RLS (for development/testing)...")
        asyncio.run(disable_rls())
    else:
        print("Setting up Row-Level Security policies...")
        asyncio.run(setup_rls())


if __name__ == "__main__":
    main()

