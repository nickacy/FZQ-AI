# src/fzq_ai/monitor/token_monitor.py
# v13 Token Monitor – tracks token usage and cost with daily/weekly caps

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

from fzq_ai.config.global_settings import settings


@dataclass
class TokenUsageEntry:
    timestamp: float
    datetime: str
    provider: str
    model: str
    task_type: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    trace_id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class TokenMonitor:
    """
    v13 Token Monitor

    - 读取 global_settings.yaml 中的预算配置：
      settings.budget.daily_cap_usd
      settings.budget.weekly_cap_usd
      settings.budget.alert_threshold
      settings.budget.auto_downgrade

    - 将每次 LLM 调用的 token 使用情况写入 JSONL：
      fzqai_token_log.jsonl

    - 提供简单的聚合能力（可被 metrics / model_selector 使用）
    """

    def __init__(self, log_path: Optional[Path] = None) -> None:
        # 1. 预算配置（带默认值，防止 YAML 缺字段时崩溃）
        budget_cfg = getattr(settings, "budget", None) or {}

        self.daily_cap_usd: float = float(getattr(budget_cfg, "daily_cap_usd", 3.0))
        self.weekly_cap_usd: float = float(getattr(budget_cfg, "weekly_cap_usd", 15.0))
        self.alert_threshold: float = float(getattr(budget_cfg, "alert_threshold", 0.8))
        self.auto_downgrade: bool = bool(getattr(budget_cfg, "auto_downgrade", False))

        # 2. 日志文件路径
        if log_path is None:
            self.log_path = Path("data/logs/fzqai_token_log.jsonl")
        else:
            self.log_path = Path(log_path)

        self._entries: list[TokenUsageEntry] = []
        self._load_entries()

    # ---------------- Core API ----------------

    def record(
        self,
        provider: str,
        model: str,
        task_type: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
        trace_id: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        记录一次 LLM 调用的 token 使用情况，并追加写入 JSONL。
        """
        now = datetime.now(timezone.utc)
        entry = TokenUsageEntry(
            timestamp=now.timestamp(),
            datetime=now.isoformat(),
            provider=provider,
            model=model,
            task_type=task_type,
            prompt_tokens=int(prompt_tokens),
            completion_tokens=int(completion_tokens),
            total_tokens=int(prompt_tokens + completion_tokens),
            cost_usd=float(cost_usd),
            trace_id=trace_id,
            meta=meta or {},
        )

        self._entries.append(entry)
        self._append_to_file(entry)

    # ---------------- Aggregation helpers ----------------

    def total_cost_usd(self) -> float:
        return sum(e.cost_usd for e in self._entries)

    def total_cost_usd_by_provider(self, provider: str) -> float:
        return sum(e.cost_usd for e in self._entries if e.provider == provider)

    def total_tokens_by_provider(self, provider: str) -> int:
        return sum(e.total_tokens for e in self._entries if e.provider == provider)

    # 可以在这里扩展更多聚合方法，供 metrics / model_selector 使用

    # ---------------- Internal helpers ----------------

    def _load_entries(self) -> None:
        """
        启动时加载历史 JSONL 日志（如果存在）。
        """
        if not self.log_path.exists():
            return

        try:
            with self.log_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    self._entries.append(TokenUsageEntry(**data))
        except Exception:
            # 日志损坏时，不让系统崩溃，只是丢弃旧日志
            self._entries = []

    def _append_to_file(self, entry: TokenUsageEntry) -> None:
        """
        将单条记录追加写入 JSONL。
        """
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as f:
            json.dump(asdict(entry), f, ensure_ascii=False)
            f.write("\n")


# 单例实例，供全局使用
token_monitor = TokenMonitor()
