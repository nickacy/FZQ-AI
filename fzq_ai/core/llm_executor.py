from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fzq_ai.config.settings import settings
from fzq_ai.llm.llm_router import LLMRouter

logger = logging.getLogger(__name__)


class LLMExecutor:
    """
    统一的 LLM 执行器：
    - 自动选择 provider
    - 自动读取 settings.llm_models
    - 自动 retry / fallback
    - 自动 Fake 输出（当所有 provider 失败时）
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
        provider: str,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        执行一次 LLM 调用（带 retry + fallback）
        """

        model_cfg = settings.llm_models.get(provider)
        if not model_cfg:
            raise ValueError(f"No config for provider={provider}")

        model_name = model or model_cfg.get("model")
        api_key = model_cfg.get("api_key")
        base_url = model_cfg.get("base_url")

        if not api_key:
            raise ValueError(f"No API key for provider={provider}")

        # 默认参数
        temperature = temperature or settings.default_temperature
        max_tokens = max_tokens or settings.default_max_tokens

        # Retry 机制
        last_error = None
        for attempt in range(1, self.retries + 2):
            try:
                logger.info(f"LLM call: provider={provider}, attempt={attempt}")

                response = await self.router.call(
                    provider=provider,
                    model=model_name,
                    api_key=api_key,
                    base_url=base_url,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self.timeout,
                )

                return response

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Attempt {attempt}/{self.retries + 1} for provider={provider} failed: {e}"
                )

        # ---------------------------------------------------------
        # 所有 provider 都失败 → fallback 到 Fake 输出
        # ---------------------------------------------------------
        logger.error(f"Real LLM call failed → fallback to Fake: {last_error}")

        return self.fake_llm_output(prompt, provider, model_name)

    # ---------------------------------------------------------
    # Fake LLM 输出（用于无 API key 或调用失败）
    # ---------------------------------------------------------
    def fake_llm_output(self, prompt: str, provider: str, model: str) -> str:
        return (
            f"[Fake LLM output using provider={provider}, model={model}]\n"
            f"Prompt was:\n{prompt[:500]}"
        )


# 单例
_executor = LLMExecutor()


async def run_llm(
    provider: str,
    prompt: str,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """
    对外暴露的统一调用接口
    """
    return await _executor.call(
        provider=provider,
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
