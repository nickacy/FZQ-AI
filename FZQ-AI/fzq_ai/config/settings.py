# fzq_ai/config/settings.py

from __future__ import annotations
from pydantic_settings import BaseSettings
from typing import Dict, Any


class Settings(BaseSettings):
    # LLM 模型配置（你会在 .env 中定义）
    llm_models: Dict[str, Any] = {}

    # 默认模型
    default_model: str = "deepseek"

    # 默认参数
    default_temperature: float = 0.7
    default_max_tokens: int = 2048

    # LLMExecutor 配置
    llm_executor_retries: int = 2
    llm_request_timeout: int = 30

    class Config:
        env_file = ".env"
        extra = "allow"   # ⭐⭐ 关键修复：允许 .env 中的额外字段


settings = Settings()
