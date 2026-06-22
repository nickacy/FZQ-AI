# fzq_ai/llm/model_selector.py
# FZQ‑AI v10 智能模型调度器（Phase 7 核心）

import re
from fzq_ai.config import settings


class ModelSelector:
    """智能模型选择器：根据任务类型、prompt、语言、长度自动选择最优模型"""

    def __init__(self):
        self.priority = settings.priority.get_order()

    # ------------------------------------------------------------
    # 语言检测
    # ------------------------------------------------------------
    def detect_language(self, text: str) -> str:
        if re.search(r"[\u4e00-\u9fff]", text):
            return "zh"
        if re.search(r"[a-zA-Z]", text):
            return "en"
        return "unknown"

    # ------------------------------------------------------------
    # 长度检测
    # ------------------------------------------------------------
    def detect_length(self, text: str) -> int:
        return len(text)

    # ------------------------------------------------------------
    # 主调度逻辑
    # ------------------------------------------------------------
    def select(self, task_type: str, prompt: str):
        lang = self.detect_language(prompt)
        length = self.detect_length(prompt)

        # 任务级覆盖（最高优先级）
        override = settings.overrides.get_override(task_type)
        if override and "primary" in override:
            primary = override["primary"]
            fallback = [m for m in self.priority if m != primary]
            return primary, fallback

        # 任务类型策略
        if task_type.startswith("risk_"):
            primary = "deepseek"
        elif task_type.startswith("narrative_"):
            primary = "qwen"
        elif task_type.startswith("news_"):
            primary = "glm"
        elif task_type.startswith("sentiment_"):
            primary = "openai"
        elif task_type.startswith("scenario_"):
            primary = "deepseek"
        elif task_type.startswith("daily_"):
            primary = "kimi"
        else:
            primary = self.priority[0]

        # 语言策略
        if lang == "zh":
            primary = "qwen"
        elif lang == "en":
            primary = "openai"

        # 长度策略
        if length > 3000:
            primary = "kimi"
        elif length > 800:
            primary = "deepseek"

        # fallback = 除 primary 之外的所有模型
        fallback = [m for m in self.priority if m != primary]

        return primary, fallback


model_selector = ModelSelector()
