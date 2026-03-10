"""
module_artifact.py — Generic module artifact ORM model.
Stores domain-specific data for pathway modules (storyboard scenes, mood board items, etc.).
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ModuleArtifact(Base):
    __tablename__ = "module_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    module_id: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "storyboard", "mood_board"
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "node", "card", "scene"
    data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="module_artifacts")
