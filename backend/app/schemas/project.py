"""
project.py — Pydantic v2 schemas for Project CRUD operations.
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    name: str = Field(max_length=200)
    platform: str = Field(default="custom", max_length=50)
    audience: str = Field(default="consumers", max_length=50)
    complexity: str = Field(default="medium", max_length=50)
    tone: str = Field(default="casual", max_length=50)
    description: Optional[str] = None
    accent_color: Optional[str] = Field(default="#00E5FF", max_length=20)


class ProjectRead(BaseModel):
    """Schema for project response."""
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

    model_config = ConfigDict(from_attributes=True)


class ProjectUpdate(BaseModel):
    """Schema for partial project update."""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    platform: Optional[str] = Field(None, max_length=50)
    audience: Optional[str] = Field(None, max_length=50)
    complexity: Optional[str] = Field(None, max_length=50)
    tone: Optional[str] = Field(None, max_length=50)
    accent_color: Optional[str] = Field(None, max_length=20)
