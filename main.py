# -*- coding: utf-8 -*-
"""
FZQ-AI Unified Entry (V15-Final)
统一入口：API / Web UI
"""

from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run_api():
    """启动 FastAPI"""
    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app:app",  # 根目录 app.py（V4.0.0 FastAPI 入口）
            "--reload",
            "--port",
            "8000",
        ],
        cwd=ROOT,
        check=True,
    )


def run_web():
    """启动 Streamlit Web UI"""
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "src/fzq_ai/ui/web_app.py",
        ],
        cwd=ROOT,
        check=True,
    )


def main():
    parser = argparse.ArgumentParser(description="FZQ-AI Unified Entry")
    parser.add_argument(
        "mode",
        choices=["api", "web"],
        help="Run mode: api (FastAPI) or web (Streamlit)",
    )
    args = parser.parse_args()

    if args.mode == "api":
        run_api()
    elif args.mode == "web":
        run_web()


if __name__ == "__main__":
    main()
