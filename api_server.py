"""
api_server.py

FZQ-AI Intelligence API Server (v2.5)
- FastAPI-based REST API
- 统一的请求/响应模型
- 全局异常处理
- 健康检查与版本信息
- 耗时统计

启动: uvicorn api_server:app --reload --port 8000
"""

from __future__ import annotations

import os
import time
import traceback
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv(override=True)

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator
from fzq_ai.llm.llm_router import LLMRouter

# ============================================================
#  应用版本信息
# ============================================================
APP_VERSION: str = "2.5.0"
BUILD_TIME: str = "2026-06-15T00:00:00Z"

# ============================================================
#  FastAPI 初始化
# ============================================================
app = FastAPI(
    title="FZQ-AI Intelligence API",
)

app.add_middleware(
    CORSMiddleware,
)

# ============================================================
#  Pydantic 模型
# ============================================================

class NewsRequest(BaseModel):
    """新闻分析请求"""

class NarrativeRequest(BaseModel):
    """叙事分析请求"""

class RiskRequest(BaseModel):
    """风险扫描请求"""

class TaskRequest(BaseModel):
    """任务编排请求"""

class APIResponse(BaseModel):
    """统一 API 响应结构"""

# ============================================================
#  全局异常处理
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """捕获所有未处理异常，返回结构化 JSON 而非裸露 traceback。"""
    return JSONResponse(
        status_code=500,
                "path": str(request.url.path),
                "method": request.method,

@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """统一 HTTPException 输出格式。"""
    return JSONResponse(
        status_code=exc.status_code,

# ============================================================
#  工具函数
# ============================================================

def _elapsed(start: float) -> float:
    return round((time.time() - start) * 1000, 2)

# ============================================================
#  路由
# ============================================================

@app.get("/")
def root() -> Dict[str, Any]:
    """健康探测根端点。"""
    return {
        "status": "ok",
        "service": "FZQ-AI Intelligence API",
        "version": APP_VERSION,

@app.get("/health", response_model=APIResponse)
async def health() -> APIResponse:
    """

    """

    # DeepSeek
        "available" if deepseek_key else "not_configured"

    # OpenAI
    provider_status["openai"] = "available" if openai_key else "not_configured"

    # Gemini
    provider_status["gemini"] = "available" if gemini_key else "not_configured"

    return APIResponse(
        success=True,
            "service": "healthy",
            "providers": provider_status,

@app.get("/version", response_model=APIResponse)
async def version() -> APIResponse:
    """

    """
    return APIResponse(
        success=True,
            "version": APP_VERSION,
            "build_time": BUILD_TIME,
            "service": "FZQ-AI Intelligence API",

@app.get("/news", response_model=APIResponse)
def news(topic: str) -> APIResponse:
    """

    """

    try:
        result: Dict[str, Any] = orchestrator.run_agent(
            agent_name="news-intel", topic=topic
        return APIResponse(
            success=result.get("success", False),
            data=result.get("data"),
            error=result.get("error"),
            elapsed_ms=_elapsed(start),
        )
    except Exception as e:
        return APIResponse(
            success=False,

@app.post("/news/analyze", response_model=APIResponse)
async def news_analyze(req: NewsRequest) -> APIResponse:
    """新闻分析（POST 版本，使用 Pydantic 模型验证）。"""

    try:
        result: Dict[str, Any] = orchestrator.run_agent(
            agent_name="news-intel", topic=req.topic
        return APIResponse(
            success=result.get("success", False),
            data=result.get("data"),
            error=result.get("error"),
            elapsed_ms=_elapsed(start),
        )
    except Exception as e:
        return APIResponse(
            success=False,

@app.post("/narrative", response_model=APIResponse)
async def narrative(req: NarrativeRequest) -> APIResponse:
    """叙事分析（POST）。"""

    try:
        result: Dict[str, Any] = orchestrator.run_agent(
            agent_name="narrative", text=req.text
        return APIResponse(
            success=result.get("success", False),
            data=result.get("data"),
            error=result.get("error"),
            elapsed_ms=_elapsed(start),
        )
    except Exception as e:
        return APIResponse(
            success=False,

@app.post("/risk", response_model=APIResponse)
async def risk(req: RiskRequest) -> APIResponse:
    """风险扫描（POST）。"""

    try:
        result: Dict[str, Any] = orchestrator.run_agent(
            agent_name="risk", topic=req.topic
        return APIResponse(
            success=result.get("success", False),
            data=result.get("data"),
            error=result.get("error"),
            elapsed_ms=_elapsed(start),
        )
    except Exception as e:
        return APIResponse(
            success=False,

@app.post("/task", response_model=APIResponse)
async def task(req: TaskRequest) -> APIResponse:
    """

    """

    try:
        result: Dict[str, Any] = orchestrator.run_nl(req.cmd, topic=req.topic)
        return APIResponse(
            success=result.get("success", False),
            data=result.get("data"),
            error=result.get("error"),
            diagnostics=result.get("diagnostics"),
            elapsed_ms=_elapsed(start),
        )
    except Exception as e:
        return APIResponse(
            success=False,

@app.get("/pipelines", response_model=APIResponse)
async def list_pipelines() -> APIResponse:
    """
    """

    try:
        return APIResponse(
            success=True,
    except Exception as e:
        return APIResponse(
            success=False,

# ============================================================
#  启动提示
# ============================================================
if __name__ == "__main__":

    print("=" * 60)
    print(f"  FZQ-AI Intelligence API Server v{APP_VERSION}")
    print("  Docs:  http://localhost:8000/docs")
    print("  Health: http://localhost:8000/health")
    print("=" * 60)
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
