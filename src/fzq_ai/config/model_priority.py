# fzq_ai/config/model_priority.py

import yaml
from pathlib import Path
from fzq_ai.config.env import get_env

CONFIG_PATH = Path(__file__).parent / "config.yaml"

class ModelPriority:
    """全局模型优先级（支持 YAML + 环境变量覆盖）"""

    def __init__(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        # YAML 中的优先级
        self.order = cfg["model_priority"]["order"]

        # 环境变量覆盖（可选）
        env_override = get_env("FZQAI_MODEL_PRIORITY")
        if env_override:
            self.order = [x.strip() for x in env_override.split(",")]

    def get_order(self):
        return self.order
