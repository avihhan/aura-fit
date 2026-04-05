from flask import Blueprint, g, jsonify, request
from app.auth import get_supabase_admin, require_auth

bp = Blueprint("nutrition", __name__)


@bp.route("/nutrition", methods=["POST"])
@require_auth
def create_nutrition_log():
    body = request.get_json(silent=True) or {}
    logged_at = body.get("logged_at")
    if not logged_at:
        return jsonify({"error": "logged_at is required"}), 400

    row = {
        "tenant_id": g.tenant_id,
        "user_id": g.user_id,
        "logged_at": logged_at,
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
    return jsonify({"nutrition_logs": result.data or []})


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
    for field in ("meal_type", "calories", "protein", "carbs", "fats", "logged_at"):
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
