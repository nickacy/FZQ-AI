"""
FZQ-AI Backend Entry (FastAPI)
FZQ-AI 后端入口（FastAPI）
----------------------------------------------------
This file defines the main FastAPI application for FZQ-AI.
It exposes:
- Chinese intelligence APIs
- Metrics APIs

本文件定义 FZQ-AI 的主 FastAPI 应用，对外提供：
- 中文情报相关 API
- 系统指标 Metrics API
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# -------------------------------
# Import API routers
# 导入各模块 API 路由
# -------------------------------
from fzq_ai.api.zh_endpoints import router as zh_router
from fzq_ai.api.metrics_endpoints import router as metrics_router


# -------------------------------
# lifespan（替代 on_event）
# -------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context.
    应用生命周期上下文。
    可在此处初始化/清理资源（缓存、模型、连接等）。
    """
    # startup
    # TODO: 如果未来需要初始化缓存、加载模型、连接数据库等，可以放在这里
    yield
    # shutdown
    # TODO: 如果未来需要清理资源（关闭连接、释放句柄等），可以放在这里


# -------------------------------
# FastAPI 初始化
# -------------------------------
app = FastAPI(
    title="FZQ-AI Intelligence System",
    description=(
        "FZQ-AI Backend API for Intelligence Pipelines\n"
        "FZQ-AI 情报系统后端 API（中文情报任务 + 系统指标）"
    ),
    version="4.0.0",
    lifespan=lifespan,
)


# -------------------------------
# CORS 配置（安全：从环境变量读取，而非允许所有来源）
# -------------------------------
_allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8501"
).split(",")
# 去除空白并过滤空字符串
allow_origins = [origin.strip() for origin in _allowed_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-Trace-Id"],
    allow_credentials=True,
)


# -------------------------------
# 挂载各模块路由
# -------------------------------
# 中文情报相关 API
app.include_router(zh_router)

# 系统 Metrics 相关 API
app.include_router(metrics_router)


# -------------------------------
# 全局端点（从 api_server.py 迁移）
# -------------------------------
@app.get("/health")
async def health():
    """健康检查端点。"""
    return {"status": "ok", "service": "FZQ-AI Intelligence API"}


@app.get("/version")
async def version():
    """版本信息端点。"""
    return {
        "version": "4.0.0",
        "build_time": "2026-06-15",
        "service": "FZQ-AI Intelligence API",
    }


# -------------------------------
# 本地运行入口（开发环境）
# -------------------------------
if __name__ == "__main__":
    # 说明：
    # - host="0.0.0.0" 方便在局域网或容器中访问
    # - port=8000 为默认端口，可根据需要调整
    # - reload=True 适合开发阶段，生产环境建议关闭
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
