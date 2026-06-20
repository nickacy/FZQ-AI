"""
FastAPI 模块化 API（子模块）
C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI\fzq_ai\api\app.py

fzq_ai.api.app
FastAPI 应用入口：
- 提供 /health 健康检查
- 提供 /run-report 触发 orchestrator
- 返回 ServiceResult 结构
"""

from __future__ import annotations
from fastapi import FastAPI
from fzq_ai.api.zh_endpoints import router as zh_router

app = FastAPI()

# 挂载中文情报 API
app.include_router(zh_router)

import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator
from fzq_ai.domain.models import ServiceResult

logger = logging.getLogger(__name__)

app = FastAPI(
    title="FZQ-AI API",
    description="Unified API for News, Narrative, Risk, and Daily Report generation",
    version="1.0.0",
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/run-report")
async def run_report():
    """
    触发 orchestrator，生成完整日报。
    """
    try:
        orchestrator = TaskOrchestrator()
        result: ServiceResult = await orchestrator.orchestrate()

        return JSONResponse(
            status_code=200 if result.success else 500,
            content=result.to_dict(),
        )

    except Exception as e:
        logger.error("run_report failed: %s", e, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "metadata": {"endpoint": "run-report"},
            },
        )
