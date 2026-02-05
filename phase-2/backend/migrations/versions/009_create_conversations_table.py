"""create conversations table

Revision ID: 009
Revises: 008
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'conversations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('user_id', sa.VARCHAR(64), nullable=False),
        sa.Column('title', sa.VARCHAR(200), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Index on user_id for listing user's conversations
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])

    # Index on updated_at for sorting by recent activity
    op.create_index('ix_conversations_updated_at', 'conversations', ['updated_at'])

    # Foreign key to users table (CASCADE on delete)
    op.create_foreign_key(
        'fk_conversations_user_id',
        'conversations', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('fk_conversations_user_id', 'conversations', type_='foreignkey')
    op.drop_index('ix_conversations_updated_at', table_name='conversations')
    op.drop_index('ix_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')
