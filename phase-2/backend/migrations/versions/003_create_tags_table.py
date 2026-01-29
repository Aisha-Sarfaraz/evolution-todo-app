"""create tags table

Revision ID: 003
Revises: 002
Create Date: 2026-01-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'tags',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.VARCHAR(50), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Foreign key to users table (CASCADE on delete)
    op.create_foreign_key(
        'fk_tags_user_id',
        'tags', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

    # Unique constraint on user_id + LOWER(name) for case-insensitive uniqueness
    op.create_index(
        'idx_tags_user_name_unique',
        'tags',
        [sa.text('user_id'), sa.text('LOWER(name)')],
        unique=True
    )


def downgrade() -> None:
    op.drop_index('idx_tags_user_name_unique', table_name='tags')
    op.drop_constraint('fk_tags_user_id', 'tags', type_='foreignkey')
    op.drop_table('tags')
