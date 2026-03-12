"""
templates.py — Project template CRUD for starter packs.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.models.project import Project
from app.models.project_template import ProjectTemplate
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/templates", tags=["templates"])


class TemplateRead(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    icon: str
    category: str
    concept_sheet: Optional[dict] = None
    is_system: bool

    class Config:
        from_attributes = True


@router.get("", response_model=list[TemplateRead])
async def list_templates(db: AsyncSession = Depends(get_db)):
    """List all project templates (system + user-created)."""
    result = await db.execute(
        select(ProjectTemplate).order_by(ProjectTemplate.category, ProjectTemplate.name)
    )
    return result.scalars().all()


@router.post("/{template_id}/use")
async def use_template(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new project from a template."""
    result = await db.execute(
        select(ProjectTemplate).where(ProjectTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    project = Project(
        name=f"{template.name} Project",
        description=template.description,
        owner_id=current_user.id,
    )
    db.add(project)
    await db.flush()

    return {
        "project_id": str(project.id),
        "name": project.name,
        "template_name": template.name,
    }
