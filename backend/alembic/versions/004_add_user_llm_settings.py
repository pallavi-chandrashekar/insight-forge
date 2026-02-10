"""Add LLM settings to users table

Revision ID: 004
Revises: 003
Create Date: 2024-02-09
"""

from alembic import op
import sqlalchemy as sa

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('llm_provider', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('llm_api_key_encrypted', sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('llm_api_key_encrypted')
        batch_op.drop_column('llm_provider')
