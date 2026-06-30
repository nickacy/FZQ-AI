# src/fzq_ai/api/server.py
# V23 — Unified FastAPI Server
# Author: Nick

from fastapi import FastAPI

from fzq_ai.api.entry import router as entry_router
from fzq_ai.api.multi import router as multi_router
from fzq_ai.api.autonomy import router as autonomy_router

app = FastAPI(title="FZQ-AI Unified API (V23)")

app.include_router(entry_router)
app.include_router(multi_router)
app.include_router(autonomy_router)
