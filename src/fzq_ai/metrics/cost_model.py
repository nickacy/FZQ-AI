# src/fzq_ai/metrics/cost_model.py

COST_TABLE = {
    "glm-5.2": 0.0005,
    "deepseek": 0.0003,
    "qwen": 0.0002,
    "kimi": 0.0004,
}

class CostModel:
    def cost(self, provider: str, tokens: int) -> float:
        price = COST_TABLE.get(provider, 0.0005)
        return tokens * price
