"""
Pydantic schemas for Context API
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class ContextCreate(BaseModel):
    """Schema for creating a context"""
    content: str = Field(..., description="Full context file content (YAML + Markdown)")
    validate: bool = Field(True, description="Whether to validate context")


class ContextUpdate(BaseModel):
    """Schema for updating a context"""
    content: str = Field(..., description="New context file content")
    validate: bool = Field(True, description="Whether to validate context")


class ContextResponse(BaseModel):
    """Basic context response"""
    id: str
    name: str
    version: str
    description: str
    context_type: str
    status: str
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    owner: Optional[str] = None
    created_by: Optional[str] = None
    user_id: str
    datasets_count: int
    relationships_count: int
    metrics_count: int
    validation_status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class ContextListResponse(ContextResponse):
    """Response for listing contexts (same as basic response)"""
    pass


class ContextDetailResponse(ContextResponse):
    """Detailed context response with full content"""
    parsed_yaml: Dict[str, Any]
    markdown_content: str
    datasets: List[Dict[str, Any]]
    relationships: Optional[List[Dict[str, Any]]] = None
    metrics: Optional[List[Dict[str, Any]]] = None
    business_rules: Optional[List[Dict[str, Any]]] = None
    filters: Optional[List[Dict[str, Any]]] = None
    settings: Optional[Dict[str, Any]] = None
    data_model: Optional[Dict[str, Any]] = None
    glossary: Optional[List[Dict[str, Any]]] = None
    validation_errors: Optional[List[Dict[str, Any]]] = None
    validation_warnings: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class ContextStatsResponse(BaseModel):
    """Context statistics response"""
    total_contexts: int
    single_dataset_contexts: int
    multi_dataset_contexts: int
    active_contexts: int
    failed_validation: int


class GlossarySearchResponse(BaseModel):
    """Glossary search result"""
    context_id: str
    context_name: str
    term: str
    definition: str
    synonyms: Optional[List[str]] = None
    related_columns: Optional[List[str]] = None
    examples: Optional[str] = None


class MetricResponse(BaseModel):
    """Metric response"""
    context_id: str
    context_name: str
    id: str
    name: str
    description: Optional[str] = None
    expression: str
    data_type: str
    format: Optional[str] = None
    datasets: Optional[List[str]] = None
    category: Optional[str] = None
    owner: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """Validation error detail"""
    code: str
    message: str
    field: Optional[str] = None
    severity: str
    details: Dict[str, Any] = {}


class ValidationResponse(BaseModel):
    """Validation result response"""
    status: str
    passed: bool
    error_count: int
    warning_count: int
    errors: List[ValidationErrorResponse]
    warnings: List[ValidationErrorResponse]
