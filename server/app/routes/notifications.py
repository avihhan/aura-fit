import os
from datetime import date

from flask import Blueprint, g, jsonify, request
from app.auth import get_supabase_admin, require_auth, require_role
from app.services.user_notifications_service import send_daily_log_reminder_email

bp = Blueprint("notifications", __name__)


@bp.route("/notifications", methods=["GET"])
@require_auth
def list_notifications():
    sb = get_supabase_admin()
    result = (
        sb.table("notifications")
        .select("*")
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return jsonify({"notifications": result.data or []})


@bp.route("/notifications/unread-count", methods=["GET"])
@require_auth
def unread_count():
    sb = get_supabase_admin()
    result = (
        sb.table("notifications")
        .select("id", count="exact")
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .eq("is_read", False)
        .execute()
    )
    return jsonify({"unread_count": result.count or 0})


@bp.route("/notifications/<int:notif_id>/read", methods=["PUT"])
@require_auth
def mark_read(notif_id):
    sb = get_supabase_admin()
    result = (
        sb.table("notifications")
        .update({"is_read": True})
        .eq("id", notif_id)
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"notification": result.data[0]})


@bp.route("/notifications", methods=["POST"])
@require_auth
@require_role("owner")
def send_notification():
    """Owner sends a notification to a specific user in their tenant."""
    body = request.get_json(silent=True) or {}
    user_id = body.get("user_id")
    title = body.get("title", "").strip()
    message = body.get("message", "").strip()

    if not user_id or not title:
        return jsonify({"error": "user_id and title are required"}), 400

    sb = get_supabase_admin()
    result = (
        sb.table("notifications")
        .insert(
            {
                "tenant_id": g.tenant_id,
                "user_id": user_id,
                "title": title,
                "message": message,
            }
        )
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Insert failed"}), 500
    return jsonify({"notification": result.data[0]}), 201


@bp.route("/notifications/reminders/daily", methods=["POST"])
def send_daily_log_reminders():
    """
    Scheduler-safe endpoint to send daily missing-log reminders.
    Uses X-Cron-Token header for authorization.
    """
    token_expected = os.environ.get("REMINDER_CRON_TOKEN", "").strip()
    token_received = request.headers.get("X-Cron-Token", "").strip()
    if not token_expected:
        return jsonify({"error": "REMINDER_CRON_TOKEN is not configured"}), 500
    if token_received != token_expected:
        return jsonify({"error": "Unauthorized"}), 401

    today = date.today().isoformat()
    sb = get_supabase_admin()
    users = (
        sb.table("users")
        .select("id, tenant_id")
        .eq("role", "member")
        .eq("email_notifications_enabled", True)
        .execute()
    )

    sent_workout = 0
    sent_nutrition = 0
    for user in (users.data or []):
        user_id = int(user["id"])
        tenant_id = int(user["tenant_id"])

        has_workout = (
            sb.table("workout_logs")
            .select("id")
            .eq("tenant_id", tenant_id)
            .eq("user_id", user_id)
            .eq("workout_date", today)
            .limit(1)
            .execute()
        )
        if not (has_workout.data or []):
            result = send_daily_log_reminder_email(
                sb,
                tenant_id=tenant_id,
                user_id=user_id,
                reminder_type="workout",
                target_date=date.fromisoformat(today),
            )
            if result.get("sent"):
                sent_workout += 1

        has_nutrition = (
            sb.table("nutrition_logs")
            .select("id")
            .eq("tenant_id", tenant_id)
            .eq("user_id", user_id)
            .gte("logged_at", f"{today}T00:00:00")
            .lte("logged_at", f"{today}T23:59:59.999999")
            .limit(1)
            .execute()
        )
        if not (has_nutrition.data or []):
            result = send_daily_log_reminder_email(
                sb,
                tenant_id=tenant_id,
                user_id=user_id,
                reminder_type="nutrition",
                target_date=date.fromisoformat(today),
            )
            if result.get("sent"):
                sent_nutrition += 1

    return jsonify(
        {
            "date": today,
            "users_checked": len(users.data or []),
            "workout_reminders_sent": sent_workout,
            "nutrition_reminders_sent": sent_nutrition,
        }
    )
