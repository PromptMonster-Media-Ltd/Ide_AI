"""
pathways.py — API endpoints for concept pathway definitions.
Serves pathway metadata to the frontend for dynamic UI rendering.
"""
from fastapi import APIRouter, HTTPException

from app.pathways import PathwayRegistry

router = APIRouter(prefix="/pathways", tags=["pathways"])


@router.get("/")
async def list_pathways():
    """Return all available pathway definitions."""
    return [p.to_api_dict() for p in PathwayRegistry.all()]


@router.get("/{pathway_id}")
async def get_pathway(pathway_id: str):
    """Return a single pathway definition."""
    try:
        pathway = PathwayRegistry.get(pathway_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Pathway '{pathway_id}' not found")
    return pathway.to_api_dict()
