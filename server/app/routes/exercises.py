from flask import Blueprint, g, jsonify, request
from app.auth import get_supabase_admin, require_auth, require_role

bp = Blueprint("exercises", __name__)


@bp.route("/exercises", methods=["GET"])
@require_auth
def list_exercises():
    """Any authenticated user can browse the exercise library."""
    sb = get_supabase_admin()
    query = (
        sb.table("exercises")
        .select("*")
        .eq("tenant_id", g.tenant_id)
        .order("name")
    )
    muscle_group = request.args.get("muscle_group")
    if muscle_group:
        query = query.eq("muscle_group", muscle_group)
    result = query.execute()
    return jsonify({"exercises": result.data or []})


@bp.route("/exercises/<int:exercise_id>", methods=["GET"])
@require_auth
def get_exercise(exercise_id):
    sb = get_supabase_admin()
    result = (
        sb.table("exercises")
        .select("*")
        .eq("id", exercise_id)
        .eq("tenant_id", g.tenant_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"exercise": result.data})


@bp.route("/exercises", methods=["POST"])
@require_auth
@require_role("owner")
def create_exercise():
    """Only owners (and super_admin via hierarchy) can create exercises."""
    body = request.get_json(silent=True) or {}
    name = body.get("name", "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    row = {"tenant_id": g.tenant_id, "name": name}
    for field in ("muscle_group", "equipment", "instructions"):
        if field in body:
            row[field] = body[field]

    sb = get_supabase_admin()
    result = sb.table("exercises").insert(row).execute()
    if not result.data:
        return jsonify({"error": "Insert failed"}), 500
    return jsonify({"exercise": result.data[0]}), 201


@bp.route("/exercises/<int:exercise_id>", methods=["PUT"])
@require_auth
@require_role("owner")
def update_exercise(exercise_id):
    body = request.get_json(silent=True) or {}
    allowed = {}
    for field in ("name", "muscle_group", "equipment", "instructions"):
        if field in body:
            allowed[field] = body[field]
    if not allowed:
        return jsonify({"error": "No updatable fields provided"}), 400

    sb = get_supabase_admin()
    result = (
        sb.table("exercises")
        .update(allowed)
        .eq("id", exercise_id)
        .eq("tenant_id", g.tenant_id)
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"exercise": result.data[0]})


@bp.route("/exercises/<int:exercise_id>", methods=["DELETE"])
@require_auth
@require_role("owner")
def delete_exercise(exercise_id):
    sb = get_supabase_admin()
    result = (
        sb.table("exercises")
        .delete()
        .eq("id", exercise_id)
        .eq("tenant_id", g.tenant_id)
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Deleted"}), 200
