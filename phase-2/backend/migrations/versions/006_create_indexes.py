"""create indexes for performance

Revision ID: 006
Revises: 005
Create Date: 2026-01-11

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tasks table indexes for filtering and sorting
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_priority', 'tasks', ['priority'])
    op.create_index('idx_tasks_category_id', 'tasks', ['category_id'])
    op.create_index('idx_tasks_created_at', 'tasks', ['created_at'])

    # Composite indexes for common query patterns
    op.create_index('idx_tasks_user_status', 'tasks', ['user_id', 'status'])
    op.create_index('idx_tasks_user_priority', 'tasks', ['user_id', 'priority'])
    op.create_index('idx_tasks_user_created', 'tasks', ['user_id', 'created_at'])

    # Full-text search index (GIN) for title and description
    # This enables fast full-text search queries
    op.execute("""
        CREATE INDEX idx_tasks_fulltext ON tasks
        USING GIN (to_tsvector('english', title || ' ' || COALESCE(description, '')))
    """)

    # Categories table indexes
    op.create_index('idx_categories_user_id', 'categories', ['user_id'])
    op.create_index('idx_categories_is_system', 'categories', ['is_system'])

    # Tags table indexes
    op.create_index('idx_tags_user_id', 'tags', ['user_id'])

    # Task_tag table indexes for efficient joins
    op.create_index('idx_task_tag_task_id', 'task_tag', ['task_id'])
    op.create_index('idx_task_tag_tag_id', 'task_tag', ['tag_id'])


def downgrade() -> None:
    # Drop task_tag indexes
    op.drop_index('idx_task_tag_tag_id', table_name='task_tag')
    op.drop_index('idx_task_tag_task_id', table_name='task_tag')

    # Drop tags indexes
    op.drop_index('idx_tags_user_id', table_name='tags')

    # Drop categories indexes
    op.drop_index('idx_categories_is_system', table_name='categories')
    op.drop_index('idx_categories_user_id', table_name='categories')

    # Drop full-text search index
    op.drop_index('idx_tasks_fulltext', table_name='tasks')

    # Drop tasks composite indexes
    op.drop_index('idx_tasks_user_created', table_name='tasks')
    op.drop_index('idx_tasks_user_priority', table_name='tasks')
    op.drop_index('idx_tasks_user_status', table_name='tasks')

    # Drop tasks single-column indexes
    op.drop_index('idx_tasks_created_at', table_name='tasks')
    op.drop_index('idx_tasks_category_id', table_name='tasks')
    op.drop_index('idx_tasks_priority', table_name='tasks')
    op.drop_index('idx_tasks_status', table_name='tasks')
    op.drop_index('idx_tasks_user_id', table_name='tasks')
