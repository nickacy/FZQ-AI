from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fzq_ai.config.settings import settings
from fzq_ai.llm.llm_router import LLMRouter

logger = logging.getLogger(__name__)

class LLMExecutor:
    """
    """

    def __init__(self):
        self.router = LLMRouter()
        self.retries = settings.llm_executor_retries
        self.timeout = settings.llm_request_timeout

    # ---------------------------------------------------------
    # 主入口：执行 LLM 调用
    # ---------------------------------------------------------
    async def call(
        self,
        """
        """

        if not model_cfg:
            raise ValueError(f"No config for provider={provider}")

        if not api_key:
            raise ValueError(f"No API key for provider={provider}")

        # 默认参数

        # Retry 机制
        for attempt in range(1, self.retries + 2):
            try:

                response = await self.router.call(
                    provider=provider,
                    timeout=self.timeout,

                return response

            except Exception as e:
                    f"Attempt {attempt}/{self.retries + 1} for provider={provider} failed: {e}"

        # ---------------------------------------------------------
        # 所有 provider 都失败 → fallback 到 Fake 输出
        # ---------------------------------------------------------

        return self.fake_llm_output(prompt, provider, model_name)

    # ---------------------------------------------------------
    # Fake LLM 输出（用于无 API key 或调用失败）
    # ---------------------------------------------------------
    def fake_llm_output(self, prompt: str, provider: str, model: str) -> str:
        return (
            f"[Fake LLM output using provider={provider}, model={model}]\n"

# 单例
_executor = LLMExecutor()

async def run_llm(
    provider: str,
) -> str:
    """
    """
    return await _executor.call(
        provider=provider,
