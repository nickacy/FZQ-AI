# fzq_ai/config/global_settings.py
# v13 Global Settings Loader (supports nested attribute access)

from __future__ import annotations

import yaml
from pathlib import Path
from fzq_ai.llm.model_client import ModelClient


class AttrDict(dict):
    """Allow dict.key access as attribute."""
    def __getattr__(self, item):
        value = self.get(item)
        if isinstance(value, dict):
            return AttrDict(value)
        return value

    def __setattr__(self, key, value):
        self[key] = value


class Settings:
    """
    v13 Global Settings Loader (supports nested attribute access).

    - Loads global_settings.yaml if present
    - Falls back to defaults
    - Normalizes model_priority (dict → flat list)
    - Provides get_client() / get_model() for Router
    """

    _DEFAULTS = {
        "model_priority": ["deepseek", "openai", "gemini"],
        "llm_models": {},
        "llm_executor_retries": 2,
        "llm_request_timeout": 60,
        "default_temperature": 0.7,
        "default_max_tokens": 2048,
        "log_level": "INFO",
    }

    def __init__(self):
        config_path = Path(__file__).parent / "global_settings.yaml"

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        else:
            import logging
            logging.getLogger(__name__).warning(
                f"global_settings.yaml not found at {config_path}, using defaults"
            )
            data = dict(self._DEFAULTS)

        # Normalize model_priority (dict → flat list)
        mp = data.get("model_priority", [])
        data["model_priority"] = self._normalize_model_priority(mp)

        # Convert nested dicts to AttrDict
        for k, v in data.items():
            if isinstance(v, dict):
                setattr(self, k, AttrDict(v))
            else:
                setattr(self, k, v)

    # ------------------------------------------------------------
    # Priority normalization
    # ------------------------------------------------------------
    def _normalize_model_priority(self, mp):
        """Normalize model_priority from dict to flat list."""
        if isinstance(mp, dict):
            result = []
            primary = mp.get("default_primary")
            if primary:
                result.append(primary)
            fallback = mp.get("fallback", [])
            if isinstance(fallback, list):
                result.extend(fallback)
            return result or ["deepseek", "openai", "gemini"]

        if isinstance(mp, list):
            return mp

        return ["deepseek", "openai", "gemini"]

    # ------------------------------------------------------------
    # Router integration
    # ------------------------------------------------------------
    def get_client(self, provider: str) -> ModelClient:
        """
        Return a ModelClient instance for the provider.
        Router depends on this.
        """
        return ModelClient(provider)

    def get_model(self, provider: str) -> str:
        """
        Return model name for provider.
        Priority:
        1. llm_models in YAML
        2. ModelClient default model
        """
        # User-defined model override
        if hasattr(self, "llm_models") and provider in self.llm_models:
            return self.llm_models[provider]

        # Fallback to ModelClient defaults
        return ModelClient._DEFAULT_MODELS.get(provider, provider)


# Singleton
settings = Settings()
