from flask import Blueprint, g, jsonify, request
from app.auth import get_supabase_admin, require_auth
from app.services.nutrition_targets_service import (
    calculate_targets,
    get_latest_body_metric,
    get_user_nutrition_profile,
)

bp = Blueprint("nutrition", __name__)


@bp.route("/nutrition", methods=["POST"])
@require_auth
def create_nutrition_log():
    body = request.get_json(silent=True) or {}
    logged_at = body.get("logged_at")
    if not logged_at:
        return jsonify({"error": "logged_at is required"}), 400
    meal_items = (body.get("meal_items") or "").strip()
    if not meal_items:
        return jsonify({"error": "meal_items is required"}), 400
    if body.get("calories") in (None, ""):
        return jsonify({"error": "calories is required"}), 400
    if body.get("protein") in (None, ""):
        return jsonify({"error": "protein is required"}), 400

    row = {
        "tenant_id": g.tenant_id,
        "user_id": g.user_id,
        "logged_at": logged_at,
        "meal_items": meal_items,
    }
    for field in ("meal_type", "calories", "protein", "carbs", "fats"):
        if field in body:
            row[field] = body[field]

    sb = get_supabase_admin()
    result = sb.table("nutrition_logs").insert(row).execute()
    if not result.data:
        return jsonify({"error": "Insert failed"}), 500
    return jsonify({"nutrition_log": result.data[0]}), 201


@bp.route("/nutrition", methods=["GET"])
@require_auth
def list_nutrition_logs():
    sb = get_supabase_admin()
    query = (
        sb.table("nutrition_logs")
        .select("*")
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .order("logged_at", desc=True)
    )

    date_from = request.args.get("from")
    date_to = request.args.get("to")
    if date_from:
        query = query.gte("logged_at", date_from)
    if date_to:
        query = query.lte("logged_at", date_to)

    result = query.execute()
    profile = get_user_nutrition_profile(sb, g.tenant_id, g.user_id)
    metric = get_latest_body_metric(sb, g.tenant_id, g.user_id)
    targets = calculate_targets(profile, metric)
    return jsonify({"nutrition_logs": result.data or [], "targets": targets})


@bp.route("/nutrition/<int:log_id>", methods=["GET"])
@require_auth
def get_nutrition_log(log_id):
    sb = get_supabase_admin()
    result = (
        sb.table("nutrition_logs")
        .select("*")
        .eq("id", log_id)
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"nutrition_log": result.data})


@bp.route("/nutrition/<int:log_id>", methods=["PUT"])
@require_auth
def update_nutrition_log(log_id):
    body = request.get_json(silent=True) or {}
    allowed = {}
    for field in ("meal_type", "calories", "protein", "carbs", "fats", "logged_at", "meal_items"):
        if field in body:
            allowed[field] = body[field]
    if not allowed:
        return jsonify({"error": "No updatable fields provided"}), 400

    sb = get_supabase_admin()
    result = (
        sb.table("nutrition_logs")
        .update(allowed)
        .eq("id", log_id)
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"nutrition_log": result.data[0]})


@bp.route("/nutrition/<int:log_id>", methods=["DELETE"])
@require_auth
def delete_nutrition_log(log_id):
    sb = get_supabase_admin()
    result = (
        sb.table("nutrition_logs")
        .delete()
        .eq("id", log_id)
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Deleted"}), 200
