"""
sharing.py — Project sharing endpoints for public/private link generation.
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.project import Project
from app.models.user import User
from app.routers.auth import get_current_user
from app.services import sharing_service

router = APIRouter(prefix="/sharing", tags=["sharing"])


class CreateShareRequest(BaseModel):
    is_public: bool = True
    password: str | None = None
    expires_hours: int | None = None


class VerifyPasswordRequest(BaseModel):
    password: str


@router.post("/{project_id}")
async def create_share(
    project_id: uuid.UUID,
    payload: CreateShareRequest = CreateShareRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create or replace a share link for a project."""
    proj_result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    if not proj_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    share = await sharing_service.create_share(
        db, project_id, current_user.id,
        is_public=payload.is_public,
        password=payload.password,
        expires_hours=payload.expires_hours,
    )

    base_url = settings.FRONTEND_URL.rstrip("/")
    share_url = f"{base_url}/shared/{share.share_token}"

    return {
        "share_token": share.share_token,
        "share_url": share_url,
        "is_public": share.is_public,
        "has_password": share.password_hash is not None,
        "expires_at": share.expires_at.isoformat() if share.expires_at else None,
    }


@router.get("/{project_id}/status")
async def get_share_status(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check if a project has an active share link."""
    share = await sharing_service.get_share_by_project(db, project_id)
    if not share:
        return {"active": False}

    base_url = settings.FRONTEND_URL.rstrip("/")
    return {
        "active": True,
        "share_token": share.share_token,
        "share_url": f"{base_url}/shared/{share.share_token}",
        "is_public": share.is_public,
        "has_password": share.password_hash is not None,
        "expires_at": share.expires_at.isoformat() if share.expires_at else None,
        "view_count": share.view_count,
        "created_at": share.created_at.isoformat() if share.created_at else None,
    }


@router.delete("/{project_id}")
async def revoke_share(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke the share link for a project."""
    share = await sharing_service.get_share_by_project(db, project_id)
    if not share:
        raise HTTPException(status_code=404, detail="No active share found")
    await db.delete(share)
    return {"detail": "Share revoked"}


# --- Public endpoints (no auth) ---


@router.get("/public/{token}")
async def get_shared_project(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """Fetch shared project data. No auth required."""
    share = await sharing_service.get_share_by_token(db, token)
    if not share:
        raise HTTPException(status_code=404, detail="Share link not found")

    # Check expiry
    if share.expires_at and share.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Share link has expired")

    # Check if password required
    if not share.is_public and share.password_hash:
        return {"requires_password": True}

    # Increment view count
    share.view_count = (share.view_count or 0) + 1
    await db.flush()

    data = await sharing_service.get_shared_project_data(db, share.project_id)
    return data


@router.post("/public/{token}/verify")
async def verify_shared_password(
    token: str,
    payload: VerifyPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Verify password for a private share link."""
    share = await sharing_service.get_share_by_token(db, token)
    if not share:
        raise HTTPException(status_code=404, detail="Share link not found")

    if share.expires_at and share.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Share link has expired")

    if not share.password_hash:
        # No password needed
        data = await sharing_service.get_shared_project_data(db, share.project_id)
        return data

    if not sharing_service.verify_password(payload.password, share.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect password")

    share.view_count = (share.view_count or 0) + 1
    await db.flush()

    data = await sharing_service.get_shared_project_data(db, share.project_id)
    return data


@router.get("/public/{token}/csv")
async def export_shared_csv(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """Export shared project blocks as Linear-compatible CSV."""
    share = await sharing_service.get_share_by_token(db, token)
    if not share:
        raise HTTPException(status_code=404, detail="Share link not found")

    data = await sharing_service.get_shared_project_data(db, share.project_id)
    project_name = data.get("project", {}).get("name", "project")
    csv_content = sharing_service.export_blocks_as_csv(data.get("blocks", []), project_name)

    return Response(
        content=csv_content.encode("utf-8"),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{project_name}-linear-export.csv"'},
    )
