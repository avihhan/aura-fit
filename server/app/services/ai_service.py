"""
AI Service — uses Google Gemini to generate personalised
meal plans and workout plans based on user context.

Set GEMINI_API_KEY in your .env to enable real generation.
When the key is missing the service returns deterministic demo plans
so the rest of the stack can be developed / tested without a live key.
"""

from __future__ import annotations

import json
import os
from typing import Any


def _gemini_model():
    """Lazy-import so the app boots even without the package installed."""
    try:
        import google.generativeai as genai
    except ImportError:
        return None
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        return None
    genai.configure(api_key=key)
    return genai.GenerativeModel(
        "gemini-2.0-flash",
        generation_config={"response_mime_type": "application/json"},
    )


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_MEAL_PLAN_PROMPT = (
    "You are a certified sports nutritionist. "
    "Generate a detailed daily meal plan in valid JSON with keys: "
    '"plan_name", "meals" (array of objects with "meal", "foods" list, '
    '"calories", "protein_g", "carbs_g", "fats_g"), and "daily_totals" '
    "(object with total calories, protein, carbs, fats). "
    "Tailor the plan to the user's profile.\n\n"
    "User profile:\n{context}"
)

_WORKOUT_PLAN_PROMPT = (
    "You are a certified personal trainer. "
    "Generate a weekly workout plan in valid JSON with keys: "
    '"plan_name", "goal", "days" (array of objects with "day", '
    '"focus", "exercises" list — each exercise has "name", "sets", '
    '"reps", "rest_seconds", "notes"). '
    "Tailor the plan to the user's goals and fitness level.\n\n"
    "User profile:\n{context}"
)


def _build_user_context(
    *,
    goal: str | None = None,
    weight: float | None = None,
    height: float | None = None,
    body_fat: float | None = None,
    dietary_prefs: str | None = None,
    fitness_level: str | None = None,
    extra: str | None = None,
) -> str:
    parts: list[str] = []
    if goal:
        parts.append(f"Goal: {goal}")
    if weight:
        parts.append(f"Weight: {weight} lbs")
    if height:
        parts.append(f"Height: {height} in")
    if body_fat:
        parts.append(f"Body fat: {body_fat}%")
    if dietary_prefs:
        parts.append(f"Dietary preferences: {dietary_prefs}")
    if fitness_level:
        parts.append(f"Fitness level: {fitness_level}")
    if extra:
        parts.append(extra)
    return "\n".join(parts) if parts else "No specific preferences given."


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_meal_plan(**kwargs: Any) -> dict:
    """Return a meal-plan dict. Uses Gemini when available, else a demo plan."""
    model = _gemini_model()
    context = _build_user_context(**kwargs)

    if model is not None:
        prompt = _MEAL_PLAN_PROMPT.format(context=context)
        try:
            resp = model.generate_content(prompt)
            return json.loads(resp.text or "{}")
        except (json.JSONDecodeError, Exception):
            pass

    return _demo_meal_plan(kwargs.get("goal"))


def generate_workout_plan(**kwargs: Any) -> dict:
    """Return a workout-plan dict. Uses Gemini when available, else a demo plan."""
    model = _gemini_model()
    context = _build_user_context(**kwargs)

    if model is not None:
        prompt = _WORKOUT_PLAN_PROMPT.format(context=context)
        try:
            resp = model.generate_content(prompt)
            return json.loads(resp.text or "{}")
        except (json.JSONDecodeError, Exception):
            pass

    return _demo_workout_plan(kwargs.get("goal"))


# ---------------------------------------------------------------------------
# Demo / fallback plans (used when no Gemini key is configured)
# ---------------------------------------------------------------------------


