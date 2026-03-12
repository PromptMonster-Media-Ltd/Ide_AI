"""
share_rating.py — Star ratings (0-5) from external viewers on shared projects.
One rating per email per share.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ShareRating(Base):
    """A star rating on a shared project from an external viewer."""

    __tablename__ = "share_ratings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    share_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("project_shares.id", ondelete="CASCADE"), nullable=False)
    author_name: Mapped[str] = mapped_column(String(100), nullable=False)
    author_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-5
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
