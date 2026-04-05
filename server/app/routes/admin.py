from flask import Blueprint, g, jsonify, request
from app.auth import get_supabase_admin, require_auth, require_role

bp = Blueprint("admin", __name__)


@bp.route("/analytics", methods=["GET"])
@require_auth
@require_role("owner")
def tenant_analytics():
    """Aggregate stats for the current tenant (owner + super_admin)."""
    from app.auth import is_platform_admin

    tid = request.args.get("tenant_id", type=int) if is_platform_admin() else None
    tenant_id = tid or g.tenant_id

    sb = get_supabase_admin()

    members = (
        sb.table("users")
        .select("id", count="exact")
        .eq("tenant_id", tenant_id)
        .eq("role", "member")
        .execute()
    )
    workouts = (
        sb.table("workout_logs")
        .select("id", count="exact")
        .eq("tenant_id", tenant_id)
        .execute()
    )
    subs = (
        sb.table("subscriptions")
        .select("id", count="exact")
        .eq("tenant_id", tenant_id)
        .eq("status", "active")
        .execute()
    )

    return jsonify(
        {
            "tenant_id": tenant_id,
            "total_members": members.count or 0,
            "total_workouts": workouts.count or 0,
            "active_subscriptions": subs.count or 0,
        }
    )


@bp.route("/members", methods=["GET"])
@require_auth
@require_role("owner")
def list_members():
    """List all members in the current tenant."""
    sb = get_supabase_admin()
    result = (
        sb.table("users")
        .select("id, email, role, is_email_verified, created_at")
        .eq("tenant_id", g.tenant_id)
        .order("created_at", desc=True)
        .execute()
    )
    return jsonify({"members": result.data or []})


@bp.route("/branding", methods=["GET"])
@require_auth
@require_role("owner")
def get_branding():
    sb = get_supabase_admin()
    result = (
        sb.table("tenants")
        .select("id, name, logo_url, primary_color, secondary_color, custom_domain")
        .eq("id", g.tenant_id)
        .maybe_single()
        .execute()
    )
    return jsonify({"branding": result.data})


@bp.route("/branding", methods=["PUT"])
@require_auth
@require_role("owner")
def update_branding():
    body = request.get_json(silent=True) or {}
    allowed = {}
    for field in ("name", "logo_url", "primary_color", "secondary_color", "custom_domain"):
        if field in body:
            allowed[field] = body[field]
    if not allowed:
        return jsonify({"error": "No updatable fields provided"}), 400

    sb = get_supabase_admin()
    result = (
        sb.table("tenants")
        .update(allowed)
        .eq("id", g.tenant_id)
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Update failed"}), 500
    return jsonify({"branding": result.data[0]})


@bp.route("/members/<int:member_id>/report", methods=["GET"])
@require_auth
@require_role("owner")
def member_report(member_id):
    """Return a JSON summary for building a PDF client progress report."""
    sb = get_supabase_admin()

    user = (
        sb.table("users")
        .select("id, email, created_at")
        .eq("id", member_id)
        .eq("tenant_id", g.tenant_id)
        .maybe_single()
        .execute()
    )
    if not user or not user.data:
        return jsonify({"error": "Member not found"}), 404

    metrics = (
        sb.table("body_metrics")
        .select("weight, body_fat_percentage, recorded_at")
        .eq("user_id", member_id)
        .eq("tenant_id", g.tenant_id)
        .order("recorded_at", desc=True)
        .limit(30)
        .execute()
    )
    workouts = (
        sb.table("workout_logs")
        .select("id, workout_date, notes")
        .eq("user_id", member_id)
        .eq("tenant_id", g.tenant_id)
        .order("workout_date", desc=True)
        .limit(30)
        .execute()
    )
    nutrition = (
        sb.table("nutrition_logs")
        .select("calories, protein, carbs, fats, logged_at")
        .eq("user_id", member_id)
        .eq("tenant_id", g.tenant_id)
        .order("logged_at", desc=True)
        .limit(30)
        .execute()
    )
    goals = (
        sb.table("goals")
        .select("goal_type, target_value, status")
        .eq("user_id", member_id)
        .eq("tenant_id", g.tenant_id)
        .execute()
    )

    return jsonify({
        "member": user.data,
        "metrics": metrics.data or [],
        "workouts": workouts.data or [],
        "nutrition": nutrition.data or [],
        "goals": goals.data or [],
    })


@bp.route("/weekly-summary", methods=["POST"])
@require_auth
@require_role("owner")
def send_weekly_summaries():
    """Send weekly summary emails to all members of the tenant."""
    from app.services.email_service import send_weekly_summary
    from app.services.streak_service import calculate_streak

    sb = get_supabase_admin()
    members = (
        sb.table("users")
        .select("id, email")
        .eq("tenant_id", g.tenant_id)
        .eq("role", "member")
        .execute()
    )

    tenant = (
        sb.table("tenants")
        .select("name")
        .eq("id", g.tenant_id)
        .maybe_single()
        .execute()
    )
    tenant_name = tenant.data["name"] if tenant.data else "AuraFit"

    sent_count = 0
    for m in (members.data or []):
        workouts = (
            sb.table("workout_logs")
            .select("workout_date")
            .eq("user_id", m["id"])
            .eq("tenant_id", g.tenant_id)
            .execute()
        )
        dates = [w["workout_date"] for w in (workouts.data or [])]
        stats = calculate_streak(dates)

        nutrition = (
            sb.table("nutrition_logs")
            .select("calories")
            .eq("user_id", m["id"])
            .eq("tenant_id", g.tenant_id)
            .execute()
        )
        cals = [n["calories"] for n in (nutrition.data or []) if n.get("calories")]
        avg_cal = int(sum(cals) / len(cals)) if cals else 0

        result = send_weekly_summary(
            to=m["email"],
            user_name=m["email"].split("@")[0],
            workouts_count=stats["total_workouts"],
            streak=stats["current_streak"],
            calories_avg=avg_cal,
            tenant_name=tenant_name,
        )
        if result.get("sent"):
            sent_count += 1

    return jsonify({"sent": sent_count, "total_members": len(members.data or [])})


@bp.route("/members/<int:member_id>", methods=["GET"])
@require_auth
@require_role("owner")
def get_member(member_id):
    """Get a specific member's profile and recent metrics."""
    sb = get_supabase_admin()

    user = (
        sb.table("users")
        .select("id, email, role, is_email_verified, created_at")
        .eq("id", member_id)
        .eq("tenant_id", g.tenant_id)
        .maybe_single()
        .execute()
    )
    if not user or not user.data:
        return jsonify({"error": "Member not found"}), 404

    metrics = (
        sb.table("body_metrics")
        .select("*")
        .eq("user_id", member_id)
        .eq("tenant_id", g.tenant_id)
        .order("recorded_at", desc=True)
        .limit(10)
        .execute()
    )

    workouts = (
        sb.table("workout_logs")
        .select("id, workout_date, notes, created_at")
        .eq("user_id", member_id)
        .eq("tenant_id", g.tenant_id)
        .order("workout_date", desc=True)
        .limit(10)
        .execute()
    )

    return jsonify(
        {
            "member": user.data,
            "recent_metrics": metrics.data or [],
            "recent_workouts": workouts.data or [],
        }
    )
