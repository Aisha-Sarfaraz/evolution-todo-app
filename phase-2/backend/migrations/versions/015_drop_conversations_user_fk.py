"""drop conversations user foreign key

Allow conversations to reference any user_id without FK constraint.
Better Auth uses 'user' table, app uses 'users' table - FK mismatch.

Revision ID: 015
Revises: 014
Create Date: 2026-02-05
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '015'
down_revision = '014'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the foreign key constraint that requires user_id to exist in users table
    op.drop_constraint('fk_conversations_user_id', 'conversations', type_='foreignkey')


def downgrade() -> None:
    # Re-create the foreign key constraint
    op.create_foreign_key(
        'fk_conversations_user_id',
        'conversations', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
