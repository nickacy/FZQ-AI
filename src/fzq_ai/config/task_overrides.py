# fzq_ai/config/task_overrides.py

import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.yaml"

class TaskOverrides:
    """任务级模型覆盖（从 YAML 加载）"""

    def __init__(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        self.overrides = cfg.get("task_overrides", {})

    def get_override(self, task_name: str):
        return self.overrides.get(task_name)
