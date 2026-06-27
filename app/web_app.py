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

# Core modules
from core.theme import inject_theme
from core.intent_engine import IntentEngine
from core.task_router import TaskRouter
from core.pipelines import PipelineRegistry
from fzq_ai.api.zh_endpoints import router as zh_router


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
# Inject theme
# -------------------------
inject_theme(app)

# -------------------------
# Mount API routers
# -------------------------
app.include_router(zh_router)


# -------------------------
# Init core components
# -------------------------
intent_engine = IntentEngine()
pipeline_registry = PipelineRegistry()
task_router = TaskRouter(pipeline_registry=pipeline_registry)


# -------------------------
# Request model
# -------------------------
class UserQuery(BaseModel):
    text: str
    language: str = "zh"
    session_id: str | None = None


# -------------------------
# Index page
# -------------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"theme_json": json.dumps(app.state.theme)},
    )


# -------------------------
# Smart entry /entry
# -------------------------
@app.post("/entry")
async def entry_point(query: UserQuery):
    # 1) Intent detection
    try:
        intent = intent_engine.detect_intent(
            text=query.text,
            language=query.language,
            session_id=query.session_id,
        )
    except Exception as e:
        raise HTTPException(500, f"IntentEngine error: {e}")

    # Low confidence clarification
    if intent.confidence < 0.4:
        return {
            "intent": intent.to_dict(),
            "route": {},
            "result": {
                "type": "clarification",
                "message": "Intent confidence is low. Please provide more details.",
            },
        }

    # 2) Route
    try:
        route = task_router.route(
            intent=intent,
            language=query.language,
            session_id=query.session_id,
        )
    except Exception as e:
        raise HTTPException(500, f"TaskRouter error: {e}")

    # 3) Execute Pipeline
    try:
        pipeline = route.pipeline
        result = await pipeline.run(
            input_text=query.text,
            intent=intent,
            route=route,
        )
    except Exception as e:
        raise HTTPException(500, f"Pipeline error: {e}")

    # 4) Return structured result
    return {
        "intent": intent.to_dict(),
        "route": route.to_dict(),
        "result": result,
    }


# -------------------------
# Health check
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok", "entry_layer": "v15"}

