"""FitBuddy web application routes."""

import logging
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .gemini_client import GeminiConfigurationError, GeminiServiceError
from .gemini_flash_generator import generate_fitness_tips, generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini
from .models import Feedback, FitnessPlan, User
from .schemas import UserProfileInput
from .updated_plan import update_workout_plan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fitbuddy")


PROJECT_DIR = Path(__file__).resolve().parent.parent
router = APIRouter()
templates = Jinja2Templates(directory=str(PROJECT_DIR / "templates"))


def page(request: Request, name: str, **context):
    status_code = context.pop("status_code", 200)
    return templates.TemplateResponse(
        request=request,
        name=name,
        context={"request": request, **context},
        status_code=status_code,
    )


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return page(request, "index.html", errors=[], form={})


@router.get("/health")
def health():
    return {"status": "ok", "app": "FitBuddy"}


@router.post("/generate", response_class=HTMLResponse)
def generate(
    request: Request,
    name: str = Form(...), age: int = Form(...), gender: str = Form(...),
    height: float = Form(...), weight: float = Form(...), goal: str = Form(...),
    experience: str = Form(...), workout_days: int = Form(...), equipment: str = Form(...),
    dietary_preference: str = Form(""), limitations: str = Form(""),
    db: Session = Depends(get_db),
):
    form = {"name": name, "age": age, "gender": gender, "height": height, "weight": weight,
            "goal": goal, "experience": experience, "workout_days": workout_days,
            "equipment": equipment, "dietary_preference": dietary_preference, "limitations": limitations}
    try:
        profile = UserProfileInput.model_validate(form)
    except ValidationError as exc:
        errors = [item["msg"].replace("Value error, ", "") for item in exc.errors()]
        return page(request, "index.html", errors=errors, form=form)

    user = User(name=profile.name, age=profile.age, gender=profile.gender, height=profile.height, weight=profile.weight,
                goal=profile.goal, experience=profile.experience, workout_days=profile.workout_days,
                equipment=profile.equipment, dietary_preference=profile.dietary_preference or None,
                limitations=profile.limitations or None)
    try:
        db.add(user)
        db.flush()
        workout = generate_workout_gemini(user)
        nutrition = generate_nutrition_tip_with_flash(user)
        fitness_tips = generate_fitness_tips(user)
        plan = FitnessPlan(user_id=user.id, workout_plan=workout, nutrition_plan=nutrition,
                           fitness_tips=fitness_tips)
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return page(request, "result.html", user=user, plan=plan, error=None)
    except (GeminiConfigurationError, GeminiServiceError) as exc:
        db.rollback()
        logger.warning("Gemini plan generation could not complete: %s", exc)
        return page(request, "error.html", message=str(exc), status_code=503)
    except Exception as exc:
        db.rollback()
        logger.error("Could not generate a fitness plan (%s)", type(exc).__name__)
        return page(request, "error.html", message="We could not generate your plan right now. Check your Gemini configuration and try again.", status_code=502)


@router.get("/plan/{plan_id}", response_class=HTMLResponse)
def show_plan(plan_id: int, request: Request, db: Session = Depends(get_db)):
    plan = db.get(FitnessPlan, plan_id)
    if not plan:
        return page(request, "error.html", message="That fitness plan was not found.", status_code=404)
    return page(request, "result.html", user=plan.user, plan=plan, error=None)


@router.get("/feedback/{plan_id}", response_class=HTMLResponse)
def feedback_form(plan_id: int, request: Request, db: Session = Depends(get_db)):
    plan = db.get(FitnessPlan, plan_id)
    if not plan:
        return page(request, "error.html", message="That fitness plan was not found.", status_code=404)
    return page(request, "feedback.html", plan=plan, error=None)


@router.post("/feedback/{plan_id}", response_class=HTMLResponse)
def submit_feedback(plan_id: int, request: Request, feedback_text: str = Form(...), db: Session = Depends(get_db)):
    plan = db.get(FitnessPlan, plan_id)
    if not plan:
        return page(request, "error.html", message="That fitness plan was not found.", status_code=404)
    if not feedback_text.strip():
        return page(request, "feedback.html", plan=plan, error="Please enter your feedback.")
    try:
        updated = update_workout_plan(plan.user, plan.workout_plan, feedback_text.strip())
        db.add(Feedback(user_id=plan.user_id, plan_id=plan.id, feedback_text=feedback_text.strip(), updated_plan=updated))
        plan.workout_plan = updated
        db.commit()
        return page(request, "result.html", user=plan.user, plan=plan, error=None)
    except (GeminiConfigurationError, GeminiServiceError) as exc:
        db.rollback()
        logger.warning("Gemini plan update could not complete: %s", exc)
        return page(request, "error.html", message=str(exc), status_code=503)
    except Exception as exc:
        db.rollback()
        logger.error("Could not update fitness plan (%s)", type(exc).__name__)
        return page(request, "error.html", message="We could not update your plan right now. Please try again.", status_code=502)


@router.get("/users", response_class=HTMLResponse)
@router.get("/view-all-users", response_class=HTMLResponse)
def users(request: Request, db: Session = Depends(get_db)):
    stored_users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return page(request, "all_users.html", users=stored_users)
