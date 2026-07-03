"""
FZQ-AI Web Application Layer (V24)

Thin re-export of the unified `api/app.py` FastAPI instance so that:
  - `main.py` (which does `from fzq_ai.ui.web_app import create_app`) still works
  - Docker CMD `uvicorn src.fzq_ai.ui.web_app:app` still works
  - All routes (entry, multi, autonomy, /api/v1/*, /api/zh/*, /v23/*, /metrics, /health)
    are defined in a SINGLE place: `fzq_ai.api.app`

Before V24.2.0 this file defined its own FastAPI app and only mounted
`entry_router` — leaving 80% of the documented endpoints inaccessible.
"""
from fzq_ai.api.app import app  # noqa: F401
from fzq_ai.api.app import _load_cors_origins  # noqa: F401  (re-export for tests)


def create_app():
    """Backward-compat shim: returns the unified FastAPI app from api.app."""
    return app
