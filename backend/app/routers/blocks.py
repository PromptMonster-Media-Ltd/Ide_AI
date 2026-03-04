"""
blocks.py — Feature blocks router. CRUD and AI generation for design blocks.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.block import Block
from app.models.design_sheet import DesignSheet
from app.models.project import Project
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.block import BlockCreate, BlockRead, BlockUpdate
from app.services.sheet_service import generate_blocks

router = APIRouter(prefix="/projects/{project_id}/blocks", tags=["blocks"])


async def _verify_project(project_id: uuid.UUID, user: User, db: AsyncSession) -> Project:
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.get("/", response_model=list[BlockRead])
async def list_blocks(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all blocks for a project, ordered by position."""
    await _verify_project(project_id, current_user, db)
    result = await db.execute(
        select(Block).where(Block.project_id == project_id).order_by(Block.order)
    )
    return result.scalars().all()


@router.post("/", response_model=BlockRead, status_code=status.HTTP_201_CREATED)
async def create_block(
    project_id: uuid.UUID,
    payload: BlockCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a custom block."""
    await _verify_project(project_id, current_user, db)
    # Get max order
    result = await db.execute(
        select(Block.order).where(Block.project_id == project_id).order_by(Block.order.desc()).limit(1)
    )
    max_order = result.scalar() or 0

    block = Block(
        project_id=project_id,
        name=payload.name,
        description=payload.description,
        category=payload.category,
        priority=payload.priority,
        effort=payload.effort,
        order=max_order + 1,
        is_mvp=payload.is_mvp,
    )
    db.add(block)
    await db.flush()
    return block


@router.post("/generate", response_model=list[BlockRead])
async def ai_generate_blocks(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI-generate blocks from the design sheet. Replaces existing blocks."""
    await _verify_project(project_id, current_user, db)

    # Get design sheet
    sheet_result = await db.execute(
        select(DesignSheet).where(DesignSheet.project_id == project_id)
    )
    sheet = sheet_result.scalar_one_or_none()
    if not sheet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Design sheet not found")

    # Delete existing blocks
    await db.execute(delete(Block).where(Block.project_id == project_id))

    # Generate new blocks
    blocks = await generate_blocks(db, sheet, project_id)
    return blocks


@router.patch("/{block_id}", response_model=BlockRead)
async def update_block(
    project_id: uuid.UUID,
    block_id: uuid.UUID,
    payload: BlockUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a block."""
    await _verify_project(project_id, current_user, db)
    result = await db.execute(
        select(Block).where(Block.id == block_id, Block.project_id == project_id)
    )
    block = result.scalar_one_or_none()
    if not block:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(block, field, value)

    await db.flush()
    return block


@router.delete("/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_block(
    project_id: uuid.UUID,
    block_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a block."""
    await _verify_project(project_id, current_user, db)
    result = await db.execute(
        select(Block).where(Block.id == block_id, Block.project_id == project_id)
    )
    block = result.scalar_one_or_none()
    if not block:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found")
    await db.delete(block)
    await db.flush()
