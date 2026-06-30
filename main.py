# -*- coding: utf-8 -*-
"""
FZQ-AI Unified Entry (V19.0.0)
统一入口：启动 FastAPI（src.fzq_ai.api.app）
"""

from __future__ import annotations
import uvicorn


def main():
    """
    启动 FZQ-AI API 服务：
    - src/fzq_ai/api/app.py 中的 FastAPI 应用
    - 包含中文情报端点 /api/zh/*
    - 健康检查 /health
    """
    uvicorn.run(
        "src.fzq_ai.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
