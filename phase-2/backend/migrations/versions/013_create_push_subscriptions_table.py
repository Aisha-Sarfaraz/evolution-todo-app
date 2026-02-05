"""create push_subscriptions table

Revision ID: 013
Revises: 012
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid


# revision identifiers, used by Alembic.
revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'push_subscriptions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('user_id', sa.VARCHAR(64), nullable=False),
        sa.Column('endpoint', sa.VARCHAR(500), nullable=False, unique=True),
        sa.Column('keys', JSONB(), nullable=False),
        sa.Column('device_info', JSONB(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Foreign key to users (CASCADE on delete)
    op.create_foreign_key(
        'fk_push_subscriptions_user_id',
        'push_subscriptions', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

    # Index on user_id for querying user's subscriptions
    op.create_index('ix_push_subscriptions_user_id', 'push_subscriptions', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_push_subscriptions_user_id', table_name='push_subscriptions')
    op.drop_constraint('fk_push_subscriptions_user_id', 'push_subscriptions', type_='foreignkey')
    op.drop_table('push_subscriptions')
