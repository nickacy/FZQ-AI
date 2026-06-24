"""
Fabricates the missing model_client.py that global_settings.py depends on.
Minimal v13 bridge module.
"""
from __future__ import annotations
from typing import Optional


class ModelClient:
    """Minimal v13 ModelClient — delegates real work to Router."""

    _DEFAULT_MODELS = {
        "deepseek": "deepseek-chat",
        "openai": "gpt-4o",
        "gemini": "gemini-2.0-flash",
        "glm": "glm-4-flash",
        "kimi": "moonshot-v1-32k",
        "qwen": "qwen-max",
    }

    def __init__(self, provider: str):
        self.provider = provider
        self.model = self._DEFAULT_MODELS.get(provider, provider)
