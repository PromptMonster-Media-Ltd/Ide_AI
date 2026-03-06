"""
project_snapshot.py — Pydantic v2 schemas for ProjectSnapshot entities.
"""
import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class SnapshotCreate(BaseModel):
    """Schema for creating a new project snapshot."""
    name: str = Field(max_length=200)
    description: Optional[str] = None


class SnapshotRead(BaseModel):
    """Schema for snapshot response."""
    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: Optional[str] = None
    snapshot_data: dict[str, Any]
    version: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SnapshotSummary(BaseModel):
    """Schema for snapshot listing (without full snapshot_data)."""
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    description: Optional[str] = None
    version: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LibraryProjectRead(BaseModel):
    """Schema for a project in the library listing with snapshot count."""
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: Optional[str] = None
    platform: str
    audience: str
    complexity: str
    tone: str
    accent_color: str
    created_at: datetime
    updated_at: datetime
    snapshot_count: int = 0

    model_config = ConfigDict(from_attributes=True)
