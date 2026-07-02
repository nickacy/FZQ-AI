# app/web_app.py — convenience bridge to src.fzq_ai.api.app
#
# Usage: uvicorn app.web_app:app --reload
#
# This file re-exports the FastAPI app from src/fzq_ai/api/app.py
# so the standard command works without needing to memorize the
# full source-tree import path.

from src.fzq_ai.api.app import app  # noqa: F401
app.include_router(api_v24.router)
