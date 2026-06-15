# fzq_ai/store/intel_store.py — v2.7 Data Layer
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json, logging, sqlite3

from fzq_ai.domain.models import Article, IntelBundle, IntelMeta

logger = logging.getLogger(__name__)

@dataclass
class IntelRecord:

class IntelStore:
    """v2.7: Persist IntelBundle, query by topic/time, trend analysis."""

    def __init__(self, db_path: str = "data/intel_store.sqlite") -> None:
        self.db_path = Path(db_path)
        self._is_memory = (str(db_path) == ":memory:")
        if not self._is_memory:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        db = ":memory:" if self._is_memory else self.db_path.as_posix()
        conn = sqlite3.connect(db)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS intel_runs (
                    run_id TEXT PRIMARY KEY,
                "CREATE INDEX IF NOT EXISTS idx_runs_topic_time "
                "ON intel_runs(topic, created_at)")

    def save_bundle(
        self, run_id: str, topic: str, bundle: IntelBundle,
        try:
            with self._get_conn() as conn:
                conn.execute(
                    """INSERT OR REPLACE INTO intel_runs
        except Exception as e:

    def load_latest(self, topic: str, limit: int = 1) -> List[IntelRecord]:
        return self._query(
            "WHERE topic = ? ORDER BY created_at DESC LIMIT ?",

    def load_trend(
        self, topic: str, since: Optional[datetime] = None
        if since:
        return self._query(sql, tuple(params))

    def _query(self, where_clause: str, params: tuple) -> List[IntelRecord]:
        sql = ("SELECT run_id, topic, created_at, provider_snapshot, bundle_json "
               f"FROM intel_runs {where_clause}")
        with self._get_conn() as conn:
            rows = conn.execute(sql, params).fetchall()
        records: List[IntelRecord] = []
        for row in rows:
        return records

def _dict_to_bundle(d: dict) -> IntelBundle:
    """Reconstruct IntelBundle from dict."""
    for ad in d.get("articles", []):
        a = Article(
            title_original=ad.get("title_original", ""),
            url=ad.get("url", ""),
            source_name=ad.get("source_name", ""),
            region=ad.get("region", ""),
            language=ad.get("language", ""),
            content_original=ad.get("content_original", ""),
            credibility=ad.get("credibility", 0.8),
        )
        # Preserve fetched_at if present
        if ad.get("fetched_at"):
            try:
            except (ValueError, TypeError):
                pass
    return IntelBundle(meta=meta, articles=articles, events=events)
