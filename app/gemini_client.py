"""Shared Google GenAI client helper and configuration errors."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors
import httpx

load_dotenv()

WORKOUT_MODEL = os.getenv("GEMINI_WORKOUT_MODEL", "gemini-3.7-flash")
NUTRITION_MODEL = os.getenv("GEMINI_NUTRITION_MODEL", "gemini-3.5-flash-lite")
WORKOUT_FALLBACK_MODEL = os.getenv("GEMINI_WORKOUT_FALLBACK_MODEL", NUTRITION_MODEL)


class GeminiConfigurationError(RuntimeError):
    """Raised when Gemini cannot be called with the current configuration."""


class GeminiServiceError(RuntimeError):
    """Raised when Gemini rejects a request or cannot serve it."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def generate_text(model: str, prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        raise GeminiConfigurationError("Add a valid GEMINI_API_KEY to your .env file.")
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(model=model, contents=prompt)
    except errors.APIError as exc:
        status_code = getattr(exc, "code", None)
        if status_code == 429:
            message = (
                "Gemini's free-tier request limit was reached. Wait for the quota to reset, "
                "then try again. Check Google AI Studio's Usage page for your limits."
            )
        elif status_code in {400, 401, 403, 404}:
            message = (
                "Gemini rejected the API key or model. Check that .env contains a current key "
                "from Google AI Studio and that the configured model is available to its project."
            )
        else:
            message = "Gemini is temporarily unavailable. Check your internet connection and try again."
        raise GeminiServiceError(message, status_code=status_code) from exc
    except (httpx.HTTPError, RuntimeError) as exc:
        raise GeminiServiceError(
            "Gemini could not complete the request. Check your internet connection, API key, "
            "and model access, then try again."
        ) from exc
    finally:
        client.close()
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty response. Please try again.")
    return text
