"""Fast, lower-cost Gemini nutrition guidance generation."""

from .gemini_client import NUTRITION_MODEL, generate_text
from .nutrition import build_nutrition_prompt


def generate_nutrition_tip_with_flash(user) -> str:
    return generate_text(NUTRITION_MODEL, build_nutrition_prompt(user))


def generate_fitness_tips(user) -> str:
    prompt = f"""Give five concise, safe general fitness tips tailored to this person.
Goal: {user.goal}. Experience: {user.experience}. Workout days: {user.workout_days}.
Equipment: {user.equipment}. Limitations: {user.limitations or 'none provided'}.
Focus on sustainable habits, recovery, technique, and consistency. Do not diagnose, promise results,
or replace professional medical advice. Format as a short numbered list."""
    return generate_text(NUTRITION_MODEL, prompt)
