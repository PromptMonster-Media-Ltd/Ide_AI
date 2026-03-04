"""
design_sheet.py — Design sheet router. Reads and updates the design sheet for a project.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.design_sheet import DesignSheet
from app.models.project import Project
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.design_sheet import DesignSheetRead, DesignSheetUpdate

router = APIRouter(prefix="/design-sheet", tags=["design-sheet"])


@router.get("/{project_id}", response_model=DesignSheetRead)
async def get_design_sheet(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the design sheet for a project."""
    # Verify project belongs to user
    proj_result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    if not proj_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    result = await db.execute(
        select(DesignSheet).where(DesignSheet.project_id == project_id)
    )
    sheet = result.scalar_one_or_none()
    if not sheet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Design sheet not found")
    return sheet


@router.patch("/{project_id}", response_model=DesignSheetRead)
async def update_design_sheet(
    project_id: uuid.UUID,
    payload: DesignSheetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the design sheet for a project."""
    proj_result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    if not proj_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    result = await db.execute(
        select(DesignSheet).where(DesignSheet.project_id == project_id)
    )
    sheet = result.scalar_one_or_none()
    if not sheet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Design sheet not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sheet, field, value)

    # Recompute confidence
    from app.services.discovery_service import compute_confidence
    sheet.confidence_score = compute_confidence(sheet)

    await db.flush()
    return sheet
