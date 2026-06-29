# -*- coding: utf-8 -*-
"""
FZQ-AI Web App (V18 Entry Layer + Resilience + UI Layout)
统一入口：/entry → EntryService.handle()

在 V17 基础上增强，而不是重写或简化：
- 保留：FastAPI 结构、EntryService.handle()、TaskRouter、AdaptedPipelineRegistry
- 已有：ErrorBoundary + SessionState + 自动重试 + 降级策略
- 新增：UI 组件接入能力（通过 ui_layout 描述，让前端按任务类型渲染不同组件）
"""

from __future__ import annotations

import logging
import time
import uuid
import asyncio
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from entry.entry_service import EntryService
from app.entry_adapter import AdaptedPipelineRegistry
from core.task_router import TaskRouter


# ============================================================
# 0. 日志与会话状态 / Logging & Session State
# ============================================================

logger = logging.getLogger("fzq_ai.entry")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

SESSION_STORE: Dict[str, Dict[str, Any]] = {}


def generate_trace_id() -> str:
    return uuid.uuid4().hex


def get_session_state(session_id: Optional[str]) -> Dict[str, Any]:
    if not session_id:
        return {}
    return SESSION_STORE.get(session_id, {})


def update_session_state(
    session_id: Optional[str],
    *,
    last_query: Optional[str] = None,
    last_language: Optional[str] = None,
    last_result: Optional[Any] = None,
    last_intent: Optional[Any] = None,
    last_route: Optional[Any] = None,
) -> None:
    if not session_id:
        return

    state = SESSION_STORE.get(session_id, {})
    if last_query is not None:
        state["last_query"] = last_query
    if last_language is not None:
        state["last_language"] = last_language
    if last_result is not None:
        state["last_result"] = last_result
    if last_intent is not None:
        state["last_intent"] = last_intent
    if last_route is not None:
        state["last_route"] = last_route

    SESSION_STORE[session_id] = state


# ============================================================
# 1. FastAPI 应用初始化 / App Initialization
# ============================================================

app = FastAPI(title="FZQ-AI Entry Layer V18")

app.mount("/static", StaticFiles(directory="frontend"), name="static")

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

from core.pipelines import PipelineRegistry

pipeline_registry = PipelineRegistry()
task_router = TaskRouter(pipeline_registry=pipeline_registry)
entry_service = EntryService(task_router=task_router, pipeline_registry=pipeline_registry)



# ============================================================
# 4. 全局异常处理 / Global Exception Handlers
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    trace_id = generate_trace_id()
    logger.error(
        f"[HTTPException] trace_id={trace_id} "
        f"status_code={exc.status_code} detail={exc.detail} path={request.url.path}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "stage": "http",
            "message": str(exc.detail),
            "trace_id": trace_id,
            "path": str(request.url.path),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    trace_id = generate_trace_id()
    logger.exception(
        f"[UnhandledException] trace_id={trace_id} path={request.url.path} exc={exc}"
    )
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "stage": "unknown",
            "message": "Internal server error",
            "trace_id": trace_id,
            "path": str(request.url.path),
        },
    )


# ============================================================
# 5. UI 组件布局描述 / UI Layout Mapping
# ============================================================

