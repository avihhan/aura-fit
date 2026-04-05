from flask import Blueprint, g, jsonify, request
from app.auth import get_supabase_admin, require_auth

bp = Blueprint("workouts", __name__)


# ---------------------------------------------------------------------------
# Workout logs
# ---------------------------------------------------------------------------


@bp.route("/workouts", methods=["POST"])
@require_auth
def create_workout():
    body = request.get_json(silent=True) or {}
    workout_date = body.get("workout_date")
    if not workout_date:
        return jsonify({"error": "workout_date is required"}), 400

    row = {
        "tenant_id": g.tenant_id,
        "user_id": g.user_id,
        "workout_date": workout_date,
    }
    if "notes" in body:
        row["notes"] = body["notes"]

    sb = get_supabase_admin()
    result = sb.table("workout_logs").insert(row).execute()
    if not result.data:
        return jsonify({"error": "Insert failed"}), 500
    return jsonify({"workout": result.data[0]}), 201


@bp.route("/workouts", methods=["GET"])
@require_auth
def list_workouts():
    sb = get_supabase_admin()
    result = (
        sb.table("workout_logs")
        .select("*")
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .order("workout_date", desc=True)
        .execute()
    )
    return jsonify({"workouts": result.data or []})


@bp.route("/workouts/<int:workout_id>", methods=["GET"])
@require_auth
def get_workout(workout_id):
    sb = get_supabase_admin()
    workout = (
        sb.table("workout_logs")
        .select("*")
        .eq("id", workout_id)
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .maybe_single()
        .execute()
    )
    if not workout or not workout.data:
        return jsonify({"error": "Not found"}), 404

    exercises = (
        sb.table("workout_exercises")
        .select("*")
        .eq("workout_log_id", workout_id)
        .execute()
    )
    return jsonify({
        "workout": workout.data,
        "exercises": exercises.data or [],
    })


@bp.route("/workouts/<int:workout_id>", methods=["PUT"])
@require_auth
def update_workout(workout_id):
    body = request.get_json(silent=True) or {}
    allowed = {}
    for field in ("workout_date", "notes"):
        if field in body:
            allowed[field] = body[field]
    if not allowed:
        return jsonify({"error": "No updatable fields provided"}), 400

    sb = get_supabase_admin()
    result = (
        sb.table("workout_logs")
        .update(allowed)
        .eq("id", workout_id)
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"workout": result.data[0]})


@bp.route("/workouts/<int:workout_id>", methods=["DELETE"])
@require_auth
def delete_workout(workout_id):
    sb = get_supabase_admin()
    sb.table("workout_exercises").delete().eq(
        "workout_log_id", workout_id
    ).execute()
    result = (
        sb.table("workout_logs")
        .delete()
        .eq("id", workout_id)
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Deleted"}), 200


# ---------------------------------------------------------------------------
# Workout exercises (sub-resource of a workout log)
# ---------------------------------------------------------------------------


@bp.route("/workouts/<int:workout_id>/exercises", methods=["POST"])
@require_auth
def add_exercise(workout_id):
    sb = get_supabase_admin()
    workout = (
        sb.table("workout_logs")
        .select("id")
        .eq("id", workout_id)
        .eq("tenant_id", g.tenant_id)
        .eq("user_id", g.user_id)
        .maybe_single()
        .execute()
    )
    if not workout or not workout.data:
        return jsonify({"error": "Workout not found"}), 404

    body = request.get_json(silent=True) or {}
    exercise_name = body.get("exercise_name", "").strip()
    if not exercise_name:
        return jsonify({"error": "exercise_name is required"}), 400

    row = {"workout_log_id": workout_id, "exercise_name": exercise_name}
    for field in ("sets", "reps", "weight", "duration_minutes", "rpe"):
        if field in body:
            row[field] = body[field]

    result = sb.table("workout_exercises").insert(row).execute()
    if not result.data:
        return jsonify({"error": "Insert failed"}), 500
    return jsonify({"exercise": result.data[0]}), 201


@bp.route("/workouts/<int:workout_id>/exercises", methods=["GET"])
@require_auth
def list_exercises_for_workout(workout_id):
    sb = get_supabase_admin()
    result = (
        sb.table("workout_exercises")
        .select("*")
        .eq("workout_log_id", workout_id)
        .execute()
    )
    return jsonify({"exercises": result.data or []})


@bp.route(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>", methods=["PUT"]
)
@require_auth
def update_exercise(workout_id, exercise_id):
    body = request.get_json(silent=True) or {}
    allowed = {}
    for field in (
        "exercise_name",
        "sets",
        "reps",
        "weight",
        "duration_minutes",
        "rpe",
    ):
        if field in body:
            allowed[field] = body[field]
    if not allowed:
        return jsonify({"error": "No updatable fields provided"}), 400

    sb = get_supabase_admin()
    result = (
        sb.table("workout_exercises")
        .update(allowed)
        .eq("id", exercise_id)
        .eq("workout_log_id", workout_id)
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"exercise": result.data[0]})


@bp.route(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>",
    methods=["DELETE"],
)
@require_auth
def delete_exercise(workout_id, exercise_id):
    sb = get_supabase_admin()
    result = (
        sb.table("workout_exercises")
        .delete()
        .eq("id", exercise_id)
        .eq("workout_log_id", workout_id)
        .execute()
    )
    if not result.data:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Deleted"}), 200
