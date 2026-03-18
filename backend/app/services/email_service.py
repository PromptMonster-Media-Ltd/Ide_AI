"""
email_service.py — Email sending via Resend.
Provides a generic send_email() helper for transactional emails.
"""
from __future__ import annotations

import resend

from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY


async def send_email(to: str, subject: str, html: str) -> dict | None:
    """Send a transactional email via Resend. Returns the Resend response or None on failure."""
    if not settings.RESEND_API_KEY:
        # Silently skip in dev when no key is configured
        print("[email_service] No RESEND_API_KEY configured — skipping email send")
        return None
    try:
        params: resend.Emails.SendParams = {
            "from": f"Ide/AI <{settings.FROM_EMAIL}>",
            "to": [to],
            "subject": subject,
            "html": html,
        }
        result = resend.Emails.send(params)
        print(f"[email_service] Sent email to {to} — id: {result.get('id', 'unknown')}")
        return result
    except Exception as exc:
        # Log the full error so it shows in Railway logs
        import traceback
        print(f"[email_service] Failed to send email to {to}: {exc}")
        traceback.print_exc()
        return None


