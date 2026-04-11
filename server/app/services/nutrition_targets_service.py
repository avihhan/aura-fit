from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

ACTIVITY_MULTIPLIER = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "very_active": 1.725,
    "extra_active": 1.9,
}

GOAL_CALORIE_ADJUSTMENT = {
    "lose": -350,
    "maintain": 0,
    "gain": 300,
}

PROTEIN_FACTOR_BY_ACTIVITY = {
    "sedentary": 0.7,
    "light": 0.8,
    "moderate": 0.9,
    "very_active": 1.0,
    "extra_active": 1.1,
}


def _result_data(result: Any) -> list[dict[str, Any]]:
    if result is None:
        return []
    data = getattr(result, "data", None)
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    return []


def _to_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _is_missing_response(exc: Exception) -> bool:
    text = str(exc).lower()
    return "missing response" in text and (
        "'code': '204'" in text or '"code": "204"' in text
    )


def _is_relation_missing(exc: Exception) -> bool:
    text = str(exc).lower()
    return "could not find the table" in text or "does not exist" in text


def _safe_execute(query) -> Any:
    try:
        return query.execute()
    except Exception as exc:
        if _is_missing_response(exc) or _is_relation_missing(exc):
            return None
        raise


def _normalize_profile_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None
    return {
        **row,
        "sex": (row.get("sex") or "").strip().lower(),
        "activity_level": (row.get("activity_level") or "").strip().lower(),
        "goal": (row.get("goal") or "").strip().lower(),
        "age_years": _to_int(row.get("age_years")),
    }


def _normalize_metric_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not row:
        return None
    return {
        **row,
        "weight": _to_float(row.get("weight")),
        "height": _to_float(row.get("height")),
    }


def get_user_nutrition_profile(sb, tenant_id: int, user_id: int) -> dict[str, Any] | None:
    result = _safe_execute(
        sb.table("user_nutrition_profiles")
        .select("*")
        .eq("tenant_id", tenant_id)
        .eq("user_id", user_id)
        .maybe_single()
    )
    data = getattr(result, "data", None) if result else None
    if not isinstance(data, dict):
        return None
    return _normalize_profile_row(data)


def upsert_user_nutrition_profile(sb, tenant_id: int, user_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    row = {
        "tenant_id": tenant_id,
        "user_id": user_id,
        "sex": (payload.get("sex") or "").strip().lower(),
        "age_years": payload.get("age_years"),
        "activity_level": (payload.get("activity_level") or "").strip().lower(),
        "goal": (payload.get("goal") or "").strip().lower(),
        "updated_at": datetime.now(UTC).isoformat(),
    }
    result = _safe_execute(
        sb.table("user_nutrition_profiles")
        .upsert(row, on_conflict="tenant_id,user_id")
    )
    if result is None:
        raise RuntimeError(
            "Nutrition profile table unavailable. Run latest migrations and reload Supabase schema."
        )
    data = _result_data(result)
    if data:
        return _normalize_profile_row(data[0]) or row
    return _normalize_profile_row(row) or row


def get_latest_body_metric(sb, tenant_id: int, user_id: int) -> dict[str, Any] | None:
    result = _safe_execute(
        sb.table("body_metrics")
        .select("id,weight,height,height_feet,height_inches,recorded_at")
        .eq("tenant_id", tenant_id)
        .eq("user_id", user_id)
        .order("recorded_at", desc=True)
        .limit(1)
    )
    rows = _result_data(result)
    if not rows:
        return None
    return _normalize_metric_row(rows[0])


def _resolve_height_inches(metric: dict[str, Any]) -> float | None:
    feet = _to_int(metric.get("height_feet"))
    inches = _to_int(metric.get("height_inches"))
    if feet is not None or inches is not None:
        return float((feet or 0) * 12 + (inches or 0))
    return _to_float(metric.get("height"))


def calculate_targets(
    profile: dict[str, Any] | None,
    metric: dict[str, Any] | None,
) -> dict[str, Any]:
    normalized_profile = _normalize_profile_row(profile)
    normalized_metric = _normalize_metric_row(metric)

    if not normalized_profile or not normalized_metric:
        return {
            "recommended_calories": None,
            "recommended_protein_g": None,
            "is_estimate": True,
            "missing_fields": ["questionnaire", "body_metrics"],
            "inputs_used": {
                "sex": normalized_profile.get("sex") if normalized_profile else None,
                "age_years": normalized_profile.get("age_years") if normalized_profile else None,
                "activity_level": normalized_profile.get("activity_level") if normalized_profile else None,
                "goal": normalized_profile.get("goal") if normalized_profile else None,
                "weight_lbs": normalized_metric.get("weight") if normalized_metric else None,
                "height_inches": _resolve_height_inches(normalized_metric) if normalized_metric else None,
            },
        }

    sex = normalized_profile.get("sex")
    age_years = _to_int(normalized_profile.get("age_years"))
    activity_level = normalized_profile.get("activity_level")
    goal = normalized_profile.get("goal")
    weight_lbs = _to_float(normalized_metric.get("weight"))
    height_inches = _resolve_height_inches(normalized_metric)

    missing_fields: list[str] = []
    if sex not in {"male", "female"}:
        missing_fields.append("sex")
    if age_years is None:
        missing_fields.append("age_years")
    if activity_level not in ACTIVITY_MULTIPLIER:
        missing_fields.append("activity_level")
    if goal not in GOAL_CALORIE_ADJUSTMENT:
        missing_fields.append("goal")
    if weight_lbs is None:
        missing_fields.append("weight")
    if height_inches is None:
        missing_fields.append("height")

    if missing_fields:
        return {
            "recommended_calories": None,
            "recommended_protein_g": None,
            "is_estimate": True,
            "missing_fields": missing_fields,
            "inputs_used": {
                "sex": sex,
                "age_years": age_years,
                "activity_level": activity_level,
                "goal": goal,
                "weight_lbs": weight_lbs,
                "height_inches": height_inches,
            },
        }

    weight_kg = float(weight_lbs) * 0.45359237
    height_cm = float(height_inches) * 2.54
    sex_offset = 5 if sex == "male" else -161
    bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * float(age_years)) + sex_offset
    tdee = bmr * ACTIVITY_MULTIPLIER[activity_level]
    recommended_calories = max(1200, round(tdee + GOAL_CALORIE_ADJUSTMENT[goal]))
    protein_g = max(60, round(float(weight_lbs) * PROTEIN_FACTOR_BY_ACTIVITY[activity_level]))

    return {
        "recommended_calories": int(recommended_calories),
        "recommended_protein_g": int(protein_g),
        "is_estimate": False,
        "missing_fields": [],
        "inputs_used": {
            "sex": sex,
            "age_years": age_years,
            "activity_level": activity_level,
            "goal": goal,
            "weight_lbs": float(weight_lbs),
            "height_inches": float(height_inches),
        },
    }
