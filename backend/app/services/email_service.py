"""
email_service.py — Email sending via Resend.
Provides send_verification_email() for auth flow and a generic send_email() helper.
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
            "from_": f"ideaFORGE <{settings.FROM_EMAIL}>",
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


async def send_verification_email(to: str, code: str) -> dict | None:
    """Send a 6-digit verification code email."""
    subject = f"{code} is your ideaFORGE verification code"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px;">
      <div style="text-align: center; margin-bottom: 24px;">
        <h1 style="color: #ffffff; font-size: 24px; margin: 0;">ideaFORGE</h1>
      </div>
      <div style="background: #1a1a24; border-radius: 12px; padding: 32px; border: 1px solid rgba(255,255,255,0.1);">
        <p style="color: #e0e0e0; font-size: 14px; margin: 0 0 16px;">
          Enter this code to verify your email address:
        </p>
        <div style="text-align: center; margin: 24px 0;">
          <span style="font-family: monospace; font-size: 36px; font-weight: bold; color: #00E5FF; letter-spacing: 8px;">
            {code}
          </span>
        </div>
        <p style="color: #888; font-size: 12px; margin: 16px 0 0;">
          This code expires in 10 minutes. If you didn't create an account, you can ignore this email.
        </p>
      </div>
    </div>
    """
    return await send_email(to, subject, html)
