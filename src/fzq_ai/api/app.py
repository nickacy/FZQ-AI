# -*- coding: utf-8 -*-
"""
FZQ-AI FastAPI App (V19-Final)
"""

from __future__ import annotations
from fastapi import FastAPI
from fzq_ai.api.zh_endpoints import router as zh_router

app = FastAPI(
    title="FZQ-AI API",
    version="19.0",
    description="Chinese Intelligence API Endpoints (Policy / Risk / Opinion / Merge)",
)

app.include_router(zh_router)
