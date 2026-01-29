"""create users table

Revision ID: 001
Revises:
Create Date: 2026-01-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('email', sa.VARCHAR(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.VARCHAR(255), nullable=False),
        sa.Column('email_verified', sa.BOOLEAN(), nullable=False, server_default='false'),
        sa.Column('display_name', sa.VARCHAR(100), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_signin_at', sa.TIMESTAMP(), nullable=True),
    )

    # Create index on email for faster lookups
    op.create_index('idx_users_email', 'users', ['email'], unique=True)


def downgrade() -> None:
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
