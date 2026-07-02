"""
FZQ-AI Web Application Layer (V24)
FastAPI unified API router + health check + version endpoint
"""

import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fzq_ai.api.entry import entry_router


def load_version() -> str:
    version_file = Path(__file__).resolve().parents[3] / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "unknown"


def create_app() -> FastAPI:
    app = FastAPI(
        title="FZQ-AI Intelligence System",
        description="Cross-Civilization Personal Intelligence Officer",
        version=load_version()
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(entry_router, prefix="/api")

    # Health check
    @app.get("/health")
    def health():
        return {"status": "ok", "version": load_version()}

    return app
