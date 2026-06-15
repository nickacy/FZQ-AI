# fzq_ai/config/settings.py

from __future__ import annotations
from pydantic_settings import BaseSettings
from typing import Dict, Any

class Settings(BaseSettings):
    # LLM 模型配置（你会在 .env 中定义）

    # 默认模型

    # 默认参数

    # LLMExecutor 配置

    class Config:
        extra = "allow"  # ⭐⭐ 关键修复：允许 .env 中的额外字段

settings = Settings()
