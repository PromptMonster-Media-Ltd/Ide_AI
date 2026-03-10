"""
design_sheet.py — Pydantic v2 schemas for DesignSheet reads and partial updates.
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DesignSheetRead(BaseModel):
    """Schema for design sheet response."""
    id: uuid.UUID
    project_id: uuid.UUID
    problem: Optional[str] = None
    audience: Optional[str] = None
    mvp: Optional[str] = None
    features: Optional[list] = None
    tone: Optional[str] = None
    platform: Optional[str] = None
    tech_constraints: Optional[str] = None
    success_metric: Optional[str] = None
    fields_data: Optional[dict] = None
    confidence_score: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DesignSheetUpdate(BaseModel):
    """Schema for partial design sheet update."""
    problem: Optional[str] = None
    audience: Optional[str] = None
    mvp: Optional[str] = None
    features: Optional[list] = None
    tone: Optional[str] = None
    platform: Optional[str] = None
    tech_constraints: Optional[str] = None
    success_metric: Optional[str] = None
    fields_data: Optional[dict] = None
    confidence_score: Optional[int] = None
