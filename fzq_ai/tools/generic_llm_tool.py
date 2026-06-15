# fzq_ai/tools/generic_llm_tool.py

from __future__ import annotations
from typing import Optional
from fzq_ai.core.llm_executor import LLMExecutor

_executor = LLMExecutor()

async def run_llm(
    provider: str,
) -> str:
    """
    """
    return await _executor.call(
        provider=provider,
