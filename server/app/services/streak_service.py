"""
Streak & Motivation Service — calculates workout streaks,
assigns badges, and produces motivational content.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any


# ---------------------------------------------------------------------------
# Badge definitions
# ---------------------------------------------------------------------------

BADGES: list[dict[str, Any]] = [
    {"key": "first_workout", "label": "First Workout", "icon": "fire", "threshold": 1},
    {"key": "streak_3", "label": "3-Day Streak", "icon": "zap", "threshold": 3},
    {"key": "streak_7", "label": "Week Warrior", "icon": "award", "threshold": 7},
    {"key": "streak_14", "label": "Two-Week Titan", "icon": "star", "threshold": 14},
    {"key": "streak_30", "label": "Monthly Machine", "icon": "trophy", "threshold": 30},
    {"key": "workouts_10", "label": "10 Workouts", "icon": "target", "threshold": 10},
    {"key": "workouts_50", "label": "50 Workouts", "icon": "shield", "threshold": 50},
    {"key": "workouts_100", "label": "Century Club", "icon": "crown", "threshold": 100},
]

MOTIVATIONAL_QUOTES = [
    "The only bad workout is the one that didn't happen.",
    "Push yourself, because no one else is going to do it for you.",
    "Success isn't always about greatness. It's about consistency.",
    "Your body can stand almost anything. It's your mind you have to convince.",
    "The pain you feel today will be the strength you feel tomorrow.",
    "Don't count the days, make the days count.",
    "Fitness is not about being better than someone else. It's about being better than you used to be.",
    "A one-hour workout is only 4% of your day. No excuses.",
]


# ---------------------------------------------------------------------------
# Streak calculation
# ---------------------------------------------------------------------------


def calculate_streak(workout_dates: list[str]) -> dict:
    """
    Given a list of ISO date strings (e.g. ["2026-04-01", "2026-04-02"]),
    returns { current_streak, longest_streak, total_workouts }.
    """
    if not workout_dates:
        return {"current_streak": 0, "longest_streak": 0, "total_workouts": 0}

    unique_dates = sorted({date.fromisoformat(d) for d in workout_dates}, reverse=True)
    total = len(unique_dates)

    current = 1
    today = date.today()
    if unique_dates[0] < today - timedelta(days=1):
        current = 0
    else:
        for i in range(1, len(unique_dates)):
            if unique_dates[i - 1] - unique_dates[i] == timedelta(days=1):
                current += 1
            else:
                break

    sorted_asc = list(reversed(unique_dates))
    longest = 1
    run = 1
    for i in range(1, len(sorted_asc)):
        if sorted_asc[i] - sorted_asc[i - 1] == timedelta(days=1):
            run += 1
            longest = max(longest, run)
        else:
            run = 1

    return {
        "current_streak": current,
        "longest_streak": longest,
        "total_workouts": total,
    }


# ---------------------------------------------------------------------------
# Badges
# ---------------------------------------------------------------------------


def earned_badges(current_streak: int, total_workouts: int) -> list[dict]:
    """Return the list of badges the user has unlocked."""
    result: list[dict] = []
    for b in BADGES:
        if b["key"].startswith("streak_") or b["key"] == "first_workout":
            if current_streak >= b["threshold"] or total_workouts >= b["threshold"]:
                result.append(b)
        elif b["key"].startswith("workouts_"):
            if total_workouts >= b["threshold"]:
                result.append(b)
    return result


# ---------------------------------------------------------------------------
# Motivational message
# ---------------------------------------------------------------------------


def get_motivation(current_streak: int) -> str:
    """Pick a motivational message, rotating by streak count."""
    idx = current_streak % len(MOTIVATIONAL_QUOTES)
    return MOTIVATIONAL_QUOTES[idx]