def build_ui_layout(task_type: Optional[str]) -> Dict[str, Any]:
    """
    根据任务类型返回前端应渲染的 UI 组件布局。
    This does NOT 渲染 UI itself, it only describes what the frontend should render.
    """

    if task_type is None:
        return {
            "layout_type": "default",
            "components": [],
        }

    # 风险扫描 → 风险雷达 + 风险摘要
    if task_type == "zh_risk_scan":
        return {
            "layout_type": "risk_dashboard",
            "components": [
                {
                    "id": "risk_block",
                    "type": "risk_block",
                    "position": "left",
                },
                {
                    "id": "risk_radar",
                    "type": "risk_radar",
                    "position": "right",
                },
            ],
        }

    # 舆情版图 → 舆情趋势 + 叙事图谱
    if task_type == "zh_opinion_landscape":
        return {
            "layout_type": "sentiment_dashboard",
            "components": [
                {
                    "id": "sentiment_trend",
                    "type": "sentiment_trend",
                    "position": "top",
                },
                {
                    "id": "narrative_graph",
                    "type": "narrative_graph",
                    "position": "bottom",
                },
            ],
        }

    # 政策简报 → 政策摘要卡片 + 时间线
    if task_type == "zh_policy_brief":
        return {
            "layout_type": "policy_dashboard",
            "components": [
                {
                    "id": "policy_brief_card",
                    "type": "policy_brief_card",
                    "position": "center",
                },
                {
                    "id": "timeline",
                    "type": "timeline",
                    "position": "bottom",
                },
            ],
        }

    # 多源合并 → 多源列表 + 合并结果摘要
    if task_type == "zh_multisource_merge":
        return {
            "layout_type": "merge_dashboard",
            "components": [
                {
                    "id": "source_list",
                    "type": "source_list",
                    "position": "left",
                },
                {
                    "id": "merge_summary",
                    "type": "merge_summary",
                    "position": "right",
                },
            ],
        }

    # 默认布局
    return {
        "layout_type": "default",
        "components": [],
    }


# ============================================================
# 6. 自动重试包装 / Resilient EntryService.handle
# ============================================================

async def _safe_handle_with_retry(
    *,
    text: str,
    language: str,
    session_id: Optional[str],
) -> Any:
    delays = [0.0, 0.5, 1.0]
    last_exc: Optional[Exception] = None

    for attempt, delay in enumerate(delays, start=1):
        try:
            if delay > 0:
                await asyncio.sleep(delay)

            logger.info(
                f"[EntryHandle] attempt={attempt} "
                f"language={language} session_id={session_id}"
            )
            start_time = time.time()

            result = await entry_service.handle(
                text=text,
                language=language,
                session_id=session_id,
            )

            elapsed_ms = (time.time() - start_time) * 1000
            logger.info(
                f"[EntryHandle] success attempt={attempt} "
                f"elapsed_ms={elapsed_ms:.2f} session_id={session_id}"
            )
            return result

        except Exception as exc:
            last_exc = exc
            logger.warning(
                f"[EntryHandle] failed attempt={attempt} "
                f"delay_next={delay} session_id={session_id} exc={exc}"
            )

    assert last_exc is not None
    raise last_exc


# ============================================================
# 7. 入口端点 / Entry Endpoint
# ============================================================

@app.post("/entry")
async def entry_endpoint(query: UserQuery):
    trace_id = generate_trace_id()

    existing_state = get_session_state(query.session_id)

    try:
        result = await _safe_handle_with_retry(
            text=query.text,
            language=query.language,
            session_id=query.session_id,
        )

        intent = None
        route = None
        task_type: Optional[str] = None

        if isinstance(result, dict):
            intent = result.get("intent")
            route = result.get("route")

            if isinstance(intent, dict):
                task_type = intent.get("task_type")

        ui_layout = build_ui_layout(task_type)

        update_session_state(
            query.session_id,
            last_query=query.text,
            last_language=query.language,
            last_result=result,
            last_intent=intent,
            last_route=route,
        )

        return {
            "status": "ok",
            "trace_id": trace_id,
            "result": result,
            "ui_layout": ui_layout,
            "session": {
                "session_id": query.session_id,
                "previous_state": existing_state,
                "last_intent": intent,
                "last_route": route,
            },
        }

    except Exception as exc:
        logger.error(
            f"[EntryEndpointFallback] trace_id={trace_id} "
            f"session_id={query.session_id} exc={exc}"
        )

        cached_state = get_session_state(query.session_id)

        fallback_payload = {
            "status": "error",
            "stage": "pipeline/model/router",
            "message": (
                "System is currently in degraded / offline mode. "
                "Last successful result is returned if available."
            ),
            "trace_id": trace_id,
            "offline": True,
            "session": {
                "session_id": query.session_id,
                "cached_state": cached_state,
            },
        }

        if cached_state.get("last_result") is not None:
            fallback_payload["last_result"] = cached_state["last_result"]

        return JSONResponse(status_code=503, content=fallback_payload)


# ============================================================
# 8. Health Check
# ============================================================

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "0.2.0",
    }
