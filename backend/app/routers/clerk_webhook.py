"""
clerk_webhook.py — Handles Clerk webhook events for user sync.
Verifies webhook signatures using svix and syncs user data to the local database.
"""
import json

from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def _verify_webhook(payload: bytes, headers: dict) -> dict:
    """Verify Clerk webhook signature using svix and return parsed payload."""
    from svix.webhooks import Webhook

    wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
    try:
        data = wh.verify(payload, headers)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature",
        )
    return data


@router.post("/clerk", status_code=status.HTTP_200_OK)
async def clerk_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Process Clerk webhook events for user lifecycle management."""
    payload = await request.body()
    headers = {
        "svix-id": request.headers.get("svix-id", ""),
        "svix-timestamp": request.headers.get("svix-timestamp", ""),
        "svix-signature": request.headers.get("svix-signature", ""),
    }

    data = _verify_webhook(payload, headers)
    event_type = data.get("type", "")
    user_data = data.get("data", {})

    if event_type == "user.created":
        await _handle_user_created(user_data, db)
    elif event_type == "user.updated":
        await _handle_user_updated(user_data, db)
    elif event_type == "user.deleted":
        await _handle_user_deleted(user_data, db)

    return {"status": "ok"}


async def _handle_user_created(user_data: dict, db: AsyncSession) -> None:
    """Create a local user row from Clerk user data."""
    clerk_id = user_data.get("id", "")
    email = _extract_primary_email(user_data)

    if not email:
        return

    # Check if user already exists (by clerk_id or email)
    result = await db.execute(
        select(User).where(
            (User.clerk_user_id == clerk_id) | (User.email == email)
        )
    )
    existing = result.scalars().first()

    if existing:
        # Link existing user to Clerk
        existing.clerk_user_id = clerk_id
        if not existing.name and user_data.get("first_name"):
            existing.name = _build_name(user_data)
        if not existing.avatar_url and user_data.get("image_url"):
            existing.avatar_url = user_data["image_url"]
        existing.email_verified = True
    else:
        user = User(
            email=email,
            clerk_user_id=clerk_id,
            name=_build_name(user_data),
            display_name=_build_name(user_data),
            avatar_url=user_data.get("image_url"),
            email_verified=True,
            preferences={},
        )
        db.add(user)

    await db.flush()


async def _handle_user_updated(user_data: dict, db: AsyncSession) -> None:
    """Update local user row from Clerk user data."""
    clerk_id = user_data.get("id", "")
    result = await db.execute(
        select(User).where(User.clerk_user_id == clerk_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        # User doesn't exist locally yet — create them
        await _handle_user_created(user_data, db)
        return

    email = _extract_primary_email(user_data)
    if email:
        user.email = email

    name = _build_name(user_data)
    if name:
        user.name = name

    if user_data.get("image_url"):
        user.avatar_url = user_data["image_url"]

    await db.flush()


async def _handle_user_deleted(user_data: dict, db: AsyncSession) -> None:
    """Deactivate user when deleted from Clerk. Preserves data for billing/audit."""
    clerk_id = user_data.get("id", "")
    result = await db.execute(
        select(User).where(User.clerk_user_id == clerk_id)
    )
    user = result.scalar_one_or_none()

    if user:
        # Soft-deactivate: clear clerk_id so they can't log in
        user.clerk_user_id = None
        await db.flush()


def _extract_primary_email(user_data: dict) -> str:
    """Extract the primary email from Clerk user data."""
    email_addresses = user_data.get("email_addresses", [])
    primary_id = user_data.get("primary_email_address_id")

    for ea in email_addresses:
        if ea.get("id") == primary_id:
            return ea.get("email_address", "")

    # Fallback: first email
    if email_addresses:
        return email_addresses[0].get("email_address", "")

    return ""


def _build_name(user_data: dict) -> str:
    """Build a full name from Clerk user data."""
    first = user_data.get("first_name") or ""
    last = user_data.get("last_name") or ""
    return f"{first} {last}".strip()
