# fzq_ai/monitor/token_monitor.py
# Token & Cost Monitoring System (Production-Ready)

import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from fzq_ai.config.settings import settings


class TokenMonitor:

    def __init__(self, log_path="fzqai_token_log.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # 模型单价（USD per 1K tokens）
        self.model_cost = {
            "openai": 0.01,
            "deepseek": 0.002,
            "qwen": 0.0008,
            "glm": 0.001,
        }

        # 从 global_settings.yaml 读取预算配置
        self.daily_cap = settings.get("budget", "daily_cap_usd", default=3)
        self.weekly_cap = settings.get("budget", "weekly_cap_usd", default=10)
        self.alert_threshold = settings.get("budget", "alert_threshold", default=0.8)
        self.auto_downgrade = settings.get("budget", "auto_downgrade", default=True)

    # ------------------------------------------------------------
    # 记录一次模型调用
    # ------------------------------------------------------------
    def record(self, model: str, prompt_tokens: int, completion_tokens: int, task_type: str):
        total = prompt_tokens + completion_tokens
        cost = (total / 1000) * self.model_cost.get(model, 0.001)

        entry = {
            "timestamp": time.time(),
            "datetime": datetime.utcnow().isoformat(),
            "model": model,
            "task_type": task_type,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total,
            "cost_usd": cost,
        }

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        return cost

    # ------------------------------------------------------------
    # 统计函数
    # ------------------------------------------------------------
    def _load_entries(self):
        if not self.log_path.exists():
            return []
        with open(self.log_path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f]

    def daily_cost(self):
        entries = self._load_entries()
        today = datetime.utcnow().date()
        return sum(e["cost_usd"] for e in entries if datetime.fromtimestamp(e["timestamp"]).date() == today)

    def weekly_cost(self):
        entries = self._load_entries()
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        return sum(e["cost_usd"] for e in entries if datetime.fromtimestamp(e["timestamp"]) >= week_ago)

    # ------------------------------------------------------------
    # 预算检查
    # ------------------------------------------------------------
    def check_budget(self):
        d = self.daily_cost()
        w = self.weekly_cost()

        alerts = []

        if d > self.daily_cap * self.alert_threshold:
            alerts.append(f"[ALERT] Daily cost at {d:.2f} USD ({d/self.daily_cap:.0%})")

        if w > self.weekly_cap * self.alert_threshold:
            alerts.append(f"[ALERT] Weekly cost at {w:.2f} USD ({w/self.weekly_cap:.0%})")

        if d > self.daily_cap:
            alerts.append("[CRITICAL] Daily budget exceeded")

        if w > self.weekly_cap:
            alerts.append("[CRITICAL] Weekly budget exceeded")

        return alerts

    # ------------------------------------------------------------
    # 是否需要自动降级模型
    # ------------------------------------------------------------
    def should_downgrade(self):
        if not self.auto_downgrade:
            return False
        return self.daily_cost() > self.daily_cap * self.alert_threshold


token_monitor = TokenMonitor()
