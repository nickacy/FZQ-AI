# -*- coding: utf-8 -*-
"""
FZQ-AI Entry Layer (V15-Final)
FastAPI + Bloomberg Terminal Theme + IntentEngine + TaskRouter
"""

from __future__ import annotations
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
import json

# 核心模块
from core.theme import inject_theme
from core.intent_engine import IntentEngine
from core.task_router import TaskRouter
from core.pipelines import PipelineRegistry


ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = ROOT / "templates"

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

app = FastAPI(title="FZQ-AI Entry Layer V15")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# 注入主题
# -------------------------
inject_theme(app)


# -------------------------
# 初始化核心组件
# -------------------------
intent_engine = IntentEngine()
pipeline_registry = PipelineRegistry()
task_router = TaskRouter(pipeline_registry=pipeline_registry)


# -------------------------
# 请求模型
# -------------------------
class UserQuery(BaseModel):
    text: str
    language: str = "zh"
    session_id: str | None = None


# -------------------------
# 首页（带主题的 UI）
# -------------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "theme_json": json.dumps(app.state.theme),  # ← 修复关键点
        },
    )


# -------------------------
# 智能入口 /entry
# -------------------------
@app.post("/entry")
async def entry_point(query: UserQuery):

    # 1) 意图识别
    try:
        intent = intent_engine.detect_intent(
            text=query.text,
            language=query.language,
            session_id=query.session_id,
        )
    except Exception as e:
        raise HTTPException(500, f"IntentEngine error: {e}")

    # 低置信度澄清
    if intent.confidence < 0.4:
        return {
            "intent": intent.to_dict(),
            "route": {},
            "result": {
                "type": "clarification",
                "message": "当前意图置信度较低，请补充说明你的需求。",
            },
        }

    # 2) 路由
    try:
        route = task_router.route(
            intent=intent,
            language=query.language,
            session_id=query.session_id,
        )
    except Exception as e:
        raise HTTPException(500, f"TaskRouter error: {e}")

    # 3) 执行 Pipeline
    try:
        pipeline = route.pipeline
        result = await pipeline.run(
            input_text=query.text,
            intent=intent,
            route=route,
        )
    except Exception as e:
        raise HTTPException(500, f"Pipeline error: {e}")

    # 4) 返回结构化结果
    return {
        "intent": intent.to_dict(),
        "route": route.to_dict(),
        "result": result,
    }


# -------------------------
# 健康检查
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok", "entry_layer": "v15"}
