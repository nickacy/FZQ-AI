# fzq_ai/config/global_settings.py
# v13 Global Settings Loader (supports nested attribute access)

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
    
    Falls back to sensible defaults if global_settings.yaml is missing.
    """

    # Default fallback configuration
    _DEFAULTS = {
        "model_priority": ["deepseek", "openai", "gemini"],
        "llm_models": {},
        "llm_executor_retries": 2,
        "llm_request_timeout": 60,
        "default_temperature": 0.7,
        "default_max_tokens": 2048,
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
            data = self._DEFAULTS

        # Convert nested dicts to AttrDict
        for k, v in data.items():
            if isinstance(v, dict):
                setattr(self, k, AttrDict(v))
            else:
                setattr(self, k, v)

    def get_client(self, provider: str) -> object:
        """Return client config for provider (placeholder)."""
        return None

    def get_model(self, provider: str) -> str:
        """Return model name for provider (placeholder)."""
        return "default"


# 单例
settings = Settings()
