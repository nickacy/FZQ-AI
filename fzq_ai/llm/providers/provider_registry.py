from fzq_ai.llm.providers.openai_provider import OpenAIProvider
from fzq_ai.llm.providers.deepseek_provider import DeepSeekProvider
from fzq_ai.llm.providers.gemini_provider import GeminiProvider

class ProviderRegistry:
    def __init__(self):
        self.providers = {
            "openai": OpenAIProvider(),
            "deepseek": DeepSeekProvider(),
            "gemini": GeminiProvider(),
        }

    def get_provider(self, name: str):
        if name not in self.providers:
            raise ValueError(f"Unknown provider: {name}")
        return self.providers[name]
