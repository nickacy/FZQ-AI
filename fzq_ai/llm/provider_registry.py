# fzq_ai/llm/provider_registry.py

from dataclasses import dataclass


@dataclass
class ProviderCapabilities:
    name: str
    json_mode: bool
    reasoning: int          # 1–5
    long_context: int       # 1–5
    speed: int              # 1–5
    cost: int               # 1–5 (1=最便宜)
    reliability: int        # 1–5


class ProviderRegistry:
    """
    Provider 能力声明（统一管理所有模型能力）
    """

    def __init__(self):
        self.providers = {
            "openai": ProviderCapabilities(
                name="openai",
                json_mode=True,
                reasoning=4,
                long_context=3,
                speed=3,
                cost=4,
                reliability=5,
            ),
            "deepseek": ProviderCapabilities(
                name="deepseek",
                json_mode=True,
                reasoning=5,
                long_context=4,
                speed=4,
                cost=2,
                reliability=4,
            ),
            "minimax": ProviderCapabilities(
                name="minimax",
                json_mode=True,
                reasoning=2,
                long_context=5,
                speed=5,
                cost=1,
                reliability=3,
            ),
        }

    def get(self, name: str) -> ProviderCapabilities:
        return self.providers[name]
