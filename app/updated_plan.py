"""Feedback-based workout-plan revisions."""

from .gemini_generator import generate_workout_text


def update_workout_plan(user, original_plan: str, user_feedback: str) -> str:
    prompt = f"""Revise this person's workout plan using their feedback. Preserve safety and suitability.
Person: age {user.age}; goal: {user.goal}; experience: {user.experience}; equipment: {user.equipment};
limitations: {user.limitations or 'none provided'}.
Current workout plan:\n{original_plan}
User feedback:\n{user_feedback}
Return the complete updated workout plan with a weekly schedule, exercises, sets, reps, rest,
progression, warm-up, cool-down, and safety notes. Do not diagnose injuries."""
    return generate_workout_text(prompt)
