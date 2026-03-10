"""
meta.py — Static metadata endpoints (partner styles, platform info, etc.).
"""
from fastapi import APIRouter

from app.services.partner_style_service import list_partner_styles

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/partner-styles")
async def get_partner_styles():
    """Return ordered metadata for all AI partner styles (for frontend selector)."""
    return list_partner_styles()
