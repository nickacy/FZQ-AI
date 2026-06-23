# fzq_ai/config/global_settings.py
# v13 Global Settings Loader

import yaml
from pathlib import Path


class Settings:

    def __init__(self):
        config_path = Path(__file__).parent / "global_settings.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Missing global_settings.yaml at {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # 直接把 YAML 的 key 映射成属性
        for k, v in data.items():
            setattr(self, k, v)


# 单例
settings = Settings()
