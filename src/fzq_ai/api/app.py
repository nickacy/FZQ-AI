# src/fzq_ai/api/app.py
# V24 — FastAPI 主入口（最终版）
# 保留 V23 兼容层 + 增量增强（V24 三大入口）

from __future__ import annotations

import pathlib
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# V24 入口层
from src.fzq_ai.api.entry_service_v24 import EntryServiceV24

# V23 兼容入口
from src.fzq_ai.api.entry import router as v23_router


# ============================================================
# 1. FastAPI 初始化
# ============================================================

app = FastAPI(title="FZQ-AI Entry Layer V24", version="24.0")


# ============================================================
# 2. CORS 设置（APP 封装需要）
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # APP 封装必须允许全部来源
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 3. 静态前端挂载（frontend/index.html）
# ============================================================

frontend_dir = (
    pathlib.Path(__file__).parent.parent.parent / "frontend"
)

if frontend_dir.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(frontend_dir)),
        name="static",
    )


@app.get("/")
def serve_index():
    """
    默认首页 → 前端 index.html
    """
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"detail": "frontend/index.html not found"}


# ============================================================
# 4. 全局异常处理
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc),
            "path": str(request.url),
        },
    )


# ============================================================
# 5. V24 入口层（主入口）
# ============================================================

entry_service = EntryServiceV24()


@app.post("/entry")
async def entry_v24(payload: dict):
    """
    单智能体入口（V24）
    """
    result = await entry_service.handle_single(payload)
    return result.__dict__


@app.post("/multi")
async def multi_v24(payload: dict):
    """
    多智能体入口（V24）
    """
    result = await entry_service.handle_multi(payload)
    return result.__dict__


@app.post("/autonomy")
async def autonomy_v24(payload: dict):
    """
    自治智能体入口（V24）
    """
    result = await entry_service.handle_autonomy(payload)
    return result.__dict__


# ============================================================
# 6. V23 兼容入口（保留旧系统）
# ============================================================

app.include_router(v23_router, prefix="/v23")


# ============================================================
# 7. 健康检查
# ============================================================

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "24.0"}
