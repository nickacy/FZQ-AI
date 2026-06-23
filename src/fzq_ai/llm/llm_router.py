# fzq_ai/llm/llm_router.py
# v13 Compatibility Layer for old pipelines

from __future__ import annotations
from typing import Any, Dict

from fzq_ai.llm.router import Router


class LLMRouter:
    """
    v13 兼容层：
    - 保留旧接口：route(task_name, prompt)
    - 底层调用 v13 Router.run(req)
    """

    def __init__(self):
        self.router = Router()

    async def route(self, task_type: str, prompt: str) -> str:
        req = {
            "task_type": task_type,
            "prompt": prompt,
        }

        result = await self.router.run(req)

        # v13 Router 返回结构化 dict
        # 旧 pipeline 只需要 output 字符串
        return result.get("output", "")
