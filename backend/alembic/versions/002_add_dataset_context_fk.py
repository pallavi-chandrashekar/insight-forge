"""Add context_id foreign key to datasets table

Revision ID: 002
Revises: 001
Create Date: 2026-02-04

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add nullable context_id column to datasets table
    # Using CHAR(36) for SQLite compatibility (will be UUID in PostgreSQL)
    with op.batch_alter_table('datasets', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('context_id', sa.CHAR(36), nullable=True)
        )

        # Add foreign key constraint with SET NULL on delete
        batch_op.create_foreign_key(
            'fk_datasets_context_id',
            'contexts',
            ['context_id'], ['id'],
            ondelete='SET NULL'
        )

        # Add index for performance
        batch_op.create_index(
            'idx_datasets_context_id',
            ['context_id']
        )


def downgrade() -> None:
    # Use batch mode for SQLite compatibility
    with op.batch_alter_table('datasets', schema=None) as batch_op:
        # Drop index
        batch_op.drop_index('idx_datasets_context_id')

        # Drop foreign key constraint
        batch_op.drop_constraint('fk_datasets_context_id', type_='foreignkey')

        # Drop column
        batch_op.drop_column('context_id')
