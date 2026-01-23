from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class SourceType(str, Enum):
    FILE = "file"
    URL = "url"
    SCRAPE = "scrape"


class ColumnSchema(BaseModel):
    name: str
    dtype: str
    nullable: bool
    sample_values: list[Any]


class DatasetSchema(BaseModel):
    columns: list[ColumnSchema]
    total_rows: int
    total_columns: int


class DatasetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class DatasetResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    source_type: SourceType
    source_url: Optional[str]
    original_filename: Optional[str]
    file_size: Optional[int]
    file_type: Optional[str]
    schema_info: Optional[dict] = Field(alias="schema")
    row_count: Optional[int]
    column_count: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        populate_by_name = True


class DatasetPreview(BaseModel):
    dataset_id: UUID
    columns: list[str]
    data: list[dict[str, Any]]
    total_rows: int
    preview_rows: int


class UrlImportRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    url: str
    description: Optional[str] = None


class ScrapeRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    url: str
    selector: Optional[str] = None  # CSS selector for table
    description: Optional[str] = None
