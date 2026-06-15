# fzq_ai/storage/intel_store.py — v2.7 Persistent Data Layer
"""SQLite-based local storage for articles, events, and pipeline runs."""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fzq_ai.domain.models import Article

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = "data/fzq_ai_intel.db"

class IntelStore:
    """Unified local storage for all FZQ-AI intelligence data."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path: str = db_path or DEFAULT_DB_PATH
        _parent = Path(self.db_path).parent
        _parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None

    # ── Connection ───────────────────────────────────────────────

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    # ── Schema ───────────────────────────────────────────────────

    def init_schema(self) -> None:
        conn = self._get_conn()
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

        """)
        logger.info("IntelStore schema initialized at %s", self.db_path)

    # ── Write ────────────────────────────────────────────────────

    def save_articles(
        self,
        """Save articles with URL-based dedup. Returns count of new rows."""
        if not articles:
            return 0

        conn = self._get_conn()
        saved = 0

        for a in articles:
            try:
                if not url and not title:

                # Dedup check
                if url:
                        "SELECT id FROM articles WHERE url=?", (url,)
                    ).fetchone()
                    if existing:
                            "UPDATE articles SET topic_query=?, pipeline_tag=? WHERE id=?",

                    """INSERT INTO articles
                        "",
                        "",
            except Exception as e:

        return saved

    # ── Read ─────────────────────────────────────────────────────

    def query_articles(
        self,
        """Query articles with optional filters."""
        conn = self._get_conn()
        sql = "SELECT * FROM articles WHERE 1=1"

        if topic:
        if region:
        if since:

        return [dict(r) for r in rows]

    def get_trend_counts(
        self,
        """Return daily article counts for trend visualization."""
        conn = self._get_conn()

        # Parse window: "7d", "30d", "1d"
        if window.endswith("d"):
            try:
            except ValueError:

        return [dict(r) for r in rows]

    def save_run(self, task: str, pipelines_used: List[str], article_count: int = 0) -> None:
        """Record an orchestrator run for audit trail."""
        try:
            conn = self._get_conn()
            conn.execute(
                "INSERT INTO runs (task, pipelines_used, article_count) VALUES (?,?,?)",
                (task, json.dumps(pipelines_used), article_count),
            )
        except Exception as e:

# ── Module-level singleton ──

_store: Optional[IntelStore] = None

def get_store(db_path: Optional[str] = None) -> IntelStore:
    """Get or create the singleton IntelStore instance."""
    if _store is None:
    return _store
