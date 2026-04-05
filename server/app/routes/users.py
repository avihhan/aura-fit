from flask import Blueprint, g, jsonify, request
from app.auth import get_supabase_admin, require_auth

bp = Blueprint("users", __name__)


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
    sb.table("users").delete().eq("id", g.user_id).eq(
        "tenant_id", g.tenant_id
    ).execute()
    return jsonify({"message": "User deleted"}), 200
