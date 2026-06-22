# src/fzq_ai/config/settings.py

import yaml
from pathlib import Path


class SettingsManager:
    """
    A simple YAML-based settings loader.
    Supports nested key access via settings.get("section", "key").
    """

    def __init__(self, path=None):
        # 默认路径：src/fzq_ai/config/global_settings.yaml
        if path is None:
            base = Path(__file__).resolve().parent
            path = base / "global_settings.yaml"

        self.path = Path(path)
        self.settings = self._load()

    def _load(self):
        if not self.path.exists():
            print(f"[Settings] Warning: {self.path} not found.")
            return {}

        with open(self.path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def get(self, *keys, default=None):
        """
        Example:
            settings.get("budget", "daily_cap_usd")
        """
        cfg = self.settings
        for k in keys:
            if cfg is None or k not in cfg:
                return default
            cfg = cfg[k]
        return cfg


# 全局实例
settings = SettingsManager()
