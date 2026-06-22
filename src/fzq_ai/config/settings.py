# fzq_ai/config/settings.py

from fzq_ai.config.model_priority import ModelPriority
from fzq_ai.config.task_overrides import TaskOverrides

class Settings:
    """全局配置入口"""

    def __init__(self):
        self.priority = ModelPriority()
        self.overrides = TaskOverrides()

    def get_model_for_task(self, task_name: str):
        """返回任务的 primary_model + fallback_models"""

        override = self.overrides.get_override(task_name)

        # 如果 YAML 中有任务覆盖
        if override and "primary" in override:
            primary = override["primary"]
        else:
            primary = self.priority.get_order()[0]

        # fallback = 除 primary 之外的所有模型
        fallback = [m for m in self.priority.get_order() if m != primary]

        return primary, fallback


settings = Settings()
