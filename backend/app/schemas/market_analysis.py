"""
market_analysis.py — Pydantic v2 schemas for MarketAnalysis reads and generation requests.
"""
import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class MarketAnalysisRead(BaseModel):
    """Full market analysis response."""
    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    target_market: Optional[dict[str, Any]] = None
    competitive_landscape: Optional[dict[str, Any]] = None
    market_metrics: Optional[dict[str, Any]] = None
    revenue_projections: Optional[dict[str, Any]] = None
    marketing_strategies: Optional[dict[str, Any]] = None
    status: str = "pending"
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MarketAnalysisGenerate(BaseModel):
    """Request body for triggering market analysis generation."""
    force_regenerate: bool = False
