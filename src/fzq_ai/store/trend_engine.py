from __future__ import annotations
from typing import List, Dict, Any

from fzq_ai.store.intel_store import IntelStore


class TrendEngine:
    """
    v4.5 TrendEngine
    - 风险时间序列加载
    - 简单趋势判断 + 下一步预测
    """

    def __init__(self, store: IntelStore | None = None):
        self.store = store

    def _load_risk_series(self, topic: str) -> List[float]:
        """
        默认实现：从 IntelStore 中按时间顺序取出 topic 的风险评分序列。
        测试中会 monkeypatch 这个方法，所以这里可以安全依赖 store。
        """
        if not self.store:
            return []
        # 假设 store 提供 load_risk_series(topic) 接口；如果没有，后续可以实现
        if hasattr(self.store, "load_risk_series"):
            return self.store.load_risk_series(topic)
        return []

    def _compute_trend(self, series: List[float]) -> str:
        if len(series) < 2:
            return "stable"
        if series[-1] > series[0]:
            return "up"
        if series[-1] < series[0]:
            return "down"
        return "stable"

    def forecast_risk(self, topic: str) -> Dict[str, Any]:
        """
        返回：
        {
          "prediction": float,
          "trend": "up" | "down" | "stable",
          "confidence": float
        }

        测试要求：
        - 返回 dict
        - 必须包含 "prediction" key
        """
        series = self._load_risk_series(topic)
        if not series:
            return {
                "prediction": 0.0,
                "trend": "stable",
                "confidence": 0.0,
            }

        # 简单线性外推：用最后一个值作为下一步预测
        prediction = float(series[-1])
        trend = self._compute_trend(series)
        confidence = min(1.0, len(series) / 10.0)  # 越多点，信心越高

        return {
            "prediction": prediction,
            "trend": trend,
            "confidence": confidence,
        }
