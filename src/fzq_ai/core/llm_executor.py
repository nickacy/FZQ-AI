from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fzq_ai.config.global_settings import settings
from fzq_ai.llm.llm_router import LLMRouter

logger = logging.getLogger(__name__)


class LLMExecutor:
    """
    Unified LLM executor:
    - Auto-select provider
    - Auto-read settings.llm_models
    - Auto retry / fallback
    - Auto Fake output (when all providers fail)
    """

    def __init__(self):
        self.router = LLMRouter()
        self.retries = settings.llm_executor_retries
        self.timeout = settings.llm_request_timeout

    async def call(
        self,
        provider: str,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        model_cfg = settings.llm_models.get(provider)
        if not model_cfg:
            raise ValueError(f"No config for provider={provider}")

        model_name = model or model_cfg.get("model")
        api_key = model_cfg.get("api_key")
        base_url = model_cfg.get("base_url")

        if not api_key:
            raise ValueError(f"No API key for provider={provider}")

        temperature = temperature or settings.default_temperature
        max_tokens = max_tokens or settings.default_max_tokens

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

        logger.error(f"Real LLM call failed, fallback to Fake: {last_error}")
        return self.fake_llm_output(prompt, provider, model_name)

    def fake_llm_output(self, prompt: str, provider: str, model: str) -> str:
        return (
            f"[Fake LLM output using provider={provider}, model={model}]\n"
            f"Prompt was:\n{prompt[:500]}"
        )


_executor = LLMExecutor()


async def run_llm(
    provider: str,
    prompt: str,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> str:
    return await _executor.call(
        provider=provider,
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
