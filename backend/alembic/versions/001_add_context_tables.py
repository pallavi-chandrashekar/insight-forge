"""Add context tables

Revision ID: 001
Revises:
Create Date: 2026-02-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE context_type_enum AS ENUM ('single_dataset', 'multi_dataset')")
    op.execute("CREATE TYPE context_status_enum AS ENUM ('draft', 'active', 'deprecated')")

    # Create contexts table
    op.create_table(
        'contexts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(100), nullable=False, index=True),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('context_type', postgresql.ENUM('single_dataset', 'multi_dataset', name='context_type_enum'), nullable=False),
        sa.Column('status', postgresql.ENUM('draft', 'active', 'deprecated', name='context_status_enum'), nullable=False),
        sa.Column('tags', postgresql.JSONB, nullable=True),
        sa.Column('category', sa.String(100), nullable=True, index=True),
        sa.Column('owner', sa.String(255), nullable=True),
        sa.Column('created_by_email', sa.String(255), nullable=True),
        sa.Column('markdown_content', sa.Text(), nullable=False),
        sa.Column('parsed_yaml', postgresql.JSONB, nullable=False),
        sa.Column('datasets', postgresql.JSONB, nullable=False),
        sa.Column('relationships', postgresql.JSONB, nullable=True),
        sa.Column('metrics', postgresql.JSONB, nullable=True),
        sa.Column('business_rules', postgresql.JSONB, nullable=True),
        sa.Column('filters', postgresql.JSONB, nullable=True),
        sa.Column('settings', postgresql.JSONB, nullable=True),
        sa.Column('data_model', postgresql.JSONB, nullable=True),
        sa.Column('glossary', postgresql.JSONB, nullable=True),
        sa.Column('validation_status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('validation_errors', postgresql.JSONB, nullable=True),
        sa.Column('validation_warnings', postgresql.JSONB, nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('file_hash', sa.String(64), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )

    # Create indexes
    op.create_index('idx_context_name_version', 'contexts', ['name', 'version'])
    op.create_index('idx_context_user_name', 'contexts', ['user_id', 'name'])
    op.create_index('idx_context_created_at', 'contexts', ['created_at'])
    op.create_index('idx_context_type', 'contexts', ['context_type'])
    op.create_index('idx_context_status', 'contexts', ['status'])

    # Create query_contexts association table
    op.create_table(
        'query_contexts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('query_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('queries.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('context_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('contexts.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('used_relationships', postgresql.JSONB, nullable=True),
        sa.Column('used_metrics', postgresql.JSONB, nullable=True),
        sa.Column('used_filters', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )

    # Create indexes for query_contexts
    op.create_index('idx_query_context_query', 'query_contexts', ['query_id'])
    op.create_index('idx_query_context_context', 'query_contexts', ['context_id'])

    # Add context_id column to queries table (nullable, for backward compatibility)
    op.add_column('queries', sa.Column('context_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('contexts.id', ondelete='SET NULL'), nullable=True))


def downgrade() -> None:
    # Remove context_id from queries
    op.drop_column('queries', 'context_id')

    # Drop query_contexts table
    op.drop_index('idx_query_context_context', table_name='query_contexts')
    op.drop_index('idx_query_context_query', table_name='query_contexts')
    op.drop_table('query_contexts')

    # Drop contexts table
    op.drop_index('idx_context_status', table_name='contexts')
    op.drop_index('idx_context_type', table_name='contexts')
    op.drop_index('idx_context_created_at', table_name='contexts')
    op.drop_index('idx_context_user_name', table_name='contexts')
    op.drop_index('idx_context_name_version', table_name='contexts')
    op.drop_table('contexts')

    # Drop enum types
    op.execute("DROP TYPE context_status_enum")
    op.execute("DROP TYPE context_type_enum")
