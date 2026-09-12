"""Pydantic read schema for AI-generated recommendation explanations."""

from typing import Literal

from pydantic import BaseModel


class ExplanationRead(BaseModel):
    recommendation_id: int
    why: str
    what_to_do: str
    expected_benefit: str
    assumptions: str
    source: Literal["gemini", "fallback"]
