"""ASGI entry point for FitBuddy: uvicorn app.main:app --reload."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routes import router

PROJECT_DIR = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="FitBuddy", description="AI Fitness Plan Generator", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(PROJECT_DIR / "static")), name="static")
app.include_router(router)
