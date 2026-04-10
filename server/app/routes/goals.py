from flask import Blueprint, g, jsonify, request
from app.auth import get_supabase_admin, require_auth
from app.services.user_notifications_service import send_plan_opt_in_email

bp = Blueprint("goals", __name__)


@bp.route("/goals", methods=["POST"])
@require_auth
def create_goal():
    body = request.get_json(silent=True) or {}
    goal_type = body.get("goal_type", "").strip()
    if not goal_type:
        return jsonify({"error": "goal_type is required"}), 400

    row = {
        "tenant_id": g.tenant_id,
        "user_id": g.user_id,
        "goal_type": goal_type,
        "status": body.get("status", "active"),
    }
    for field in ("target_value", "start_date", "end_date"):
        if field in body:
            row[field] = body[field]

    sb = get_supabase_admin()
    result = sb.table("goals").insert(row).execute()
    if not result.data:
        return jsonify({"error": "Insert failed"}), 500

    goal = result.data[0]
    if str(goal.get("status", "")).lower() == "active":
        send_plan_opt_in_email(
            sb,
            tenant_id=g.tenant_id,
            user_id=g.user_id,
            goal_type=goal.get("goal_type") or "fitness",
        )
    return jsonify({"goal": goal}), 201


@bp.route("/goals", methods=["GET"])
@require_auth
def list_goals():
    sb = get_supabase_admin()
    query = (
        sb.table("goals")
        .select("*")
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
    )
    status = request.args.get("status")
    if status:
        query = query.eq("status", status)
    result = query.execute()
    return jsonify({"goals": result.data or []})


@bp.route("/goals/<int:goal_id>", methods=["GET"])
@require_auth
def get_goal(goal_id):
    sb = get_supabase_admin()
    result = (
        sb.table("goals")
        .select("*")
        .eq("id", goal_id)
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"goal": result.data})


@bp.route("/goals/<int:goal_id>", methods=["PUT"])
@require_auth
def update_goal(goal_id):
    body = request.get_json(silent=True) or {}
    allowed = {}
    for field in ("goal_type", "target_value", "start_date", "end_date", "status"):
        if field in body:
            allowed[field] = body[field]
    if not allowed:
        return jsonify({"error": "No updatable fields provided"}), 400

    sb = get_supabase_admin()
    result = (
        sb.table("goals")
        .update(allowed)
        .eq("id", goal_id)
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"goal": result.data[0]})


@bp.route("/goals/<int:goal_id>", methods=["DELETE"])
@require_auth
def delete_goal(goal_id):
    sb = get_supabase_admin()
    result = (
        sb.table("goals")
        .delete()
        .eq("id", goal_id)
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Deleted"}), 200
