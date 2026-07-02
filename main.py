"""
FZQ-AI Unified Entry Layer (V24)
FastAPI + Uvicorn unified startup
"""

import uvicorn
from fzq_ai.ui.web_app import create_app


def main():
    app = create_app()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )


if __name__ == "__main__":
    main()
