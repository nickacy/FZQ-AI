# fzq_ai/store/intel_store.py — v2.7 Data Layer
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json, logging, sqlite3

from fzq_ai.domain.models import IntelBundle

logger = logging.getLogger(__name__)


@dataclass
class IntelRecord:
    run_id: str
    topic: str
    created_at: datetime
    provider_snapshot: Dict[str, Any]
    bundle: IntelBundle


class IntelStore:
    """v2.7: Persist IntelBundle, query by topic/time, trend analysis."""

    def __init__(self, db_path: str = "data/intel_store.sqlite") -> None:
        self.db_path = Path(db_path)
        self._is_memory = (str(db_path) == ":memory:")
        # P0-C10: :memory: 模式必须持有单一持久连接，
        # 否则每次 _get_conn() 都新建独立内存库，表与数据随即丢失。
        self._mem_conn: Optional[sqlite3.Connection] = None
        if self._is_memory:
            self._mem_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._mem_conn.row_factory = sqlite3.Row
        else:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if self._is_memory:
            # 复用持久连接；调用方的 `with conn:` 只做 commit/rollback，不会关闭连接。
            assert self._mem_conn is not None
            return self._mem_conn
        conn = sqlite3.connect(self.db_path.as_posix())
        conn.row_factory = sqlite3.Row
        return conn

    def close(self) -> None:
        """关闭 :memory: 模式持有的持久连接（文件模式无持久连接，调用安全）。"""
        if self._mem_conn is not None:
            self._mem_conn.close()
            self._mem_conn = None

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS intel_runs (
                    run_id TEXT PRIMARY KEY,
                    topic TEXT,
                    created_at TEXT,
                    provider_snapshot TEXT,
                    bundle_json TEXT
                )""")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_runs_topic_time "
                "ON intel_runs(topic, created_at)")

    def save_bundle(
        self, run_id: str, topic: str, bundle: IntelBundle,
        provider_snapshot: Dict[str, Any],
        created_at: Optional[datetime] = None,
    ) -> None:
        """持久化 IntelBundle。失败时抛错（不再静默吞异常）。"""
        created_at = created_at or datetime.now(timezone.utc)
        # P0-C9: bundle 是 pydantic BaseModel，必须用 model_dump(mode="json")；
        # dataclasses.asdict 对 BaseModel 必抛 TypeError。
        bj = json.dumps(bundle.model_dump(mode="json"), ensure_ascii=False)
        ps = json.dumps(provider_snapshot, ensure_ascii=False)
        with self._get_conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO intel_runs
                   (run_id, topic, created_at, provider_snapshot, bundle_json)
                   VALUES (?, ?, ?, ?, ?)""",
                (run_id, topic, created_at.isoformat(),
                 ps, bj))

    def load_latest(self, topic: str, limit: int = 1) -> List[IntelRecord]:
        return self._query(
            "WHERE topic = ? ORDER BY created_at DESC LIMIT ?",
            (topic, limit))

    def load_trend(
        self, topic: str, since: Optional[datetime] = None
    ) -> List[IntelRecord]:
        sql = "WHERE topic = ?"
        params: list = [topic]
        if since:
            sql += " AND created_at >= ?"
            params.append(since.isoformat())
        sql += " ORDER BY created_at ASC"
        return self._query(sql, tuple(params))

    def _query(self, where_clause: str, params: tuple) -> List[IntelRecord]:
        sql = ("SELECT run_id, topic, created_at, provider_snapshot, bundle_json "
               f"FROM intel_runs {where_clause}")
        with self._get_conn() as conn:
            rows = conn.execute(sql, params).fetchall()
        records: List[IntelRecord] = []
        for row in rows:
            bd = json.loads(row["bundle_json"])
            bundle = _dict_to_bundle(bd)
            records.append(IntelRecord(
                run_id=row["run_id"], topic=row["topic"],
                created_at=datetime.fromisoformat(row["created_at"]),
                provider_snapshot=json.loads(row["provider_snapshot"]),
                bundle=bundle))
        return records


def _dict_to_bundle(d: dict) -> IntelBundle:
    """Reconstruct IntelBundle from dict.

    存储端使用 model_dump(mode="json")，故直接 model_validate 全字段还原，
    保证 save→load 往返无字段丢失（summary/risk_summary/fetched_at 等一并保留）。
    """
    return IntelBundle.model_validate(d)
