# fzq_ai/llm/llm_router.py

from typing import Any
from fzq_ai.llm.router import LLMRouter as CoreLLMRouter


class LLMRouter(CoreLLMRouter):
    """
    兼容旧引用的薄封装。
    实际逻辑全部在 fzq_ai.llm.router.LLMRouter 中。
    """
    pass
