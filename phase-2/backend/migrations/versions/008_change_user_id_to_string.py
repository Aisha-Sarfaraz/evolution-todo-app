"""change user_id columns from UUID to VARCHAR(64)

Revision ID: 008
Revises: 007
Create Date: 2026-01-29

Better Auth uses string IDs (not UUIDs), so user_id columns must be VARCHAR(64).
Drops FK constraints since Better Auth manages users in its own tables.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Drop ALL foreign key constraints on tasks, categories, tags that reference users.id
    # Use IF EXISTS since constraint names may vary
    conn.execute(sa.text("ALTER TABLE tasks DROP CONSTRAINT IF EXISTS fk_tasks_user_id"))
    conn.execute(sa.text("ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_user_id_fkey"))
    conn.execute(sa.text("ALTER TABLE tasks DROP CONSTRAINT IF EXISTS fk_tasks_category_id"))
    conn.execute(sa.text("ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_category_id_fkey"))
    conn.execute(sa.text("ALTER TABLE categories DROP CONSTRAINT IF EXISTS fk_categories_user_id"))
    conn.execute(sa.text("ALTER TABLE categories DROP CONSTRAINT IF EXISTS categories_user_id_fkey"))
    conn.execute(sa.text("ALTER TABLE tags DROP CONSTRAINT IF EXISTS fk_tags_user_id"))
    conn.execute(sa.text("ALTER TABLE tags DROP CONSTRAINT IF EXISTS tags_user_id_fkey"))

    # 2. Drop unique indexes that include user_id (IF EXISTS)
    conn.execute(sa.text("DROP INDEX IF EXISTS idx_categories_user_name_unique"))
    conn.execute(sa.text("DROP INDEX IF EXISTS idx_tags_user_name_unique"))

    # 3. Change user_id columns from UUID to VARCHAR(64)
    conn.execute(sa.text("ALTER TABLE tasks ALTER COLUMN user_id TYPE VARCHAR(64) USING user_id::text"))
    conn.execute(sa.text("ALTER TABLE categories ALTER COLUMN user_id TYPE VARCHAR(64) USING user_id::text"))
    conn.execute(sa.text("ALTER TABLE tags ALTER COLUMN user_id TYPE VARCHAR(64) USING user_id::text"))

    # 4. Change users.id from UUID to VARCHAR(64)
    conn.execute(sa.text("ALTER TABLE users ALTER COLUMN id TYPE VARCHAR(64) USING id::text"))

    # 5. Recreate unique indexes
    conn.execute(sa.text("CREATE UNIQUE INDEX idx_categories_user_name_unique ON categories (user_id, LOWER(name))"))
    conn.execute(sa.text("CREATE UNIQUE INDEX idx_tags_user_name_unique ON tags (user_id, LOWER(name))"))

    # 6. Re-add category FK for tasks
    conn.execute(sa.text("ALTER TABLE tasks ADD CONSTRAINT fk_tasks_category_id FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL"))


def downgrade() -> None:
    # Drop re-added FK
    op.drop_constraint('fk_tasks_category_id', 'tasks', type_='foreignkey')

    # Drop recreated indexes
    op.drop_index('idx_tags_user_name_unique', table_name='tags')
    op.drop_index('idx_categories_user_name_unique', table_name='categories')

    # Revert users.id to UUID
    op.alter_column('users', 'id',
                    type_=sa.dialects.postgresql.UUID(),
                    existing_type=sa.VARCHAR(64),
                    existing_nullable=False,
                    postgresql_using='id::uuid')

    # Revert user_id columns to UUID
    op.alter_column('tags', 'user_id',
                    type_=sa.dialects.postgresql.UUID(),
                    existing_type=sa.VARCHAR(64),
                    existing_nullable=False,
                    postgresql_using='user_id::uuid')

    op.alter_column('categories', 'user_id',
                    type_=sa.dialects.postgresql.UUID(),
                    existing_type=sa.VARCHAR(64),
                    existing_nullable=True,
                    postgresql_using='user_id::uuid')

    op.alter_column('tasks', 'user_id',
                    type_=sa.dialects.postgresql.UUID(),
                    existing_type=sa.VARCHAR(64),
                    existing_nullable=False,
                    postgresql_using='user_id::uuid')

    # Recreate unique indexes
    op.create_index(
        'idx_categories_user_name_unique',
        'categories',
        [sa.text('user_id'), sa.text('LOWER(name)')],
        unique=True
    )

    op.create_index(
        'idx_tags_user_name_unique',
        'tags',
        [sa.text('user_id'), sa.text('LOWER(name)')],
        unique=True
    )

    # Recreate FK constraints
    op.create_foreign_key(
        'fk_tags_user_id', 'tags', 'users',
        ['user_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_categories_user_id', 'categories', 'users',
        ['user_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_tasks_category_id', 'tasks', 'categories',
        ['category_id'], ['id'], ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_tasks_user_id', 'tasks', 'users',
        ['user_id'], ['id'], ondelete='CASCADE'
    )
