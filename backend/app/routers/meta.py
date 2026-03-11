"""
meta.py — Static metadata endpoints (partner styles, modules, categories, etc.).
"""
from fastapi import APIRouter

from app.services.categorization_service import get_all_categories
from app.services.modular_pathway_service import get_all_modules
from app.services.partner_style_service import list_partner_styles

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/partner-styles")
async def get_partner_styles():
    """Return ordered metadata for all AI partner styles (for frontend selector)."""
    return list_partner_styles()


@router.get("/modules")
async def get_modules():
    """Return full module library with IDs, labels, groups, descriptions, estimated times."""
    return get_all_modules()


@router.get("/categories")
async def get_categories():
    """Return all 16 concept categories with default module stacks."""
    return get_all_categories()
