from flask import Blueprint, g, jsonify, request
from app.auth import get_supabase_admin, require_auth

bp = Blueprint("body_metrics", __name__)


@bp.route("/body-metrics", methods=["POST"])
@require_auth
def create_body_metric():
    body = request.get_json(silent=True) or {}

    recorded_at = body.get("recorded_at")
    if not recorded_at:
        return jsonify({"error": "recorded_at is required"}), 400

    row = {
        "tenant_id": g.tenant_id,
        "user_id": g.user_id,
        "recorded_at": recorded_at,
    }
    if "weight" in body:
        row["weight"] = body["weight"]
    if "height" in body:
        row["height"] = body["height"]
    if "body_fat_percentage" in body:
        row["body_fat_percentage"] = body["body_fat_percentage"]

    sb = get_supabase_admin()
    result = sb.table("body_metrics").insert(row).execute()

    if not result.data:
        return jsonify({"error": "Insert failed"}), 500

    return jsonify({"body_metric": result.data[0]}), 201


@bp.route("/body-metrics", methods=["GET"])
@require_auth
def list_body_metrics():
    sb = get_supabase_admin()
    result = (
        sb.table("body_metrics")
        .select("*")
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .order("recorded_at", desc=True)
        .execute()
    )
    return jsonify({"body_metrics": result.data or []})


@bp.route("/body-metrics/<int:metric_id>", methods=["GET"])
@require_auth
def get_body_metric(metric_id):
    sb = get_supabase_admin()
    result = (
        sb.table("body_metrics")
        .select("*")
        .eq("id", metric_id)
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .maybe_single()
        .execute()
    )

    if not result.data:
        return jsonify({"error": "Not found"}), 404

    return jsonify({"body_metric": result.data})


@bp.route("/body-metrics/<int:metric_id>", methods=["PUT"])
@require_auth
def update_body_metric(metric_id):
    body = request.get_json(silent=True) or {}

    allowed = {}
    for field in ("weight", "height", "body_fat_percentage", "recorded_at"):
        if field in body:
            allowed[field] = body[field]

    if not allowed:
        return jsonify({"error": "No updatable fields provided"}), 400

    sb = get_supabase_admin()
    result = (
        sb.table("body_metrics")
        .update(allowed)
        .eq("id", metric_id)
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .execute()
    )

    if not result.data:
        return jsonify({"error": "Not found or update failed"}), 404

    return jsonify({"body_metric": result.data[0]})


@bp.route("/body-metrics/<int:metric_id>", methods=["DELETE"])
@require_auth
def delete_body_metric(metric_id):
    sb = get_supabase_admin()
    result = (
        sb.table("body_metrics")
        .delete()
        .eq("id", metric_id)
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .execute()
    )

    if not result.data:
        return jsonify({"error": "Not found"}), 404

    return jsonify({"message": "Deleted"}), 200
