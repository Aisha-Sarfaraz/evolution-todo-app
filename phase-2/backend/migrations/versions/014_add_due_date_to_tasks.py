"""add due_date column to tasks table

Revision ID: 014
Revises: 013
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '014'
down_revision = '013'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('due_date', sa.TIMESTAMP(timezone=True), nullable=True))

    # Composite index for date range queries
    op.create_index('ix_tasks_user_due_date', 'tasks', ['user_id', 'due_date'])


def downgrade() -> None:
    op.drop_index('ix_tasks_user_due_date', table_name='tasks')
    op.drop_column('tasks', 'due_date')
