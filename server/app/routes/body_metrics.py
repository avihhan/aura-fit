from flask import Blueprint, g, jsonify, request
from app.auth import get_supabase_admin, require_auth

bp = Blueprint("body_metrics", __name__)


def _normalize_height_fields(payload: dict) -> tuple[int | None, int | None, float | None]:
    feet = payload.get("height_feet")
    inches = payload.get("height_inches")
    legacy = payload.get("height")

    feet_num = int(feet) if feet not in (None, "") else None
    inches_num = int(inches) if inches not in (None, "") else None

    if feet_num is None and inches_num is None and legacy not in (None, ""):
        raw = float(legacy)
        if raw >= 96:
            total_inches = raw / 2.54
        else:
            total_inches = raw
        feet_num = int(total_inches // 12)
        inches_num = int(round(total_inches - feet_num * 12))

    if inches_num is not None and inches_num >= 12:
        feet_num = (feet_num or 0) + (inches_num // 12)
        inches_num = inches_num % 12

    legacy_height = None
    if feet_num is not None or inches_num is not None:
        legacy_height = float((feet_num or 0) * 12 + (inches_num or 0))

    return feet_num, inches_num, legacy_height


def _serialize_metric(row: dict) -> dict:
    feet = row.get("height_feet")
    inches = row.get("height_inches")
    if feet is None and inches is None and row.get("height") not in (None, ""):
        raw = float(row.get("height"))
        if raw >= 96:
            total_inches = raw / 2.54
        else:
            total_inches = raw
        feet = int(total_inches // 12)
        inches = int(round(total_inches - feet * 12))

    return {
        **row,
        "height_feet": feet,
        "height_inches": inches,
    }


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
    height_feet, height_inches, legacy_height = _normalize_height_fields(body)
    if height_feet is not None or height_inches is not None:
        row["height_feet"] = height_feet
        row["height_inches"] = height_inches
    if legacy_height is not None:
        row["height"] = legacy_height
    if "body_fat_percentage" in body:
        row["body_fat_percentage"] = body["body_fat_percentage"]

    sb = get_supabase_admin()
    result = sb.table("body_metrics").insert(row).execute()

    if not result.data:
        return jsonify({"error": "Insert failed"}), 500

    return jsonify({"body_metric": _serialize_metric(result.data[0])}), 201


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
    return jsonify({"body_metrics": [_serialize_metric(r) for r in (result.data or [])]})


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

    return jsonify({"body_metric": _serialize_metric(result.data)})


@bp.route("/body-metrics/<int:metric_id>", methods=["PUT"])
@require_auth
def update_body_metric(metric_id):
    body = request.get_json(silent=True) or {}

    allowed = {}
    for field in ("weight", "body_fat_percentage", "recorded_at"):
        if field in body:
            allowed[field] = body[field]
    if any(k in body for k in ("height", "height_feet", "height_inches")):
        height_feet, height_inches, legacy_height = _normalize_height_fields(body)
        allowed["height_feet"] = height_feet
        allowed["height_inches"] = height_inches
        allowed["height"] = legacy_height

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

    return jsonify({"body_metric": _serialize_metric(result.data[0])})


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
