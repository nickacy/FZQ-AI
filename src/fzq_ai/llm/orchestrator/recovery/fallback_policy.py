# src/fzq_ai/llm/orchestrator/recovery/fallback_policy.py

FALLBACK_CHAIN = {
    "glm-5.2": "deepseek",
    "deepseek": "qwen",
    "qwen": "kimi",
}

class FallbackPolicy:
    def get_fallback(self, provider_name):
        from fzq_ai.llm.router_v2.router import RouterV2
        router = RouterV2()

        fallback = FALLBACK_CHAIN.get(provider_name)
        if not fallback:
            return None

        return router.get_provider(fallback)
