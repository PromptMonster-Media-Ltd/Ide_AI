"""
library.py — Library router. Manages .ideai file export/import and project snapshot versioning.
"""
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import Response
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.project import Project
from app.models.project_snapshot import ProjectSnapshot
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.project_snapshot import LibraryProjectRead, SnapshotCreate, SnapshotSummary
from app.services import library_service

router = APIRouter(prefix="/library", tags=["library"])


@router.get("/projects", response_model=list[LibraryProjectRead])
async def list_library_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all user projects with snapshot counts for the library view."""
    # Subquery to count snapshots per project
    snapshot_count_sq = (
        select(
            ProjectSnapshot.project_id,
            sa_func.count(ProjectSnapshot.id).label("snapshot_count"),
        )
        .group_by(ProjectSnapshot.project_id)
        .subquery()
    )

    result = await db.execute(
        select(
            Project,
            sa_func.coalesce(snapshot_count_sq.c.snapshot_count, 0).label("snapshot_count"),
        )
        .outerjoin(snapshot_count_sq, Project.id == snapshot_count_sq.c.project_id)
        .where(Project.user_id == current_user.id)
        .order_by(Project.updated_at.desc())
    )

    projects = []
    for row in result.all():
        project = row[0]
        count = row[1]
        projects.append(
            LibraryProjectRead(
                id=project.id,
                user_id=project.user_id,
                name=project.name,
                description=project.description,
                platform=project.platform,
                audience=project.audience,
                complexity=project.complexity,
                tone=project.tone,
                accent_color=project.accent_color,
                created_at=project.created_at,
                updated_at=project.updated_at,
                snapshot_count=count,
            )
        )
    return projects


@router.post("/{project_id}/export")
async def export_ideai_file(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download a project as a .ideai schema file."""
    proj_r = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = proj_r.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    content = await library_service.export_ideai_file(project, db)
    slug = project.name.lower().replace(" ", "-")[:30]
    filename = f"{slug}.ideai"

    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/import", response_model=LibraryProjectRead)
async def import_ideai_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload and import a .ideai file to create a new project."""
    if not file.filename or not file.filename.endswith(".ideai"):
        raise HTTPException(status_code=400, detail="File must have .ideai extension")

    try:
        raw = await file.read()
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=400, detail="Invalid .ideai file: could not parse JSON")

    if data.get("format") != "ideai_schema":
        raise HTTPException(status_code=400, detail="Invalid .ideai file: missing or wrong format field")

    try:
        project = await library_service.import_ideai_file(data, current_user.id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

    return LibraryProjectRead(
        id=project.id,
        user_id=project.user_id,
        name=project.name,
        description=project.description,
        platform=project.platform,
        audience=project.audience,
        complexity=project.complexity,
        tone=project.tone,
        accent_color=project.accent_color,
        created_at=project.created_at,
        updated_at=project.updated_at,
        snapshot_count=0,
    )


@router.post("/{project_id}/snapshots", response_model=SnapshotSummary, status_code=status.HTTP_201_CREATED)
async def create_snapshot(
    project_id: uuid.UUID,
    payload: SnapshotCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a named snapshot of the current project state."""
    try:
        snapshot = await library_service.create_snapshot(
            project_id=project_id,
            user_id=current_user.id,
            name=payload.name,
            description=payload.description,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return snapshot


@router.get("/{project_id}/snapshots", response_model=list[SnapshotSummary])
async def list_snapshots(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all snapshots for a project."""
    try:
        snapshots = await library_service.list_snapshots(project_id, current_user.id, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return snapshots


@router.post("/snapshots/{snapshot_id}/restore")
async def restore_snapshot(
    snapshot_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Restore a project to a previously saved snapshot state."""
    try:
        project = await library_service.restore_snapshot(snapshot_id, current_user.id, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return {"status": "restored", "project_id": str(project.id), "project_name": project.name}
