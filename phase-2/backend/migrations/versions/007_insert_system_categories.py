"""insert system categories

Revision ID: 007
Revises: 006
Create Date: 2026-01-11

"""
from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Insert predefined system categories (user_id=NULL, is_system=true)
    system_categories = [
        {'id': uuid.uuid4(), 'name': 'Work', 'color': '#3B82F6', 'is_system': True},  # Blue
        {'id': uuid.uuid4(), 'name': 'Personal', 'color': '#8B5CF6', 'is_system': True},  # Purple
        {'id': uuid.uuid4(), 'name': 'Shopping', 'color': '#10B981', 'is_system': True},  # Green
        {'id': uuid.uuid4(), 'name': 'Health', 'color': '#EF4444', 'is_system': True},  # Red
        {'id': uuid.uuid4(), 'name': 'Fitness', 'color': '#F59E0B', 'is_system': True},  # Orange
        {'id': uuid.uuid4(), 'name': 'Finance', 'color': '#14B8A6', 'is_system': True},  # Teal
        {'id': uuid.uuid4(), 'name': 'Education', 'color': '#6366F1', 'is_system': True},  # Indigo
        {'id': uuid.uuid4(), 'name': 'Home', 'color': '#EC4899', 'is_system': True},  # Pink
    ]

    # Use bulk insert for efficiency
    op.bulk_insert(
        sa.table('categories',
            sa.column('id', sa.dialects.postgresql.UUID),
            sa.column('user_id', sa.dialects.postgresql.UUID),
            sa.column('name', sa.VARCHAR),
            sa.column('is_system', sa.BOOLEAN),
            sa.column('color', sa.VARCHAR),
            sa.column('created_at', sa.TIMESTAMP),
        ),
        [
            {
                'id': cat['id'],
                'user_id': None,
                'name': cat['name'],
                'is_system': cat['is_system'],
                'color': cat['color'],
                'created_at': sa.text('CURRENT_TIMESTAMP'),
            }
            for cat in system_categories
        ]
    )


def downgrade() -> None:
    # Delete all system categories
    op.execute("DELETE FROM categories WHERE is_system = true")
