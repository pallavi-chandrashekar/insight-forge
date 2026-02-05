from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base
from app.models.types import UUID, JSONType


class SourceType(str, enum.Enum):
    FILE = "file"
    URL = "url"
    SCRAPE = "scrape"


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    context_id = Column(UUID, ForeignKey("contexts.id", ondelete="SET NULL"), nullable=True)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_type = Column(Enum(SourceType), nullable=False)
    source_url = Column(String(1024), nullable=True)  # For URL/scrape sources

    # File info
    file_path = Column(String(512), nullable=True)
    original_filename = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)  # bytes
    file_type = Column(String(50), nullable=True)  # csv, json, excel, parquet

    # Data info
    schema = Column(JSONType, nullable=True)  # Column names, types, sample values
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="datasets")
    context = relationship("Context", back_populates="datasets_rel")
    queries = relationship("Query", back_populates="dataset", cascade="all, delete-orphan")
    visualizations = relationship("Visualization", back_populates="dataset", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Dataset {self.name}>"
