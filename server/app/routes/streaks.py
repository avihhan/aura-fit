from flask import Blueprint, g, jsonify
from app.auth import get_supabase_admin, require_auth

bp = Blueprint("streaks", __name__)


@bp.route("/streaks", methods=["GET"])
@require_auth
def get_streaks():
    """Return the current user's workout streak, badges, and a motivational message."""
    from app.services.streak_service import (
        calculate_streak,
        earned_badges,
        get_motivation,
    )

    sb = get_supabase_admin()
    rows = (
        sb.table("workout_logs")
        .select("workout_date")
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .execute()
    )
    dates = [r["workout_date"] for r in (rows.data or [])]

    stats = calculate_streak(dates)
    badges = earned_badges(stats["current_streak"], stats["total_workouts"])
    motivation = get_motivation(stats["current_streak"])

    return jsonify({
        **stats,
        "badges": badges,
        "motivation": motivation,
    })
