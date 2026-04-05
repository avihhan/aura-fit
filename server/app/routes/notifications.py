from flask import Blueprint, g, jsonify, request
from app.auth import get_supabase_admin, require_auth, require_role

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
