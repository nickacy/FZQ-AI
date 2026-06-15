"""
fzq_ai/store/trend_engine.py — v2.7 Trend Engine
Aggregates article counts, risk levels, and region distribution over time.
"""

from __future__ import annotations
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from fzq_ai.domain.models import Article
from fzq_ai.store.intel_store import IntelStore


class TrendEngine:
    """v2.7: Time-series trend analysis over IntelStore data."""

    def __init__(self, store: IntelStore):
        self._store = store

    def get_daily_counts(self, topic: str) -> List[Dict[str, Any]]:
        """Return daily article counts for a topic."""
        records = self._store.load_trend(topic)
        daily: Dict[str, int] = defaultdict(int)
        for r in records:
            day = r.created_at.strftime("%Y-%m-%d")
            daily[day] += len(r.bundle.articles) if r.bundle.articles else 0
        return [{"date": d, "count": c} for d, c in sorted(daily.items())]

    def get_risk_trend(self, topic: str) -> List[Dict[str, Any]]:
        """Return average risk level per day."""
        records = self._store.load_trend(topic)
        daily: Dict[str, List[float]] = defaultdict(list)
        for r in records:
            day = r.created_at.strftime("%Y-%m-%d")
            for a in r.bundle.articles or []:
                rl = getattr(a, "risk_level", 0) or 0
                daily[day].append(float(rl))
        return [
            {"date": d, "avg_risk": round(sum(v)/len(v), 2) if v else 0}
            for d, v in sorted(daily.items())
        ]

    def get_region_trend(self, topic: str) -> List[Dict[str, Any]]:
        """Return article counts per region over time."""
        records = self._store.load_trend(topic)
        region_daily: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        for r in records:
            day = r.created_at.strftime("%Y-%m-%d")
            for a in r.bundle.articles or []:
                region = a.region or "unknown"
                region_daily[day][region] += 1
        result = []
        for day in sorted(region_daily):
            entry = {"date": day}
            entry.update(dict(region_daily[day]))
            result.append(entry)
        return result


    def forecast_risk(self, topic: str):
        """v4.5: Simple linear forecast of risk trend."""
        risk_data = self.get_risk_trend(topic)
        if len(risk_data) < 2:
            return {'trend': 'stable', 'forecast_next': 0, 'confidence': 0.0}
        recent = [r['avg_risk'] for r in risk_data[-5:]]
        avg = sum(recent) / len(recent)
        trend = ('rising' if len(recent) >= 2 and recent[-1] > recent[0]
                 else 'falling' if recent[-1] < recent[0] else 'stable')
        return {'trend': trend, 'forecast_next': round(avg, 2),
                'confidence': min(len(recent) / 10, 0.9)}
