# -*- coding: utf-8 -*-
"""
FZQ-AI Unified Entry (V15-Final)
统一入口：启动 FastAPI（web_app.py）
"""

from __future__ import annotations
import uvicorn


def main():
    """
    启动 V15 新入口端：
    - app/web_app.py 中的 FastAPI 应用
    - Bloomberg Terminal 主题
    - IntentEngine + TaskRouter + Pipelines
    """
    uvicorn.run(
        "app.web_app:app",   # ← 关键：指向新的入口端
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()
