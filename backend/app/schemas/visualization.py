from pydantic import BaseModel, Field
from typing import Optional, Any, Union
from datetime import datetime
from uuid import UUID
from enum import Enum


class ChartType(str, Enum):
    BAR = "bar"
    LINE = "line"
    SCATTER = "scatter"
    PIE = "pie"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"
    BOX = "box"
    AREA = "area"
    TABLE = "table"


class VizConfig(BaseModel):
    x_column: Optional[Union[str, list[str]]] = None
    y_column: Optional[Union[str, list[str]]] = None
    color_column: Optional[str] = None
    size_column: Optional[str] = None
    aggregation: Optional[str] = None  # sum, mean, count, etc.
    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None


class VizRequest(BaseModel):
    dataset_id: UUID
    query_id: Optional[UUID] = None
    chart_type: ChartType
    config: VizConfig
    name: Optional[str] = None
    description: Optional[str] = None


class VizResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    query_id: Optional[UUID]
    name: Optional[str]
    description: Optional[str]
    chart_type: ChartType
    config: dict[str, Any]
    chart_data: Optional[dict[str, Any]]  # Plotly JSON
    image_path: Optional[str]
    tableau_workbook_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class VizSuggestion(BaseModel):
    chart_type: ChartType
    title: str
    description: str
    confidence: float = Field(ge=0, le=1)
    config: VizConfig
    reasoning: str
