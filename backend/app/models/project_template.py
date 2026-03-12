"""
project_template.py — Starter templates/packs for quick project creation.
Templates are seeded and can also be user-created.
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProjectTemplate(Base):
    """A reusable project template with pre-filled settings."""

    __tablename__ = "project_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(10), default="📋")
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "saas", "mobile", "creative"
    concept_sheet: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # Pre-filled fields
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)  # System templates vs user-created
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
