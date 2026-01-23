from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class QueryType(str, enum.Enum):
    SQL = "sql"
    NATURAL_LANGUAGE = "natural_language"
    PANDAS = "pandas"


class Query(Base):
    __tablename__ = "queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=True)
    query_type = Column(Enum(QueryType), nullable=False)

    # Original input (natural language or raw query)
    original_input = Column(Text, nullable=False)

    # Generated/translated query (for NL -> SQL/Pandas translation)
    generated_query = Column(Text, nullable=True)

    # Result preview (first N rows as JSON)
    result_preview = Column(JSONB, nullable=True)
    result_row_count = Column(String(50), nullable=True)

    # Execution info
    execution_time_ms = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="queries")
    dataset = relationship("Dataset", back_populates="queries")
    visualizations = relationship("Visualization", back_populates="query")

    def __repr__(self):
        return f"<Query {self.id}>"
