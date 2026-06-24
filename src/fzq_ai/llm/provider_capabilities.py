# v13 Provider Capability Table

PROVIDER_CAPABILITIES = {
    "deepseek": {
        "supports": ["chat", "reasoning", "coding", "analysis"],
        "max_tokens": 32000,
    },
    "qwen": {
        "supports": ["chat", "coding", "analysis"],
        "max_tokens": 32000,
    },
    "kimi": {
        "supports": ["chat", "analysis"],
        "max_tokens": 16000,
    },
    "openai": {
        "supports": ["chat", "coding", "analysis"],
        "max_tokens": 16000,
    },
    "glm": {
        "supports": ["chat", "analysis", "coding"],
        "max_tokens": 32000,
    },
    "gemini": {
        "supports": ["chat", "analysis"],
        "max_tokens": 16000,
    },
}
