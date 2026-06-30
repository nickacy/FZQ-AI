# -*- coding: utf-8 -*-
"""
FZQ-AI Web App (V19 Entry Layer)
Unified entry point.
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

app = FastAPI(title="FZQ-AI Entry Layer V19")

import pathlib
frontend_dir = pathlib.Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserQuery(BaseModel):
    text: str = Field(..., max_length=5000)
    language: str = Field("zh", max_length=10)
    session_id: str | None = None


entry_service = EntryService()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": str(exc)},
    )


@app.post("/entry")
async def entry_endpoint(query: UserQuery):
    """Unified entry: intent classify -> task route -> pipeline execute."""
    result = await entry_service.handle(
        text=query.text,
        language=query.language,
        session_id=query.session_id,
    )
    return {"result": result}


@app.get("/health")
async def health():
    return {"status": "ok", "version": "19.0.0"}
