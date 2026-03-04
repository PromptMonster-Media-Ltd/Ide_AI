"""
prompt_kit.py — Pydantic v2 schemas for PromptKit generation and retrieval.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PromptKitRead(BaseModel):
    """Schema for prompt kit response."""
    id: uuid.UUID
    project_id: uuid.UUID
    platform: str
    content: str
    version: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PromptKitGenerate(BaseModel):
    """Schema for requesting prompt kit generation."""
    platform: str
