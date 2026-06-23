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

    def __init__(self):
        config_path = Path(__file__).parent / "global_settings.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Missing global_settings.yaml at {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Convert nested dicts to AttrDict
        for k, v in data.items():
            if isinstance(v, dict):
                setattr(self, k, AttrDict(v))
            else:
                setattr(self, k, v)


# 单例
settings = Settings()
