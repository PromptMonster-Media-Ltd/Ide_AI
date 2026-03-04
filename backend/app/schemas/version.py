"""
version.py — Pydantic v2 schemas for Version snapshot entities.
"""
import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class VersionCreate(BaseModel):
    """Schema for creating a new version snapshot."""
    snapshot: dict[str, Any]
    label: Optional[str] = None


class VersionRead(BaseModel):
    """Schema for version response."""
    id: uuid.UUID
    project_id: uuid.UUID
    snapshot: dict[str, Any]
    label: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
