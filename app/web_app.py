# -*- coding: utf-8 -*-
"""
FZQ-AI Web App (V17 Entry Layer)
统一入口：/entry → EntryService.handle()
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from entry.entry_service import EntryService
from app.entry_adapter import AdaptedPipelineRegistry
from core.task_router import TaskRouter


# ============================================================
# 1. FastAPI 应用初始化 / App Initialization
# ============================================================

app = FastAPI(title="FZQ-AI Entry Layer V17")

# 静态文件挂载（必须在 app 创建之后）
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# CORS 收紧：仅本地开发域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 2. 请求模型 / Request Model
# ============================================================

class UserQuery(BaseModel):
    text: str = Field(..., max_length=5000)
    language: str = Field("zh", max_length=10)
    session_id: str | None = None


# ============================================================
# 3. 核心组件初始化 / Core Components
# ============================================================

pipeline_registry = AdaptedPipelineRegistry()
task_router = TaskRouter(pipeline_registry=pipeline_registry)
entry_service = EntryService(task_router=task_router, pipeline_registry=pipeline_registry)


# ============================================================
# 4. 全局异常处理 / Global Exception Handler
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": str(exc),
        },
    )


# ============================================================
# 5. 入口端点 / Entry Endpoint
# ============================================================

@app.post("/entry")
async def entry_endpoint(query: UserQuery):
    """
    Unified entry point:
    - Intent recognition: IntentEngine.classify()
    - Task routing: TaskRouter.route()
    - Pipeline execution: pipeline.run()
    - Structured output: EntryService.handle()
    """
    result = await entry_service.handle(
        text=query.text,
        language=query.language,
        session_id=query.session_id,
    )
    return {"result": result}


# ============================================================
# 6. Health Check
# ============================================================

@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
