"""
webhooks.py — Inbound email webhook handler for Resend.
Receives emails sent to user@inbox.ideaforge.dev and creates inbox items.
"""
from fastapi import APIRouter, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.idea_inbox import IdeaInbox
from app.models.user import User

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/inbound-email", status_code=status.HTTP_200_OK)
async def inbound_email(request: Request):
    """
    Handle inbound email from Resend.
    Resend sends a POST with JSON body containing:
    - from: sender email
    - to: recipient (user's inbox_email)
    - subject: email subject
    - text / html: email body
    """
    try:
        payload = await request.json()
    except Exception:
        return {"status": "invalid payload"}

    to_email = payload.get("to", "")
    subject = payload.get("subject", "Untitled Idea")
    body = payload.get("text") or payload.get("html", "")
    sender = payload.get("from", "")

    if not to_email:
        return {"status": "no recipient"}

    # Normalize: Resend may send to as a list or string
    if isinstance(to_email, list):
        to_email = to_email[0] if to_email else ""

    # Look up the user by inbox_email
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.inbox_email == to_email)
        )
        user = result.scalar_one_or_none()
        if not user:
            return {"status": "unknown recipient"}

        item = IdeaInbox(
            user_id=user.id,
            subject=subject[:500],
            body=body[:10000] if body else None,
            source="email",
            sender_email=sender[:255] if sender else None,
        )
        db.add(item)
        await db.commit()

    return {"status": "ok"}
