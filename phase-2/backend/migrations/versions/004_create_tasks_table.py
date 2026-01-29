"""create tasks table

Revision ID: 004
Revises: 003
Create Date: 2026-01-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'tasks',
        # Phase I attributes (preserved)
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('title', sa.VARCHAR(200), nullable=False),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column('status', sa.VARCHAR(20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),

        # Phase II new attributes
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('priority', sa.VARCHAR(20), nullable=False, server_default='Medium'),
        sa.Column('category_id', UUID(as_uuid=True), nullable=True),

        # CHECK constraints for status and priority enums
        sa.CheckConstraint("status IN ('pending', 'complete')", name='chk_task_status'),
        sa.CheckConstraint("priority IN ('Low', 'Medium', 'High', 'Urgent')", name='chk_task_priority'),
    )

    # Foreign key to users table (CASCADE on delete)
    op.create_foreign_key(
        'fk_tasks_user_id',
        'tasks', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

    # Foreign key to categories table (SET NULL on delete)
    op.create_foreign_key(
        'fk_tasks_category_id',
        'tasks', 'categories',
        ['category_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_tasks_category_id', 'tasks', type_='foreignkey')
    op.drop_constraint('fk_tasks_user_id', 'tasks', type_='foreignkey')
    op.drop_table('tasks')
