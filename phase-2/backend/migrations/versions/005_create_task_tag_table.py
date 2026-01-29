"""create task_tag join table

Revision ID: 005
Revises: 004
Create Date: 2026-01-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'task_tag',
        sa.Column('task_id', UUID(as_uuid=True), nullable=False),
        sa.Column('tag_id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # Composite primary key
        sa.PrimaryKeyConstraint('task_id', 'tag_id', name='pk_task_tag'),
    )

    # Foreign key to tasks table (CASCADE on delete)
    op.create_foreign_key(
        'fk_task_tag_task_id',
        'task_tag', 'tasks',
        ['task_id'], ['id'],
        ondelete='CASCADE'
    )

    # Foreign key to tags table (CASCADE on delete)
    op.create_foreign_key(
        'fk_task_tag_tag_id',
        'task_tag', 'tags',
        ['tag_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('fk_task_tag_tag_id', 'task_tag', type_='foreignkey')
    op.drop_constraint('fk_task_tag_task_id', 'task_tag', type_='foreignkey')
    op.drop_table('task_tag')
