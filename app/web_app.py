# -*- coding: utf-8 -*-
"""
FZQ-AI Web App (V23-Final)
Unified entry point for /entry, /multi, /autonomy.
"""

from __future__ import annotations

from typing import Any, Dict

import pathlib
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from fzq_ai.schemas.route import RouteResult
from fzq_ai.entry.entry_service_v23 import EntryServiceV23


app = FastAPI(title="FZQ-AI Entry Layer V23", version="23.3.0")

# ------------------------------------------------------------
# Static frontend mount (保持原有前端目录结构)
# ------------------------------------------------------------
frontend_dir = pathlib.Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# ------------------------------------------------------------
# CORS 设置（保留原有本地开发域名）
# ------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

entry_service = EntryServiceV23()


# ------------------------------------------------------------
# 统一异常处理
# ------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": str(exc)},
    )


# ------------------------------------------------------------
# RouteResult → dict 封装
# ------------------------------------------------------------
def wrap(result: RouteResult) -> Dict[str, Any]:
    return {
        "status": result.status,
        "data": result.data,
        "ui_layout": result.ui_layout,
        "debug_info": result.debug_info,
        "trace_id": result.trace_id,
    }


# ------------------------------------------------------------
# /entry — 单智能体统一入口
# ------------------------------------------------------------
@app.post("/entry")
async def entry_endpoint(request: Request):
    payload = await request.json()
    task = payload.get("task")
    ctx = payload.get("ctx", {})
    options = payload.get("options", {})

    result = await entry_service.handle(task, ctx, options)
    return wrap(result)


# ------------------------------------------------------------
# /multi — 多智能体协作入口
# ------------------------------------------------------------
@app.post("/multi")
async def multi_endpoint(request: Request):
    payload = await request.json()
    task = payload.get("task", "multi_agent")
    ctx = payload.get("ctx", {})
    options = payload.get("options", {})

    ctx["multi_agent"] = True
    result = await entry_service.handle(task, ctx, options)
    return wrap(result)


# ------------------------------------------------------------
# /autonomy — 自治智能体入口
# ------------------------------------------------------------
@app.post("/autonomy")
async def autonomy_endpoint(request: Request):
    payload = await request.json()
    task = "autonomy_v23"
    ctx = payload.get("ctx", {})
    options = payload.get("options", {})

    result = await entry_service.handle(task, ctx, options)
    return wrap(result)


# ------------------------------------------------------------
# /health — 健康检查
# ------------------------------------------------------------
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "23.3.0",
        "entry": True,
        "multi": True,
        "autonomy": True,
    }
