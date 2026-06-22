# fzq_ai/monitor/metrics.py
# FZQ‑AI v13 Metrics Recorder

import time
import json
from pathlib import Path


class MetricsRecorder:

    def __init__(self, path="fzqai_metrics.jsonl"):
        self.path = Path(path)

    def record(self, name: str, duration: float, extra: dict = None):
        data = {
            "timestamp": time.time(),
            "name": name,
            "duration_ms": round(duration * 1000, 2),
        }
        if extra:
            data.update(extra)

        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")


metrics = MetricsRecorder()
