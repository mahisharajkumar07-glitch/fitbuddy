"""SQLAlchemy models for users, plans, and feedback."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(40), nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    goal: Mapped[str] = mapped_column(String(300), nullable=False)
    experience: Mapped[str] = mapped_column(String(40), nullable=False)
    workout_days: Mapped[int] = mapped_column(Integer, nullable=False)
    equipment: Mapped[str] = mapped_column(Text, nullable=False)
    dietary_preference: Mapped[str | None] = mapped_column(Text)
    limitations: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    plans: Mapped[list["FitnessPlan"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    feedback_entries: Mapped[list["Feedback"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class FitnessPlan(Base):
    __tablename__ = "fitness_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    workout_plan: Mapped[str] = mapped_column(Text, nullable=False)
    nutrition_plan: Mapped[str] = mapped_column(Text, nullable=False)
    fitness_tips: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[User] = relationship(back_populates="plans")
    feedback_entries: Mapped[list["Feedback"]] = relationship(back_populates="plan", cascade="all, delete-orphan")


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_id: Mapped[int] = mapped_column(ForeignKey("fitness_plans.id", ondelete="CASCADE"), nullable=False)
    feedback_text: Mapped[str] = mapped_column(Text, nullable=False)
    updated_plan: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[User] = relationship(back_populates="feedback_entries")
    plan: Mapped[FitnessPlan] = relationship(back_populates="feedback_entries")