def _demo_meal_plan(goal: str | None = None) -> dict:
    return {
        "plan_name": f"Sample Meal Plan – {goal or 'General Health'}",
        "meals": [
            {
                "meal": "Breakfast",
                "foods": ["Oatmeal with berries", "Greek yogurt", "Black coffee"],
                "calories": 420,
                "protein_g": 28,
                "carbs_g": 52,
                "fats_g": 12,
            },
            {
                "meal": "Lunch",
                "foods": ["Grilled chicken breast", "Brown rice", "Steamed broccoli"],
                "calories": 560,
                "protein_g": 45,
                "carbs_g": 55,
                "fats_g": 14,
            },
            {
                "meal": "Snack",
                "foods": ["Apple slices", "Almond butter"],
                "calories": 250,
                "protein_g": 6,
                "carbs_g": 30,
                "fats_g": 14,
            },
            {
                "meal": "Dinner",
                "foods": ["Salmon fillet", "Sweet potato", "Mixed greens salad"],
                "calories": 620,
                "protein_g": 42,
                "carbs_g": 48,
                "fats_g": 22,
            },
        ],
        "daily_totals": {
            "calories": 1850,
            "protein_g": 121,
            "carbs_g": 185,
            "fats_g": 62,
        },
        "_demo": True,
    }


def _demo_workout_plan(goal: str | None = None) -> dict:
    return {
        "plan_name": f"Sample Workout Plan – {goal or 'General Fitness'}",
        "goal": goal or "General Fitness",
        "days": [
            {
                "day": "Monday",
                "focus": "Upper Body Push",
                "exercises": [
                    {"name": "Bench Press", "sets": 4, "reps": "8-10", "rest_seconds": 90, "notes": ""},
                    {"name": "Overhead Press", "sets": 3, "reps": "8-10", "rest_seconds": 90, "notes": ""},
                    {"name": "Incline Dumbbell Press", "sets": 3, "reps": "10-12", "rest_seconds": 60, "notes": ""},
                    {"name": "Tricep Pushdowns", "sets": 3, "reps": "12-15", "rest_seconds": 60, "notes": ""},
                ],
            },
            {
                "day": "Tuesday",
                "focus": "Lower Body",
                "exercises": [
                    {"name": "Barbell Squat", "sets": 4, "reps": "6-8", "rest_seconds": 120, "notes": ""},
                    {"name": "Romanian Deadlift", "sets": 3, "reps": "8-10", "rest_seconds": 90, "notes": ""},
                    {"name": "Leg Press", "sets": 3, "reps": "10-12", "rest_seconds": 90, "notes": ""},
                    {"name": "Calf Raises", "sets": 4, "reps": "15-20", "rest_seconds": 45, "notes": ""},
                ],
            },
            {
                "day": "Wednesday",
                "focus": "Rest / Active Recovery",
                "exercises": [
                    {"name": "Light walking or yoga", "sets": 1, "reps": "20-30 min", "rest_seconds": 0, "notes": ""},
                ],
            },
            {
                "day": "Thursday",
                "focus": "Upper Body Pull",
                "exercises": [
                    {"name": "Barbell Row", "sets": 4, "reps": "8-10", "rest_seconds": 90, "notes": ""},
                    {"name": "Pull-ups", "sets": 3, "reps": "AMRAP", "rest_seconds": 90, "notes": ""},
                    {"name": "Face Pulls", "sets": 3, "reps": "15-20", "rest_seconds": 60, "notes": ""},
                    {"name": "Barbell Curl", "sets": 3, "reps": "10-12", "rest_seconds": 60, "notes": ""},
                ],
            },
            {
                "day": "Friday",
                "focus": "Full Body / Conditioning",
                "exercises": [
                    {"name": "Deadlift", "sets": 3, "reps": "5", "rest_seconds": 180, "notes": ""},
                    {"name": "Dumbbell Lunges", "sets": 3, "reps": "10 each", "rest_seconds": 60, "notes": ""},
                    {"name": "Push-ups", "sets": 3, "reps": "15-20", "rest_seconds": 45, "notes": ""},
                    {"name": "Plank", "sets": 3, "reps": "45 sec", "rest_seconds": 30, "notes": ""},
                ],
            },
        ],
        "_demo": True,
    }
