"""Add Kaggle credentials to users table

Revision ID: 003
Revises: 002
Create Date: 2026-02-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add Kaggle credential columns to users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('kaggle_username', sa.String(255), nullable=True)
        )
        batch_op.add_column(
            sa.Column('kaggle_key_encrypted', sa.Text(), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('kaggle_key_encrypted')
        batch_op.drop_column('kaggle_username')
