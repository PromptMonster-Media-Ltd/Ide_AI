"""
pipeline.py — Pydantic v2 schemas for Pipeline layer nodes.
"""
import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class PipelineNodeRead(BaseModel):
    """Schema for pipeline node response."""
    id: uuid.UUID
    project_id: uuid.UUID
    layer: str
    selected_tool: str
    config: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PipelineNodeUpdate(BaseModel):
    """Schema for partial pipeline node update."""
    selected_tool: Optional[str] = None
    config: Optional[dict[str, Any]] = None


class PipelineRecommendation(BaseModel):
    """Schema for AI-generated pipeline recommendation."""
    nodes: list[PipelineNodeRead]
    estimated_cost_min: int = 0
    estimated_cost_max: int = 0
    reasoning: list[str] = []
