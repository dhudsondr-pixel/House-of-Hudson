"""Planner type registry.

Adding a new planner type: define a function `build(canvas, theme)` and
register it in PLANNER_TYPES.
"""

from .daily import build as build_daily
from .goal_setter import build as build_goal
from .habit_tracker import build as build_habit
from .meal_planner import build as build_meal
from .time_blocker import build as build_time
from .weekly import build as build_weekly


PLANNER_TYPES = {
    "daily-planner": {
        "build": build_daily,
        "display_name": "Daily Planner",
        "keywords": ("daily planner", "to do list", "productivity planner",
                     "schedule template", "undated planner"),
        "category": "Productivity",
    },
    "weekly-planner": {
        "build": build_weekly,
        "display_name": "Weekly Planner",
        "keywords": ("weekly planner", "week at a glance", "weekly schedule",
                     "weekly agenda", "undated weekly"),
        "category": "Productivity",
    },
    "habit-tracker": {
        "build": build_habit,
        "display_name": "Habit Tracker",
        "keywords": ("habit tracker", "habit chart", "monthly habit",
                     "goal tracker", "routine tracker"),
        "category": "Self-Care",
    },
    "goal-setter": {
        "build": build_goal,
        "display_name": "Goal Setting Workbook",
        "keywords": ("goal planner", "goal setting", "smart goals",
                     "vision board", "intention setting"),
        "category": "Self-Improvement",
    },
    "time-blocker": {
        "build": build_time,
        "display_name": "Time Blocking Template",
        "keywords": ("time blocking", "time block planner", "hourly planner",
                     "schedule template", "deep work planner"),
        "category": "Productivity",
    },
    "meal-planner": {
        "build": build_meal,
        "display_name": "Weekly Meal Planner",
        "keywords": ("meal planner", "weekly meal plan", "grocery list",
                     "meal prep", "menu planner"),
        "category": "Home",
    },
}
