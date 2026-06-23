# fzq_ai/monitor/token_monitor.py
# FZQ‑AI v13 TokenMonitor（统一配置体系 + JSONL 日志 + 自动预算检查）

import json
from pathlib import Path
from datetime import datetime, timezone

from fzq_ai.config.global_settings import settings


class TokenMonitor:
    """
    v13 TokenMonitor
    - 记录每次 LLM 调用的 token 使用量与成本
    - JSONL 日志格式（可被分析工具直接读取）
    - 支持每日/每周预算检查
    - 支持自动降级（由 Router 调用）
    """

    def __init__(self):
        # -----------------------------------------------------
        # v13 配置体系（来自 global_settings.yaml）
        # -----------------------------------------------------
        self.daily_cap = settings.budget.daily_cap_usd
        self.weekly_cap = settings.budget.weekly_cap_usd
        self.alert_threshold = settings.budget.alert_threshold
        self.auto_downgrade = settings.budget.auto_downgrade

        # -----------------------------------------------------
        # 日志文件路径
        # -----------------------------------------------------
        self.log_path = Path("fzqai_token_log.jsonl")
        self.entries = self._load_entries()

    # ---------------------------------------------------------
    # 加载历史日志
    # ---------------------------------------------------------
    def _load_entries(self):
        if not self.log_path.exists():
            return []
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                return [json.loads(line) for line in f]
        except Exception:
            return []

    # ---------------------------------------------------------
    # 记录一次 token 使用
    # ---------------------------------------------------------
    def record(self, model: str, prompt_tokens: int, completion_tokens: int, task_type: str):
        total_tokens = (prompt_tokens or 0) + (completion_tokens or 0)

        # 成本计算（示例：每 1k tokens = $0.002）
        cost_usd = total_tokens / 1000 * 0.002

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "task_type": task_type,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost_usd": cost_usd,
        }

        # 写入 JSONL
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        self.entries.append(entry)

    # ---------------------------------------------------------
    # 预算检查（Router 会调用）
    # ---------------------------------------------------------
    def check_budget(self):
        alerts = []

        # 今日成本
        today = datetime.now(timezone.utc).date()
        daily_cost = sum(
            e["cost_usd"]
            for e in self.entries
            if datetime.fromisoformat(e["timestamp"]).date() == today
        )

        # 本周成本
        week_start = today.fromisocalendar(today.isocalendar().year, today.isocalendar().week, 1)
        weekly_cost = sum(
            e["cost_usd"]
            for e in self.entries
            if datetime.fromisoformat(e["timestamp"]).date() >= week_start
        )

        # 阈值检查
        if daily_cost >= self.daily_cap * self.alert_threshold:
            alerts.append(f"WARNING: Daily cost {daily_cost:.4f} USD approaching limit {self.daily_cap} USD")

        if daily_cost >= self.daily_cap:
            alerts.append(f"CRITICAL: Daily cost {daily_cost:.4f} USD exceeded limit {self.daily_cap} USD")

        if weekly_cost >= self.weekly_cap * self.alert_threshold:
            alerts.append(f"WARNING: Weekly cost {weekly_cost:.4f} USD approaching limit {self.weekly_cap} USD")

        if weekly_cost >= self.weekly_cap:
            alerts.append(f"CRITICAL: Weekly cost {weekly_cost:.4f} USD exceeded limit {self.weekly_cap} USD")

        return alerts


# 单例
token_monitor = TokenMonitor()
