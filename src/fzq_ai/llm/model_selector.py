# fzq_ai/llm/model_selector.py
# FZQ‑AI v12 ModelSelector（带 TokenMonitor 自动降级）

from typing import Tuple, List
from fzq_ai.monitor.token_monitor import token_monitor


class ModelSelector:

    def __init__(self):
        # 你原来的模型优先级（如有）
        self.default_primary = "deepseek"
        self.default_fallback = ["qwen", "glm", "openai"]

    # ------------------------------------------------------------
    # 主入口：选择 primary + fallback
    # ------------------------------------------------------------
    def select(self, task_type: str, prompt: str) -> Tuple[str, List[str]]:

        # --------------------------------------------------------
        # Step 1：自动降级策略（新增）
        # --------------------------------------------------------
        if token_monitor.should_downgrade():
            print("[Routing] Budget high → Auto downgrade to low-cost models")

            # 低成本模型优先级
            primary = "qwen"
            fallback = ["glm", "deepseek"]

            return primary, fallback

        # --------------------------------------------------------
        # Step 2：正常模型选择逻辑（你原来的逻辑）
        # --------------------------------------------------------
        # 你可以在这里加入任务偏好（如 risk、scenario 等）
        # 当前保持最简洁版本，与你原始结构一致

        primary = self.default_primary
        fallback = self.default_fallback

        return primary, fallback


# 全局实例
model_selector = ModelSelector()
