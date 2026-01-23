from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class QueryType(str, Enum):
    SQL = "sql"
    NATURAL_LANGUAGE = "natural_language"
    PANDAS = "pandas"


class QueryRequest(BaseModel):
    dataset_id: UUID
    query_type: QueryType
    query: str = Field(..., min_length=1)
    name: Optional[str] = None


class NaturalLanguageQueryRequest(BaseModel):
    dataset_id: UUID
    question: str = Field(..., min_length=1)
    name: Optional[str] = None


class QueryResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    name: Optional[str]
    query_type: QueryType
    original_input: str
    generated_query: Optional[str]
    result_preview: Optional[list[dict[str, Any]]]
    result_row_count: Optional[str]
    execution_time_ms: Optional[str]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class QueryHistoryItem(BaseModel):
    id: UUID
    dataset_id: UUID
    dataset_name: str
    name: Optional[str]
    query_type: QueryType
    original_input: str
    created_at: datetime

    class Config:
        from_attributes = True
