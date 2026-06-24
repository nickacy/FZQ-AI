# fzq_ai/config/global_settings.py
# v13 Global Settings Loader (supports nested attribute access)

from __future__ import annotations

import yaml
from pathlib import Path


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
    - Merges with _DEFAULTS so all expected keys always exist
    - Normalizes model_priority (dict -> flat list)
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
                yaml_data = yaml.safe_load(f) or {}
        else:
            import logging
            logging.getLogger(__name__).warning(
                f"global_settings.yaml not found at {config_path}, using defaults"
            )
            yaml_data = {}

        # Merge: start with defaults, override with YAML
        data = dict(self._DEFAULTS)
        data.update(yaml_data)

        # Normalize model_priority (dict -> flat list)
        mp = data.get("model_priority", [])
        data["model_priority"] = self._normalize_model_priority(mp)

        # Ensure llm_models is always a dict
        if not isinstance(data.get("llm_models"), dict):
            data["llm_models"] = {}

        # Set all as attributes
        for k, v in data.items():
            if isinstance(v, dict):
                setattr(self, k, AttrDict(v))
            else:
                setattr(self, k, v)

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

    def get_client(self, provider: str):
        """Return a ModelClient instance for the provider."""
        # Lazy import to avoid circular dependency
        from fzq_ai.clients.model_client import ModelClient
        return ModelClient(provider)

    def get_model(self, provider: str) -> str:
        """Return model name for provider."""
        if hasattr(self, "llm_models") and provider in self.llm_models:
            return self.llm_models[provider]
        # Lazy import for defaults
        from fzq_ai.clients.model_client import ModelClient
        return ModelClient._DEFAULT_MODELS.get(provider, provider)


# Singleton
settings = Settings()
