"""
fzq_ai/agent/watchlist_agent.py — v3.0 Watchlist Agent (skeleton)
Monitors a configurable list of topics on a schedule.
"""

from __future__ import annotations
import json
import os
from typing import Any, Dict, List

DEFAULT_WATCHLIST = ["global conflict", "US election", "energy market"]


class WatchlistAgent:
    """
    v3.0 — Topic watchlist monitor.

    Reads topics from watchlist.json, runs pipelines per topic,
    compares with historical data for trend alerts.
    """

    def __init__(self, orchestrator: Any = None,
                 watchlist_path: str = "watchlist.json"):
        self._orchestrator = orchestrator
        self._path = watchlist_path or "watchlist.json"
        self._topics: List[str] = self._load()

    def _load(self) -> List[str]:
        if os.path.exists(self._path):
            with open(self._path, "r", encoding="utf-8") as f:
                return json.load(f)
        return list(DEFAULT_WATCHLIST)

    def _save(self) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._topics, f, indent=2, ensure_ascii=False)

    def add_topic(self, topic: str) -> None:
        if topic not in self._topics:
            self._topics.append(topic)
            self._save()

    def remove_topic(self, topic: str) -> None:
        if topic in self._topics:
            self._topics.remove(topic)
            self._save()

    def list_topics(self) -> List[str]:
        return list(self._topics)

    def run_once(self) -> Dict[str, Any]:
        """Execute pipelines for each topic once."""
        results: Dict[str, Any] = {}
        for topic in self._topics:
            results[topic] = {
                "status": "scanned",
                "topic": topic,
            }
        return results
