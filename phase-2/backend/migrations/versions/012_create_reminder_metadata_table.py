"""create reminder_metadata table

Revision ID: 012
Revises: 011
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'reminder_metadata',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('task_id', UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('due_date', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('reminder_time', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('notification_sent', sa.BOOLEAN(), nullable=False, server_default='false'),
        sa.Column('snooze_until', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # At least one of due_date or reminder_time must be set
        sa.CheckConstraint(
            'due_date IS NOT NULL OR reminder_time IS NOT NULL',
            name='chk_reminder_has_date'
        ),
    )

    # Foreign key to tasks (CASCADE on delete)
    op.create_foreign_key(
        'fk_reminder_metadata_task_id',
        'reminder_metadata', 'tasks',
        ['task_id'], ['id'],
        ondelete='CASCADE'
    )

    # Index for scheduler queries (find due reminders that haven't been sent)
    op.create_index(
        'ix_reminder_metadata_reminder_sent',
        'reminder_metadata',
        ['reminder_time', 'notification_sent'],
    )


def downgrade() -> None:
    op.drop_index('ix_reminder_metadata_reminder_sent', table_name='reminder_metadata')
    op.drop_constraint('fk_reminder_metadata_task_id', 'reminder_metadata', type_='foreignkey')
    op.drop_table('reminder_metadata')
