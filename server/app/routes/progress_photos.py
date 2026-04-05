from flask import Blueprint, g, jsonify, request
from app.auth import get_supabase_admin, require_auth

bp = Blueprint("progress_photos", __name__)


@bp.route("/progress-photos", methods=["POST"])
@require_auth
def create_progress_photo():
    body = request.get_json(silent=True) or {}
    image_url = body.get("image_url", "").strip()
    if not image_url:
        return jsonify({"error": "image_url is required"}), 400

    row = {
        "tenant_id": g.tenant_id,
        "user_id": g.user_id,
        "image_url": image_url,
    }

    sb = get_supabase_admin()
    result = sb.table("progress_photos").insert(row).execute()
    if not result.data:
        return jsonify({"error": "Insert failed"}), 500
    return jsonify({"progress_photo": result.data[0]}), 201


@bp.route("/progress-photos", methods=["GET"])
@require_auth
def list_progress_photos():
    sb = get_supabase_admin()
    result = (
        sb.table("progress_photos")
        .select("*")
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .order("uploaded_at", desc=True)
        .execute()
    )
    return jsonify({"progress_photos": result.data or []})


@bp.route("/progress-photos/<int:photo_id>", methods=["DELETE"])
@require_auth
def delete_progress_photo(photo_id):
    sb = get_supabase_admin()
    result = (
        sb.table("progress_photos")
        .delete()
        .eq("id", photo_id)
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Deleted"}), 200
