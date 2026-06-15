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
    version=APP_VERSION,
    description="多模型情报分析系统 · 新闻 · 叙事 · 风险 · 日报",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
#  Pydantic 模型
# ============================================================


class NewsRequest(BaseModel):
    """新闻分析请求"""
    topic: str = Field(..., description="新闻主题关键词", min_length=1, max_length=500)
    max_articles: int = Field(default=50, ge=1, le=200, description="最大文章数")


class NarrativeRequest(BaseModel):
    """叙事分析请求"""
    text: str = Field(..., description="待分析的叙事文本", min_length=1)


class RiskRequest(BaseModel):
    """风险扫描请求"""
    topic: str = Field(..., description="风险主题", min_length=1)


class TaskRequest(BaseModel):
    """任务编排请求"""
    cmd: str = Field(..., description="自然语言任务指令", min_length=1)
    topic: Optional[str] = Field(default=None, description="可选主题限定")


class APIResponse(BaseModel):
    """统一 API 响应结构"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    elapsed_ms: float = 0.0
    diagnostics: Optional[Dict[str, Any]] = None


# ============================================================
#  全局异常处理
# ============================================================


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """捕获所有未处理异常，返回结构化 JSON 而非裸露 traceback。"""
    return JSONResponse(
        status_code=500,
        content=APIResponse(
            success=False,
            error=f"{type(exc).__name__}: {str(exc)}",
            diagnostics={
                "path": str(request.url.path),
                "method": request.method,
            },
        ).model_dump(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """统一 HTTPException 输出格式。"""
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(
            success=False,
            error=exc.detail,
            diagnostics={"path": str(request.url.path)},
        ).model_dump(),
    )


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
    }


@app.get("/health", response_model=APIResponse)
async def health() -> APIResponse:
    """
    健康检查端点。

    返回各 LLM provider 状态及整体服务健康度。
    """
    start: float = time.time()

    provider_status: Dict[str, str] = {}

    # DeepSeek
    deepseek_key: str = os.getenv("DEEPSEEK_API_KEY", "").strip()
    provider_status["deepseek"] = (
        "available" if deepseek_key else "not_configured"
    )

    # OpenAI
    openai_key: str = os.getenv("OPENAI_API_KEY", "").strip()
    provider_status["openai"] = "available" if openai_key else "not_configured"

    # Gemini
    gemini_key: str = os.getenv("GEMINI_API_KEY", "").strip()
    provider_status["gemini"] = "available" if gemini_key else "not_configured"

    return APIResponse(
        success=True,
        data={
            "service": "healthy",
            "providers": provider_status,
        },
        elapsed_ms=_elapsed(start),
    )


@app.get("/version", response_model=APIResponse)
async def version() -> APIResponse:
    """
    版本信息端点。

    返回应用版本号和构建时间。
    """
    start: float = time.time()
    return APIResponse(
        success=True,
        data={
            "version": APP_VERSION,
            "build_time": BUILD_TIME,
            "service": "FZQ-AI Intelligence API",
        },
        elapsed_ms=_elapsed(start),
    )


@app.get("/news", response_model=APIResponse)
def news(topic: str) -> APIResponse:
    """
    新闻情报分析。

    Args:
        topic: 新闻主题关键词
    """
    start: float = time.time()

    try:
        orchestrator: TaskOrchestrator = TaskOrchestrator()
        result: Dict[str, Any] = orchestrator.run_agent(
            agent_name="news-intel", topic=topic
        )
        return APIResponse(
            success=result.get("success", False),
            data=result.get("data"),
            error=result.get("error"),
            elapsed_ms=_elapsed(start),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            elapsed_ms=_elapsed(start),
        )


@app.post("/news/analyze", response_model=APIResponse)
async def news_analyze(req: NewsRequest) -> APIResponse:
    """新闻分析（POST 版本，使用 Pydantic 模型验证）。"""
    start: float = time.time()

    try:
        orchestrator: TaskOrchestrator = TaskOrchestrator()
        result: Dict[str, Any] = orchestrator.run_agent(
            agent_name="news-intel", topic=req.topic
        )
        return APIResponse(
            success=result.get("success", False),
            data=result.get("data"),
            error=result.get("error"),
            elapsed_ms=_elapsed(start),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            elapsed_ms=_elapsed(start),
        )


@app.post("/narrative", response_model=APIResponse)
async def narrative(req: NarrativeRequest) -> APIResponse:
    """叙事分析（POST）。"""
    start: float = time.time()

    try:
        orchestrator: TaskOrchestrator = TaskOrchestrator()
        result: Dict[str, Any] = orchestrator.run_agent(
            agent_name="narrative", text=req.text
        )
        return APIResponse(
            success=result.get("success", False),
            data=result.get("data"),
            error=result.get("error"),
            elapsed_ms=_elapsed(start),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            elapsed_ms=_elapsed(start),
        )


@app.post("/risk", response_model=APIResponse)
async def risk(req: RiskRequest) -> APIResponse:
    """风险扫描（POST）。"""
    start: float = time.time()

    try:
        orchestrator: TaskOrchestrator = TaskOrchestrator()
        result: Dict[str, Any] = orchestrator.run_agent(
            agent_name="risk", topic=req.topic
        )
        return APIResponse(
            success=result.get("success", False),
            data=result.get("data"),
            error=result.get("error"),
            elapsed_ms=_elapsed(start),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            elapsed_ms=_elapsed(start),
        )


@app.post("/task", response_model=APIResponse)
async def task(req: TaskRequest) -> APIResponse:
    """
    任务编排端点。

    支持自然语言任务指令，自动路由到对应 Pipeline。
    """
    start: float = time.time()

    try:
        orchestrator: TaskOrchestrator = TaskOrchestrator()
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
            error=str(e),
            elapsed_ms=_elapsed(start),
        )


@app.get("/pipelines", response_model=APIResponse)
async def list_pipelines() -> APIResponse:
    """
    列出所有可用 Pipeline 及其简要说明。
    """
    start: float = time.time()

    try:
        orchestrator: TaskOrchestrator = TaskOrchestrator()
        pipelines: Dict[str, str] = orchestrator.list_pipelines()
        return APIResponse(
            success=True,
            data=pipelines,
            elapsed_ms=_elapsed(start),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            elapsed_ms=_elapsed(start),
        )


# ============================================================
#  启动提示
# ============================================================
if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print(f"  FZQ-AI Intelligence API Server v{APP_VERSION}")
    print("  Docs:  http://localhost:8000/docs")
    print("  Health: http://localhost:8000/health")
    print("=" * 60)
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
