from __future__ import annotations

from datetime import date
from typing import Any

from app.services.email_service import send_email


def get_user_notification_settings(
    sb: Any, *, tenant_id: int, user_id: int
) -> dict[str, Any] | None:
    result = (
        sb.table("users")
        .select("id, email, email_notifications_enabled")
        .eq("tenant_id", tenant_id)
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    return result.data if result and result.data else None


def send_user_email_if_enabled(
    sb: Any,
    *,
    tenant_id: int,
    user_id: int,
    subject: str,
    html_body: str,
) -> dict[str, Any]:
    user = get_user_notification_settings(sb, tenant_id=tenant_id, user_id=user_id)
    if not user:
        return {"sent": False, "detail": "User not found"}
    if not user.get("email_notifications_enabled", True):
        return {"sent": False, "detail": "Email notifications disabled"}
    email = (user.get("email") or "").strip()
    if not email:
        return {"sent": False, "detail": "No email address"}
    return send_email(to=email, subject=subject, html_body=html_body)


def send_plan_opt_in_email(sb: Any, *, tenant_id: int, user_id: int, goal_type: str) -> dict[str, Any]:
    return send_user_email_if_enabled(
        sb,
        tenant_id=tenant_id,
        user_id=user_id,
        subject="Your plan is active",
        html_body=(
            "<div style='font-family:sans-serif;max-width:480px;margin:auto;padding:20px;'>"
            "<h2 style='color:#6c63ff;'>Plan Activated</h2>"
            f"<p>You opted into a <strong>{goal_type}</strong> plan.</p>"
            "<p>We will keep you on track with reminders and progress nudges.</p>"
            "</div>"
        ),
    )


def send_workout_completion_email(
    sb: Any,
    *,
    tenant_id: int,
    user_id: int,
    workout_date: str,
    exercise_name: str,
) -> dict[str, Any]:
    return send_user_email_if_enabled(
        sb,
        tenant_id=tenant_id,
        user_id=user_id,
        subject="Workout logged successfully",
        html_body=(
            "<div style='font-family:sans-serif;max-width:480px;margin:auto;padding:20px;'>"
            "<h2 style='color:#22c55e;'>Workout Completed</h2>"
            f"<p>Great job. Your workout for <strong>{workout_date}</strong> is logged.</p>"
            f"<p>Latest exercise added: <strong>{exercise_name}</strong>.</p>"
            "</div>"
        ),
    )


def send_daily_log_reminder_email(
    sb: Any,
    *,
    tenant_id: int,
    user_id: int,
    reminder_type: str,
    target_date: date,
) -> dict[str, Any]:
    friendly = "workout log" if reminder_type == "workout" else "nutrition log"
    return send_user_email_if_enabled(
        sb,
        tenant_id=tenant_id,
        user_id=user_id,
        subject=f"Reminder: complete your {friendly}",
        html_body=(
            "<div style='font-family:sans-serif;max-width:480px;margin:auto;padding:20px;'>"
            "<h2 style='color:#f59e0b;'>Daily Reminder</h2>"
            f"<p>You have not filled your <strong>{friendly}</strong> for {target_date.isoformat()}.</p>"
            "<p>Open AuraFit and log it to stay consistent.</p>"
            "</div>"
        ),
    )
