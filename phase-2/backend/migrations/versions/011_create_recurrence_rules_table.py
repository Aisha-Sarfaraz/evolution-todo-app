"""create recurrence_rules table

Revision ID: 011
Revises: 010
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid


# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'recurrence_rules',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('task_id', UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('frequency', sa.VARCHAR(20), nullable=False),
        sa.Column('interval', sa.INTEGER(), nullable=False, server_default='1'),
        sa.Column('days_of_week', ARRAY(sa.INTEGER()), nullable=True),
        sa.Column('day_of_month', sa.INTEGER(), nullable=True),
        sa.Column('end_date', sa.DATE(), nullable=True),
        sa.Column('next_occurrence', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # CHECK constraints
        sa.CheckConstraint(
            "frequency IN ('daily','weekly','monthly','yearly')",
            name='chk_recurrence_frequency'
        ),
        sa.CheckConstraint(
            '"interval" >= 1',
            name='chk_recurrence_interval'
        ),
        sa.CheckConstraint(
            'day_of_month IS NULL OR (day_of_month >= 1 AND day_of_month <= 31)',
            name='chk_recurrence_day_of_month'
        ),
    )

    # Foreign key to tasks (CASCADE on delete)
    op.create_foreign_key(
        'fk_recurrence_rules_task_id',
        'recurrence_rules', 'tasks',
        ['task_id'], ['id'],
        ondelete='CASCADE'
    )

    # Index on next_occurrence for scheduler queries
    op.create_index('ix_recurrence_rules_next_occurrence', 'recurrence_rules', ['next_occurrence'])


def downgrade() -> None:
    op.drop_index('ix_recurrence_rules_next_occurrence', table_name='recurrence_rules')
    op.drop_constraint('fk_recurrence_rules_task_id', 'recurrence_rules', type_='foreignkey')
    op.drop_table('recurrence_rules')
