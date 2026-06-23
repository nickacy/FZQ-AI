"""
Legacy config module — 统一入口已迁移至 fzq_ai.config (config/__init__.py)

本文件保留向后兼容，避免旧代码 `from fzq_ai.config import ...` 失败。
.env 加载已统一移至应用入口（main.py / app.py），避免重复加载。
"""

from fzq_ai.config import (  # noqa: F401
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    get_config,
)
