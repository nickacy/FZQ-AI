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
