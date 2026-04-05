from flask import Blueprint, g, jsonify, request
from app.auth import get_supabase_admin, require_auth, require_role

bp = Blueprint("subscriptions", __name__)


@bp.route("/subscriptions/me", methods=["GET"])
@require_auth
def my_subscription():
    """Get the current user's active subscription."""
    sb = get_supabase_admin()
    result = (
        sb.table("subscriptions")
        .select("*")
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .eq("status", "active")
        .maybe_single()
        .execute()
    )
    return jsonify({"subscription": result.data})


@bp.route("/subscriptions", methods=["GET"])
@require_auth
@require_role("owner")
def list_subscriptions():
    """Owner views all subscriptions in their tenant."""
    sb = get_supabase_admin()
    result = (
        sb.table("subscriptions")
        .select("*")
        .eq("tenant_id", g.tenant_id)
        .order("start_date", desc=True)
        .execute()
    )
    return jsonify({"subscriptions": result.data or []})


@bp.route("/subscriptions", methods=["POST"])
@require_auth
@require_role("owner")
def create_subscription():
    body = request.get_json(silent=True) or {}
    user_id = body.get("user_id")
    tier = body.get("tier", "").strip()
    start_date = body.get("start_date")

    if not user_id or not tier or not start_date:
        return (
            jsonify({"error": "user_id, tier, and start_date are required"}),
            400,
        )

    sb = get_supabase_admin()
    result = (
        sb.table("subscriptions")
        .insert(
            {
                "tenant_id": g.tenant_id,
                "user_id": user_id,
                "tier": tier,
                "status": "active",
                "start_date": start_date,
                "end_date": body.get("end_date"),
            }
        )
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Insert failed"}), 500
    return jsonify({"subscription": result.data[0]}), 201


@bp.route("/subscriptions/<int:sub_id>", methods=["PUT"])
@require_auth
@require_role("owner")
def update_subscription(sub_id):
    body = request.get_json(silent=True) or {}
    allowed = {}
    for field in ("tier", "status", "end_date"):
        if field in body:
            allowed[field] = body[field]
    if not allowed:
        return jsonify({"error": "No updatable fields provided"}), 400

    sb = get_supabase_admin()
    result = (
        sb.table("subscriptions")
        .update(allowed)
        .eq("id", sub_id)
        .eq("tenant_id", g.tenant_id)
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"subscription": result.data[0]})
