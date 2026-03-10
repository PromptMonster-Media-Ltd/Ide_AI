"""
pathways.py — API endpoints for concept pathway definitions.
Serves pathway metadata to the frontend for dynamic UI rendering.
Includes AI-powered pathway detection from project descriptions.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.pathways import PathwayRegistry
from app.services.pathway_service import detect_pathway

router = APIRouter(prefix="/pathways", tags=["pathways"])


class DetectRequest(BaseModel):
    description: str


@router.get("/")
async def list_pathways():
    """Return all available pathway definitions."""
    return [p.to_api_dict() for p in PathwayRegistry.all()]


@router.post("/detect")
async def detect_pathway_endpoint(payload: DetectRequest):
    """AI-detect the best pathway for a project description."""
    result = await detect_pathway(payload.description)
    # Include full pathway definition alongside the detection result
    try:
        pw = PathwayRegistry.get(result["pathway_id"])
        result["pathway"] = pw.to_api_dict()
    except ValueError:
        pass
    return result


@router.get("/{pathway_id}")
async def get_pathway(pathway_id: str):
    """Return a single pathway definition."""
    try:
        pathway = PathwayRegistry.get(pathway_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Pathway '{pathway_id}' not found")
    return pathway.to_api_dict()
