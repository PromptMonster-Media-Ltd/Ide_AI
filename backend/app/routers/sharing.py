"""
sharing.py — Project sharing endpoints for public/private link generation.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.project import Project
from app.models.project_share import ProjectShare
from app.models.share_comment import ShareComment
from app.models.share_rating import ShareRating
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


# --- Comments & Ratings (public, no auth) ---

class CommentCreate(BaseModel):
    author_name: str = Field(min_length=1, max_length=100)
    author_email: Optional[str] = Field(None, max_length=255)
    content: str = Field(min_length=1, max_length=2000)

class RatingCreate(BaseModel):
    author_name: str = Field(min_length=1, max_length=100)
    author_email: Optional[str] = Field(None, max_length=255)
    score: float = Field(ge=0, le=5)


@router.get("/public/{token}/comments")
async def get_comments(token: str, db: AsyncSession = Depends(get_db)):
    """Get all comments on a shared project."""
    share = await sharing_service.get_share_by_token(db, token)
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    result = await db.execute(
        select(ShareComment)
        .where(ShareComment.share_id == share.id)
        .order_by(ShareComment.created_at.desc())
    )
    comments = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "author_name": c.author_name,
            "content": c.content,
            "created_at": c.created_at.isoformat(),
        }
        for c in comments
    ]


@router.post("/public/{token}/comments", status_code=status.HTTP_201_CREATED)
async def add_comment(token: str, payload: CommentCreate, db: AsyncSession = Depends(get_db)):
    """Add a comment to a shared project."""
    share = await sharing_service.get_share_by_token(db, token)
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    if not share.allow_feedback:
        raise HTTPException(status_code=403, detail="Comments are disabled for this share")

    comment = ShareComment(
        share_id=share.id,
        author_name=payload.author_name,
        author_email=payload.author_email,
        content=payload.content,
    )
    db.add(comment)
    await db.flush()
    return {
        "id": str(comment.id),
        "author_name": comment.author_name,
        "content": comment.content,
        "created_at": comment.created_at.isoformat(),
    }


@router.get("/public/{token}/ratings")
async def get_ratings(token: str, db: AsyncSession = Depends(get_db)):
    """Get rating summary for a shared project."""
    share = await sharing_service.get_share_by_token(db, token)
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    result = await db.execute(
        select(
            sa_func.count(ShareRating.id).label("count"),
            sa_func.avg(ShareRating.score).label("average"),
        )
        .where(ShareRating.share_id == share.id)
    )
    row = result.one()
    return {
        "count": row.count or 0,
        "average": round(float(row.average), 1) if row.average else 0,
    }


@router.post("/public/{token}/ratings", status_code=status.HTTP_201_CREATED)
async def add_rating(token: str, payload: RatingCreate, db: AsyncSession = Depends(get_db)):
    """Rate a shared project (0-5 stars)."""
    share = await sharing_service.get_share_by_token(db, token)
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    if not share.allow_ratings:
        raise HTTPException(status_code=403, detail="Ratings are disabled for this share")

    rating = ShareRating(
        share_id=share.id,
        author_name=payload.author_name,
        author_email=payload.author_email,
        score=payload.score,
    )
    db.add(rating)
    await db.flush()
    return {"score": rating.score, "created_at": rating.created_at.isoformat()}
