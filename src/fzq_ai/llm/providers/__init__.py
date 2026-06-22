# fzq_ai/llm/providers/__init__.py
"""
Unified provider exports for FZQ‑AI v9.4
This file exposes:
- All LLM provider classes
- ProviderRegistry (central provider manager)
"""

from fzq_ai.llm.providers.provider_registry import ProviderRegistry

# --- Core Providers ---
from fzq_ai.llm.providers.openai_provider import OpenAIProvider
from fzq_ai.llm.providers.deepseek_provider import DeepSeekProvider
from fzq_ai.llm.providers.gemini_provider import GeminiProvider

# --- China Model Providers ---
from fzq_ai.llm.providers.glm_provider import GLMProvider
from fzq_ai.llm.providers.kimi_provider import KimiProvider
from fzq_ai.llm.providers.doubao_provider import DoubaoProvider
from fzq_ai.llm.providers.qwen_provider import QwenProvider

# --- MiniMax Provider ---
from fzq_ai.llm.providers.minimax_client import MiniMaxClient


__all__ = [
    # Registry
    "ProviderRegistry",

    # Core Providers
    "OpenAIProvider",
    "DeepSeekProvider",
    "GeminiProvider",

    # China Providers
    "GLMProvider",
    "KimiProvider",
    "DoubaoProvider",
    "QwenProvider",

    # MiniMax
    "MiniMaxClient",
]
