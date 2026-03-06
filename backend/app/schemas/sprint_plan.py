"""
sprint_plan.py — Pydantic v2 schemas for SprintPlan reads, generation, and updates.
"""
import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class SprintPlanRead(BaseModel):
    """Full sprint plan response."""
    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    milestones: Optional[list[dict[str, Any]]] = None
    sprints: Optional[list[dict[str, Any]]] = None
    timeline: Optional[list[dict[str, Any]]] = None
    status: str = "pending"
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SprintPlanGenerate(BaseModel):
    """Request body for triggering sprint plan generation."""
    force_regenerate: bool = False


class SprintPlanUpdate(BaseModel):
    """Request body for updating a sprint plan (manual edits)."""
    milestones: Optional[list[dict[str, Any]]] = None
    sprints: Optional[list[dict[str, Any]]] = None
    timeline: Optional[list[dict[str, Any]]] = None
    status: Optional[str] = None
