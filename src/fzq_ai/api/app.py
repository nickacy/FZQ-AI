# src/fzq_ai/api/app.py
# V24 — FastAPI 主入口（最终版）
# 保留 V23 兼容层 + 增量增强（V24 三大入口）

from __future__ import annotations

import os
import pathlib
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from fzq_ai.api.v24_routes import router as v24_router

# V24 中文情报（zh_risk_scan / zh_policy_brief / zh_opinion_landscape / zh_multisource_merge）
from fzq_ai.api.zh_endpoints import router as zh_router

# V24 入口层
from fzq_ai.api.entry_service_v24 import EntryServiceV24

# V23 兼容入口（仅 /v23/entry）
from fzq_ai.api.entry import router as v23_router
from fzq_ai.schemas.route import RouteResult

# Metrics API（/api/metrics, /api/pipelines）
from fzq_ai.api.metrics_endpoints import router as metrics_router

# Observability
try:
    from fzq_ai.utils.monitoring import get_metrics_response
except Exception:  # pragma: no cover — monitoring is optional
    get_metrics_response = None


# ============================================================
# 1. FastAPI 初始化
# ============================================================

app = FastAPI(title="FZQ-AI API", version="24.0.0")


# ============================================================
# 2. CORS 设置（从环境变量读白名单；不允许 * + credentials）
# ============================================================

def _load_cors_origins() -> list[str]:
    """Load allowed CORS origins from environment.
    - ALLOWED_ORIGINS="http://a,http://b"  → list
    - 缺省：仅允许本地前端（开发期）
    - APP 模式（APP_MODE=mobile）下允许 chrome-extension://* 与 http://localhost
      （移动 WebView 容器）；仍避免与 credentials=True 冲突
    """
    raw = os.getenv("ALLOWED_ORIGINS", "").strip()
    if raw:
        origins = [o.strip() for o in raw.split(",") if o.strip()]
    else:
        origins = [
            "http://localhost:3000",
            "http://localhost:8501",
            "http://127.0.0.1:3000",
        ]
    if os.getenv("APP_MODE", "").lower() == "mobile":
        # APP 封装允许的来源（WebView 默认不会发 Origin，无需 credentials）
        origins.extend(["null"])  # file:// 或 webview 内请求
    return origins


_cors_origins = _load_cors_origins()
# 若配置了 credentials，origins 不能含 "*"
_allow_credentials = bool(_cors_origins) and "*" not in _cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 3. 静态前端挂载（frontend/index.html）
# ============================================================

project_root = pathlib.Path(__file__).resolve().parents[3]
frontend_dir = project_root / "frontend-react" / "dist"

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
    return {"detail": "frontend-react/dist/index.html not found; run frontend build first"}


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
# 5. V24 路由（前端契约 /api/v1/*）
# ============================================================

app.include_router(v24_router)


# ============================================================
# 6. V24 入口层（主入口，兼容层）
# ============================================================

entry_service = EntryServiceV24()


@app.post("/entry", response_model=RouteResult)
async def entry_v24(payload: dict):
    """
    单智能体入口（V24）
    """
    result = await entry_service.handle_single(payload)
    return result


@app.post("/multi", response_model=RouteResult)
async def multi_v24(payload: dict):
    """
    多智能体入口（V24）
    """
    result = await entry_service.handle_multi(payload)
    return result


@app.post("/autonomy", response_model=RouteResult)
async def autonomy_v24(payload: dict):
    """
    自治智能体入口（V24）
    """
    result = await entry_service.handle_autonomy(payload)
    return result


# ============================================================
# 7. V23 兼容入口（保留旧系统）
# ============================================================

app.include_router(v23_router, prefix="/v23")


# ============================================================
# 7b. V24 中文情报端点（/api/zh/*）
# ============================================================

app.include_router(zh_router)


# ============================================================
# 7c. Metrics API（/api/metrics, /api/pipelines）
# ============================================================

app.include_router(metrics_router)


# ============================================================
# 7d. Prometheus 指标（如果 prometheus_client 可用）
# ============================================================

if get_metrics_response is not None:
    @app.get("/metrics", response_class=PlainTextResponse)
    def metrics_endpoint():
        return get_metrics_response()


# ============================================================
# 8. 健康检查
# ============================================================

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "24.0.0"}
