from flask import Blueprint, g, jsonify, request
from authentication import get_supabase_admin, require_auth

bp = Blueprint("routes", __name__)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "aura-fit-api"})


# ---------------------------------------------------------------------------
# User profile
# ---------------------------------------------------------------------------

@bp.route("/users/me", methods=["GET"])
@require_auth
def get_user():
    sb = get_supabase_admin()
    tenant_row = (
        sb.table("tenants")
        .select("id, name, logo_url, primary_color, secondary_color")
        .eq("id", g.tenant_id)
        .maybe_single()
        .execute()
    )
    return jsonify(
        {
            "user": {
                "id": g.user_id,
                "auth_id": g.auth_uid,
                "email": g.email,
                "tenant_id": g.tenant_id,
                "role": g.role,
            },
            "tenant": tenant_row.data if tenant_row.data else None,
        }
    )


@bp.route("/users/me", methods=["PUT"])
@require_auth
def update_user():
    body = request.get_json(silent=True) or {}

    allowed = {}
    if "email" in body:
        allowed["email"] = body["email"].strip()
    if "two_factor_enabled" in body:
        allowed["two_factor_enabled"] = bool(body["two_factor_enabled"])

    if not allowed:
        return jsonify({"error": "No updatable fields provided"}), 400

    sb = get_supabase_admin()
    result = (
        sb.table("users")
        .update(allowed)
        .eq("id", g.user_id)
        .eq("tenant_id", g.tenant_id)
        .execute()
    )

    if not result.data:
        return jsonify({"error": "Update failed"}), 500

    return jsonify({"user": result.data[0]})


@bp.route("/users/me", methods=["DELETE"])
@require_auth
def delete_user():
    sb = get_supabase_admin()
    sb.table("users").delete().eq("id", g.user_id).eq("tenant_id", g.tenant_id).execute()
    return jsonify({"message": "User deleted"}), 200


# ---------------------------------------------------------------------------
# Body metrics CRUD
# ---------------------------------------------------------------------------

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
