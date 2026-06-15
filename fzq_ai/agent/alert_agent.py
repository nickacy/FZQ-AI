"""
fzq_ai/agent/alert_agent.py — v3.0 Alert Agent (skeleton)
Scans data for high-risk signals and triggers alerts.
"""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class AlertAgent:
    """
    v3.0 — Risk alert scanner.

    Scans recent data for high-risk events and generates alert records.
    """

    def __init__(self, store: Any = None, risk_threshold: int = 4):
        self._store = store
        self._threshold = risk_threshold
        self._alerts: List[Dict[str, Any]] = []

    def scan_for_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Scan data layer for articles with risk_level >= threshold.

        Args:
            hours: Look-back window in hours

        Returns:
            List of alert dicts with title, risk_level, risk_type, url
        """
        alerts: List[Dict[str, Any]] = []
        since = datetime.now() - timedelta(hours=hours)

        if self._store:
            try:
                articles = self._store.query_articles(since=since, limit=200)
                for a in articles:
                    risk = getattr(a, "risk_level", 0) or 0
                    if risk >= self._threshold:
                        alerts.append({
                            "title": getattr(a, "title_original", ""),
                            "risk_level": risk,
                            "risk_type": getattr(a, "risk_type", ""),
                            "url": getattr(a, "url", ""),
                            "source": getattr(a, "source_name", ""),
                        })
            except Exception:
                pass

        self._alerts = alerts
        return alerts

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        return self._alerts

    def clear_alerts(self) -> None:
        self._alerts.clear()


    def detect_major_events(self, bundle=None):
        """v4.5: Rule-based major event detection."""
        alerts = []
        if bundle is None:
            return alerts
        articles = getattr(bundle, 'articles', []) or []
        keywords = ['war', 'attack', 'ceasefire', 'sanction', 'coup',
                    'election', 'missile', 'invasion', 'treaty', 'summit']
        for a in articles:
            title = (getattr(a, 'title_original', '') or '').lower()
            risk = getattr(a, 'risk_level', 0) or 0
            if risk >= 4 or any(k in title for k in keywords):
                alerts.append({
                    'title': getattr(a, 'title_original', ''),
                    'risk_level': risk,
                    'source': getattr(a, 'source_name', ''),
                    'url': getattr(a, 'url', ''),
                })
        return alerts
