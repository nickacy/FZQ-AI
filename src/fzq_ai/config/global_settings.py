# -*- coding: utf-8 -*-
"""
FZQ-AI Global Settings (V19-Final)
全局配置（V19 最终版）

本文件提供：
- PROVIDER_MAP（模型 Provider → Client 类）
- PROVIDER_CAPABILITIES（能力矩阵）
- MODEL_PRIORITY（模型优先级链）
- DEFAULT_MODEL（默认模型）
- COST_MATRIX（推理成本）
- CONTEXT_LENGTH（上下文长度）
- PROVIDER_HEALTH（健康检查）
- get_client() / get_model()（供 ModelRouter 使用）
"""

from __future__ import annotations
from pathlib import Path
import yaml


class Settings:
    """V19 全局配置"""

    # ============================================================
    # 1. Provider → Client 映射
    # ============================================================

    PROVIDER_MAP = {
        "deepseek": "DeepSeekClient",
        "qwen": "QwenClient",
        "glm": "GLMClient",
        "kimi": "KimiClient",
        "openai": "OpenAIClient",
        "gemini": "GeminiClient",
    }

    # ============================================================
    # 2. 能力矩阵（模型能力）
    # ============================================================

    PROVIDER_CAPABILITIES = {
        "deepseek": {
            "chat": True,
            "embedding": True,
            "long_context": True,
            "cost": "low",
        },
        "qwen": {
            "chat": True,
            "embedding": True,
            "long_context": True,
            "cost": "low",
        },
        "glm": {
            "chat": True,
            "embedding": True,
            "long_context": False,
            "cost": "medium",
        },
        "kimi": {
            "chat": True,
            "embedding": False,
            "long_context": True,
            "cost": "medium",
        },
        "openai": {
            "chat": True,
            "embedding": True,
            "long_context": True,
            "cost": "high",
        },
        "gemini": {
            "chat": True,
            "embedding": True,
            "long_context": True,
            "cost": "high",
        },
    }

    # ============================================================
    # 3. 模型优先级链（fallback）
    # ============================================================

    MODEL_PRIORITY = [
        "deepseek",
        "qwen",
        "glm",
        "openai",
        "gemini",
    ]

    # ============================================================
    # 4. 默认模型
    # ============================================================

    DEFAULT_MODEL = "deepseek"

    # ============================================================
    # 5. 成本矩阵（可用于预算控制）
    # ============================================================

    COST_MATRIX = {
        "deepseek": 1,
        "qwen": 1,
        "glm": 2,
        "kimi": 2,
        "openai": 3,
        "gemini": 3,
    }

    # ============================================================
    # 6. 上下文长度
    # ============================================================

    CONTEXT_LENGTH = {
        "deepseek": 128000,
        "qwen": 128000,
        "glm": 32000,
        "kimi": 200000,
        "openai": 128000,
        "gemini": 100000,
    }

    # ============================================================
    # 7. Provider 健康检查（可扩展）
    # ============================================================

    PROVIDER_HEALTH = {
        "deepseek": True,
        "qwen": True,
        "glm": True,
        "kimi": True,
        "openai": True,
        "gemini": True,
    }

    # ============================================================
    # 8. YAML 加载（可选）
    # ============================================================

    def __init__(self):
        yaml_path = Path(__file__).parent / "global_settings.yaml"
        if yaml_path.exists():
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            for k, v in data.items():
                setattr(self, k, v)

    # ============================================================
    # 9. ModelRouter 接口
    # ============================================================

    def get_client(self, provider: str):
        """Return a ModelClient instance for the provider."""
        from fzq_ai.clients.model_client import ModelClient
        return ModelClient(provider)

    def get_model(self, provider: str) -> str:
        """Return model name for provider."""
        from fzq_ai.clients.model_client import ModelClient
        return ModelClient._DEFAULT_MODELS.get(provider, provider)


# Singleton
settings = Settings()
