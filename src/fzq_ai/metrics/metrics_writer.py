# src/fzq_ai/metrics/metrics_writer.py
# v13 MetricsWriter – append metrics entries to JSONL

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class MetricsEntry:
    timestamp: float
    datetime: str
    name: str
    duration_ms: float
    extra: Optional[Dict[str, Any]] = None


class MetricsWriter:
    """
    负责将 metrics 记录写入 JSONL 文件：
    - 默认文件名：fzqai_metrics.jsonl
    - 只负责“写入”，不做复杂聚合
    """

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = Path(path) if path is not None else Path("data/logs/fzqai_metrics.jsonl")

    def append(self, name: str, duration_ms: float, extra: Optional[Dict[str, Any]] = None) -> None:
        now = datetime.now(timezone.utc)
        entry = MetricsEntry(
            timestamp=now.timestamp(),
            datetime=now.isoformat(),
            name=name,
            duration_ms=float(duration_ms),
            extra=extra or {},
        )
        self._append_to_file(entry)

    def _append_to_file(self, entry: MetricsEntry) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            json.dump(asdict(entry), f, ensure_ascii=False)
            f.write("\n")


metrics_writer = MetricsWriter()
