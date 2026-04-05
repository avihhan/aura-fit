from flask import Blueprint, g, jsonify, request
from app.auth import get_supabase_admin, require_auth

bp = Blueprint("favorites", __name__)


@bp.route("/favorites", methods=["GET"])
@require_auth
def list_favorites():
    sb = get_supabase_admin()
    result = (
        sb.table("favorites")
        .select("*, exercises(id, name, muscle_group, equipment)")
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return jsonify({"favorites": result.data or []})


@bp.route("/favorites", methods=["POST"])
@require_auth
def add_favorite():
    body = request.get_json(silent=True) or {}
    exercise_id = body.get("exercise_id")
    if not exercise_id:
        return jsonify({"error": "exercise_id is required"}), 400

    sb = get_supabase_admin()
    result = (
        sb.table("favorites")
        .insert(
            {
                "tenant_id": g.tenant_id,
                "user_id": g.user_id,
                "exercise_id": exercise_id,
            }
        )
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Insert failed"}), 500
    return jsonify({"favorite": result.data[0]}), 201


@bp.route("/favorites/<int:exercise_id>", methods=["DELETE"])
@require_auth
def remove_favorite(exercise_id):
    sb = get_supabase_admin()
    result = (
        sb.table("favorites")
        .delete()
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .eq("exercise_id", exercise_id)
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Removed"}), 200
