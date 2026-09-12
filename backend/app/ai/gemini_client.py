"""Thin wrapper around the `google-genai` SDK.

Backend is the sole source of numerical truth: this client only ever sends a
fully-formed, grounded prompt (built in `app/ai/prompts.py`) to Gemini for
narrative explanation, and never asks it to compute or invent numbers.

Raises `GeminiUnavailableError` whenever the explanation service should fall
back to the deterministic template path: the API key is unset (short-circuit,
no network call attempted), or the API call itself fails or times out.
"""

from google import genai
from google.genai import types

from app.core.config import settings

REQUEST_TIMEOUT_MS = 10_000


class GeminiUnavailableError(Exception):
    """Raised when Gemini cannot be used and the caller should fall back."""


def generate_explanation(prompt: str) -> str:
    if not settings.gemini_api_key:
        raise GeminiUnavailableError("Gemini API key is not configured")

    try:
        client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS),
        )
        response = client.models.generate_content(
            model=settings.gemini_model, contents=prompt
        )
        text = response.text
    except Exception as exc:  # noqa: BLE001 - any SDK/network failure triggers fallback
        raise GeminiUnavailableError(f"Gemini call failed: {exc}") from exc

    if not text or not text.strip():
        raise GeminiUnavailableError("Gemini returned an empty response")

    return text
