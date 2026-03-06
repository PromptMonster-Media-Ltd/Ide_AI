"""
market_analysis.py — MarketAnalysis ORM model. Stores AI-generated market research
including target market, competitive landscape, metrics, revenue projections, and strategies.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MarketAnalysis(Base):
    __tablename__ = "market_analyses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), unique=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Analysis sections — each stored as structured JSON
    target_market: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    competitive_landscape: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    market_metrics: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    revenue_projections: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    marketing_strategies: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Generation status: pending | generating | complete | error
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="market_analysis")
    owner = relationship("User")
