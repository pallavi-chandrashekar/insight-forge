"""
Context model for storing dataset metadata and relationships
"""
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class ContextType(str, enum.Enum):
    """Context type enum"""
    SINGLE_DATASET = "single_dataset"
    MULTI_DATASET = "multi_dataset"


class ContextStatus(str, enum.Enum):
    """Context status enum"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class Context(Base):
    """
    Context file metadata and content.

    Contexts can be:
    - Single-dataset: Rich documentation for one dataset
    - Multi-dataset: Relationship definitions across datasets
    """
    __tablename__ = "contexts"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User ownership
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Context metadata
    name = Column(String(100), nullable=False, index=True)
    version = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    context_type = Column(
        SQLEnum(ContextType, name="context_type_enum"),
        nullable=False,
        default=ContextType.SINGLE_DATASET
    )
    status = Column(
        SQLEnum(ContextStatus, name="context_status_enum"),
        nullable=False,
        default=ContextStatus.ACTIVE
    )

    # Optional metadata
    tags = Column(JSONB, nullable=True)  # Array of strings
    category = Column(String(100), nullable=True, index=True)
    owner = Column(String(255), nullable=True)
    created_by_email = Column(String(255), nullable=True)

    # Content storage
    markdown_content = Column(Text, nullable=False)  # Full markdown file
    parsed_yaml = Column(JSONB, nullable=False)      # Parsed YAML frontmatter

    # Cached parsed structures for performance
    datasets = Column(JSONB, nullable=False)          # Array of dataset definitions
    relationships = Column(JSONB, nullable=True)      # Array of relationships
    metrics = Column(JSONB, nullable=True)            # Array of metrics
    business_rules = Column(JSONB, nullable=True)     # Array of business rules
    filters = Column(JSONB, nullable=True)            # Array of filters
    settings = Column(JSONB, nullable=True)           # Context settings

    # New rich metadata fields
    data_model = Column(JSONB, nullable=True)         # ER diagram and entities
    glossary = Column(JSONB, nullable=True)           # Business term definitions

    # Validation status
    validation_status = Column(
        String(20),
        nullable=False,
        default="pending"
    )  # pending/passed/failed/warning
    validation_errors = Column(JSONB, nullable=True)  # Validation error details
    validation_warnings = Column(JSONB, nullable=True) # Validation warnings

    # Metadata
    file_size_bytes = Column(Integer, nullable=True)
    file_hash = Column(String(64), nullable=True, index=True)  # SHA-256 for deduplication

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="contexts")
    query_contexts = relationship(
        "QueryContext",
        back_populates="context",
        cascade="all, delete-orphan"
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_context_name_version", "name", "version"),
        Index("idx_context_user_name", "user_id", "name"),
        Index("idx_context_created_at", "created_at"),
        Index("idx_context_type", "context_type"),
        Index("idx_context_status", "status"),
    )

    def __repr__(self):
        return f"<Context {self.name} v{self.version} ({self.context_type})>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "context_type": self.context_type.value,
            "status": self.status.value,
            "tags": self.tags,
            "category": self.category,
            "owner": self.owner,
            "created_by": self.created_by_email,
            "user_id": str(self.user_id),
            "datasets_count": len(self.datasets) if self.datasets else 0,
            "relationships_count": len(self.relationships) if self.relationships else 0,
            "metrics_count": len(self.metrics) if self.metrics else 0,
            "validation_status": self.validation_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class QueryContext(Base):
    """
    Association between queries and contexts.
    Tracks which parts of the context were used in a query.
    """
    __tablename__ = "query_contexts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(
        UUID(as_uuid=True),
        ForeignKey("queries.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    context_id = Column(
        UUID(as_uuid=True),
        ForeignKey("contexts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Track which parts of the context were used
    used_relationships = Column(JSONB, nullable=True)  # Array of relationship IDs used
    used_metrics = Column(JSONB, nullable=True)        # Array of metric IDs used
    used_filters = Column(JSONB, nullable=True)        # Array of filter IDs used

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    query = relationship("Query", back_populates="query_contexts")
    context = relationship("Context", back_populates="query_contexts")

    __table_args__ = (
        Index("idx_query_context_query", "query_id"),
        Index("idx_query_context_context", "context_id"),
    )

    def __repr__(self):
        return f"<QueryContext query={self.query_id} context={self.context_id}>"
