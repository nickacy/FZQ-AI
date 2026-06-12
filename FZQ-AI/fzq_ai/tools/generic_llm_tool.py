# fzq_ai/tools/generic_llm_tool.py

from __future__ import annotations
from typing import Optional
from fzq_ai.core.llm_executor import LLMExecutor

_executor = LLMExecutor()


async def run_llm(
    provider: str,
    prompt: str,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """
    统一 LLM 调用接口（只支持 prompt，不支持 messages）
    """
    return await _executor.call(
        provider=provider,
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
