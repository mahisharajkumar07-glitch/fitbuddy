"""Build the nutrition-only prompt used by the lighter Gemini model."""


def build_nutrition_prompt(user) -> str:
    return f"""Give general, practical nutrition guidance for a fitness plan.
Goal: {user.goal}. Dietary preference: {user.dietary_preference or 'none specified'}.
Consider age {user.age}, weight {user.weight} kg, and workout frequency {user.workout_days} days/week.
Suggest balanced meal ideas, hydration, and simple habits. Avoid exact medical prescriptions,
extreme diets, and unsupported calorie targets. Mention consulting a qualified professional for
medical conditions, allergies, or individualized nutrition needs. Format with clear headings."""
