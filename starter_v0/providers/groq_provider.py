from __future__ import annotations

import os

from providers.openai_provider import OpenAIProvider


class GroqProvider(OpenAIProvider):
    """Groq exposes an OpenAI-compatible Chat Completions API."""

    def __init__(self) -> None:
        super().__init__(
            api_key_env="GROQ_API_KEY",
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
            # Local function calling is required for this lab; do not use Groq
            # Compound here because it only supports Groq built-in tools.
            default_model=os.getenv("GROQ_MODEL", "qwen/qwen3.6-27b"),
        )
