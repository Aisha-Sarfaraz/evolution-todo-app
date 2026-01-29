"""create categories table

Revision ID: 002
Revises: 001
Create Date: 2026-01-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'categories',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=True),  # Nullable for system categories
        sa.Column('name', sa.VARCHAR(100), nullable=False),
        sa.Column('is_system', sa.BOOLEAN(), nullable=False, server_default='false'),
        sa.Column('color', sa.VARCHAR(7), nullable=True),  # Hex color code
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Foreign key to users table (with CASCADE on delete for user categories)
    op.create_foreign_key(
        'fk_categories_user_id',
        'categories', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

    # Unique constraint on user_id + LOWER(name) to prevent duplicate category names per user
    op.create_index(
        'idx_categories_user_name_unique',
        'categories',
        [sa.text('user_id'), sa.text('LOWER(name)')],
        unique=True
    )


def downgrade() -> None:
    op.drop_index('idx_categories_user_name_unique', table_name='categories')
    op.drop_constraint('fk_categories_user_id', 'categories', type_='foreignkey')
    op.drop_table('categories')
