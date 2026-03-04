"""
exports.py — Export router. Generates downloadable design kit files in multiple formats.
Also includes version management endpoints.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.block import Block
from app.models.design_sheet import DesignSheet
from app.models.pipeline_node import PipelineNode
from app.models.project import Project
from app.models.version import Version
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.version import VersionCreate, VersionRead
from app.services import export_service

router = APIRouter(prefix="/projects/{project_id}/export", tags=["exports"])


async def _get_project_data(project_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession):
    """Fetch project, sheet, blocks, and pipeline nodes."""
    proj = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user_id)
    )
    project = proj.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    sheet_r = await db.execute(select(DesignSheet).where(DesignSheet.project_id == project_id))
    sheet = sheet_r.scalar_one_or_none()

    blocks_r = await db.execute(select(Block).where(Block.project_id == project_id).order_by(Block.order))
    blocks = list(blocks_r.scalars().all())

    pipe_r = await db.execute(select(PipelineNode).where(PipelineNode.project_id == project_id))
    pipeline = list(pipe_r.scalars().all())

    return project, sheet, blocks, pipeline


CONTENT_TYPES = {
    "md": ("text/markdown", "design-kit.md"),
    "txt": ("text/plain", "design-kit.txt"),
    "pdf": ("application/pdf", "design-kit.pdf"),
    "docx": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", "design-kit.docx"),
    "zip": ("application/zip", "design-kit.zip"),
}


@router.get("/")
async def export_project(
    project_id: uuid.UUID,
    format: str = "md",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export a project design kit in the specified format."""
    if format not in CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

    project, sheet, blocks, pipeline = await _get_project_data(project_id, current_user.id, db)

    if not sheet:
        raise HTTPException(status_code=404, detail="Design sheet not found. Complete discovery first.")

    content_type, filename = CONTENT_TYPES[format]

    generators = {
        "md": export_service.generate_markdown,
        "txt": export_service.generate_text,
        "pdf": export_service.generate_pdf,
        "docx": export_service.generate_docx,
        "zip": export_service.generate_zip,
    }

    content = await generators[format](sheet, blocks, pipeline)

    if isinstance(content, str):
        content = content.encode("utf-8")

    return Response(
        content=content,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# --- Version management ---

versions_router = APIRouter(prefix="/projects/{project_id}/versions", tags=["versions"])


@versions_router.get("/", response_model=list[VersionRead])
async def list_versions(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all versions for a project."""
    result = await db.execute(
        select(Version)
        .where(Version.project_id == project_id)
        .order_by(Version.created_at.desc())
    )
    return result.scalars().all()


@versions_router.post("/", response_model=VersionRead, status_code=status.HTTP_201_CREATED)
async def create_version(
    project_id: uuid.UUID,
    payload: VersionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a version snapshot of the current project state."""
    # Verify project ownership
    proj = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    if not proj.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    version = Version(
        project_id=project_id,
        snapshot=payload.snapshot,
        label=payload.label,
    )
    db.add(version)
    await db.flush()
    return version


@versions_router.post("/auto", response_model=VersionRead, status_code=status.HTTP_201_CREATED)
async def auto_snapshot(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Auto-create a snapshot from current project state."""
    project, sheet, blocks, pipeline = await _get_project_data(project_id, current_user.id, db)

    snapshot = {
        "project": {"name": project.name, "platform": project.platform, "audience": project.audience},
        "sheet": {
            "problem": sheet.problem if sheet else None,
            "audience": sheet.audience if sheet else None,
            "mvp": sheet.mvp if sheet else None,
            "features": sheet.features if sheet else [],
            "confidence": sheet.confidence_score if sheet else 0,
        },
        "blocks": [
            {"name": b.name, "priority": b.priority, "effort": b.effort}
            for b in blocks
        ],
        "pipeline": [
            {"layer": n.layer, "tool": n.selected_tool}
            for n in pipeline
        ],
    }

    version = Version(
        project_id=project_id,
        snapshot=snapshot,
        label="Auto-snapshot",
    )
    db.add(version)
    await db.flush()
    return version
