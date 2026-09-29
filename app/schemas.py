"""Validated form data schemas for FitBuddy."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserProfileInput(BaseModel):
    """Validation rules for the profile submitted to the plan form."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=120)
    age: int = Field(ge=13, le=100)
    gender: str = Field(min_length=1, max_length=40)
    height: float = Field(gt=0, le=260)
    weight: float = Field(gt=0, le=500)
    goal: str = Field(min_length=1, max_length=300)
    experience: Literal["Beginner", "Intermediate", "Advanced"]
    workout_days: int = Field(ge=1, le=7)
    equipment: str = Field(min_length=1, max_length=500)
    dietary_preference: str = Field(default="", max_length=500)
    limitations: str = Field(default="", max_length=1000)

    @field_validator("name", "gender", "goal", "equipment")
    @classmethod
    def require_non_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field cannot be blank.")
        return value
