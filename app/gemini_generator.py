"""Workout-plan generation."""

import logging

from .gemini_client import (
    WORKOUT_FALLBACK_MODEL,
    WORKOUT_MODEL,
    GeminiServiceError,
    generate_text,
)

logger = logging.getLogger("fitbuddy.gemini")


def generate_workout_text(prompt: str) -> str:
    try:
        return generate_text(WORKOUT_MODEL, prompt)
    except GeminiServiceError as exc:
        if exc.status_code != 503 or WORKOUT_FALLBACK_MODEL == WORKOUT_MODEL:
            raise
        logger.warning("Primary workout model returned 503; trying the configured fallback model.")
        return generate_text(WORKOUT_FALLBACK_MODEL, prompt)


def generate_workout_gemini(user) -> str:
    prompt = f"""Create a practical, safe weekly fitness workout plan.
User: age {user.age}, gender {user.gender}, height {user.height} cm, weight {user.weight} kg.
Goal: {user.goal}. Experience: {user.experience}. Workout days: {user.workout_days}.
Equipment: {user.equipment}. Injuries or limitations: {user.limitations or 'none provided'}.
Include a weekly schedule, warm-up, exercises with sets/repetitions/rest, progression guidance,
cool-down, and safety notes. Adapt every exercise to the equipment and limitations. Use clear headings
and plain text; do not diagnose or prescribe treatment. Tell the user to stop if they feel pain."""
    return generate_workout_text(prompt)
