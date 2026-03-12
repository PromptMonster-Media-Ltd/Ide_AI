"""
branching.py — Concept branching (git-like fork for ideas).
Creates a copy of a project so users can explore alternative directions.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.models.concept_branch import ConceptBranch
from app.models.project import Project
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/branching", tags=["branching"])


class BranchCreate(BaseModel):
    branch_name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None


class BranchRead(BaseModel):
    id: uuid.UUID
    parent_project_id: uuid.UUID
    branch_project_id: uuid.UUID
    branch_name: str
    description: Optional[str] = None
    created_at: str


@router.post("/{project_id}/branch", status_code=status.HTTP_201_CREATED)
async def create_branch(
    project_id: uuid.UUID,
    payload: BranchCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fork a project into a new branch for exploring alternative directions."""
    # Verify ownership
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    parent = result.scalar_one_or_none()
    if not parent:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create the branch as a new project
    branch_project = Project(
        name=f"{parent.name} — {payload.branch_name}",
        description=parent.description,
        owner_id=current_user.id,
    )
    db.add(branch_project)
    await db.flush()

    # Record the branch relationship
    branch = ConceptBranch(
        parent_project_id=project_id,
        branch_project_id=branch_project.id,
        branch_name=payload.branch_name,
        description=payload.description,
        created_by=current_user.id,
    )
    db.add(branch)
    await db.flush()

    return {
        "id": str(branch.id),
        "parent_project_id": str(project_id),
        "branch_project_id": str(branch_project.id),
        "branch_name": branch.branch_name,
        "description": branch.description,
        "created_at": branch.created_at.isoformat(),
    }


@router.get("/{project_id}/branches")
async def list_branches(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all branches for a project."""
    result = await db.execute(
        select(ConceptBranch)
        .where(ConceptBranch.parent_project_id == project_id, ConceptBranch.created_by == current_user.id)
        .order_by(ConceptBranch.created_at.desc())
    )
    branches = result.scalars().all()
    return [
        {
            "id": str(b.id),
            "parent_project_id": str(b.parent_project_id),
            "branch_project_id": str(b.branch_project_id),
            "branch_name": b.branch_name,
            "description": b.description,
            "created_at": b.created_at.isoformat(),
        }
        for b in branches
    ]
