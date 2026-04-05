"""
Email Service — sends transactional emails via SendGrid.

Set SENDGRID_API_KEY and SENDGRID_FROM_EMAIL in .env.
When keys are missing, emails are logged to stdout for local dev.
"""

from __future__ import annotations

import os
from typing import Any


def _sendgrid_client():
    try:
        import sendgrid  # noqa: F811
        from sendgrid.helpers.mail import Content, Email, Mail, To  # noqa: F401
    except ImportError:
        return None, None
    key = os.getenv("SENDGRID_API_KEY", "")
    if not key:
        return None, None
    return sendgrid.SendGridAPIClient(api_key=key), {
        "Email": Email,
        "To": To,
        "Content": Content,
        "Mail": Mail,
    }


def send_email(*, to: str, subject: str, html_body: str) -> dict[str, Any]:
    """
    Send a single email. Returns {"sent": True/False, "detail": ...}.
    Falls back to console logging when SendGrid is not configured.
    """
    client, helpers = _sendgrid_client()
    from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@aurafit.app")

    if client is None:
        print(f"[EMAIL-DEV] To={to}  Subject={subject}")
        print(f"[EMAIL-DEV] Body preview: {html_body[:200]}")
        return {"sent": False, "detail": "SendGrid not configured — logged to console"}

    mail = helpers["Mail"](
        from_email=helpers["Email"](from_email),
        to_emails=helpers["To"](to),
        subject=subject,
        html_content=helpers["Content"]("text/html", html_body),
    )
    try:
        response = client.send(mail)
        return {"sent": True, "status_code": response.status_code}
    except Exception as exc:
        return {"sent": False, "detail": str(exc)}


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------


def send_weekly_summary(
    *,
    to: str,
    user_name: str,
    workouts_count: int,
    streak: int,
    calories_avg: int,
    tenant_name: str = "AuraFit",
) -> dict[str, Any]:
    """Build and send a weekly summary email."""
    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto;padding:24px;">
      <h2 style="color:#6c63ff;">Your Weekly Summary</h2>
      <p>Hey {user_name},</p>
      <p>Here's how your week went at <strong>{tenant_name}</strong>:</p>
      <table style="width:100%;border-collapse:collapse;margin:16px 0;">
        <tr>
          <td style="padding:8px;border-bottom:1px solid #eee;"><strong>Workouts</strong></td>
          <td style="padding:8px;border-bottom:1px solid #eee;text-align:right;">{workouts_count}</td>
        </tr>
        <tr>
          <td style="padding:8px;border-bottom:1px solid #eee;"><strong>Current Streak</strong></td>
          <td style="padding:8px;border-bottom:1px solid #eee;text-align:right;">{streak} days</td>
        </tr>
        <tr>
          <td style="padding:8px;"><strong>Avg Daily Calories</strong></td>
          <td style="padding:8px;text-align:right;">{calories_avg} kcal</td>
        </tr>
      </table>
      <p>Keep it up! Every day counts.</p>
      <p style="color:#888;font-size:12px;">— The {tenant_name} Team</p>
    </div>
    """
    return send_email(
        to=to,
        subject=f"Your {tenant_name} Weekly Summary",
        html_body=html,
    )


def send_streak_milestone(
    *,
    to: str,
    user_name: str,
    streak: int,
    badge_label: str,
) -> dict[str, Any]:
    """Notify the user when they unlock a new streak badge."""
    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto;padding:24px;text-align:center;">
      <h2 style="color:#6c63ff;">New Badge Unlocked!</h2>
      <p style="font-size:48px;margin:8px 0;">🏆</p>
      <p>Congratulations {user_name}!</p>
      <p>You've earned the <strong>{badge_label}</strong> badge with a
         <strong>{streak}-day</strong> workout streak.</p>
      <p>Keep pushing!</p>
    </div>
    """
    return send_email(
        to=to,
        subject=f"You earned the {badge_label} badge!",
        html_body=html,
    )
