"""
fzq_ai.metrics.recorder

MetricsRecorder：
- 记录 Pipeline / Tool 执行耗时
- 记录成功 / 失败次数
- 未来可扩展为 Prometheus / Grafana
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class MetricsRecorder:
    pipeline_times: Dict[str, float] = field(default_factory=dict)
    pipeline_calls: Dict[str, int] = field(default_factory=dict)
    pipeline_errors: Dict[str, int] = field(default_factory=dict)

    def record(self, name: str, duration: float, success: bool) -> None:
        self.pipeline_times[name] = self.pipeline_times.get(name, 0.0) + duration
        self.pipeline_calls[name] = self.pipeline_calls.get(name, 0) + 1
        if not success:
            self.pipeline_errors[name] = self.pipeline_errors.get(name, 0) + 1


# 全局单例
metrics = MetricsRecorder()
