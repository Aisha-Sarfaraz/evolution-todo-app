"""create messages table

Revision ID: 010
Revises: 009
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid


# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'messages',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('conversation_id', UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.VARCHAR(64), nullable=False),
        sa.Column('role', sa.VARCHAR(20), nullable=False),
        sa.Column('content', sa.TEXT(), nullable=False),
        sa.Column('tool_calls', JSONB(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # CHECK constraint for role
        sa.CheckConstraint("role IN ('user', 'assistant')", name='chk_message_role'),
    )

    # Foreign key to conversations (CASCADE on delete)
    op.create_foreign_key(
        'fk_messages_conversation_id',
        'messages', 'conversations',
        ['conversation_id'], ['id'],
        ondelete='CASCADE'
    )

    # Index on conversation_id for loading conversation messages
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])

    # Index on user_id for user isolation queries
    op.create_index('ix_messages_user_id', 'messages', ['user_id'])

    # Composite index for context window queries (conversation + chronological)
    op.create_index(
        'ix_messages_conversation_created',
        'messages',
        ['conversation_id', sa.text('created_at DESC')],
    )


def downgrade() -> None:
    op.drop_index('ix_messages_conversation_created', table_name='messages')
    op.drop_index('ix_messages_user_id', table_name='messages')
    op.drop_index('ix_messages_conversation_id', table_name='messages')
    op.drop_constraint('fk_messages_conversation_id', 'messages', type_='foreignkey')
    op.drop_table('messages')
