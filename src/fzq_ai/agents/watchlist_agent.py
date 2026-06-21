from __future__ import annotations
from typing import Any, Dict, List
import math

from fzq_ai.store.intel_store import IntelStore


class WatchlistAgent:
    """
    v4.5 WatchlistAgent
    - 叙事变化检测（Narrative Shift）
    - 结合 embedding + 主题关键词
    """

    def __init__(self, store: IntelStore | None = None):
        self.store = store

    # ====== 内部工具方法 ======

    def _cosine(self, v1: List[float], v2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(v1, v2))
        n1 = math.sqrt(sum(a * a for a in v1))
        n2 = math.sqrt(sum(b * b for b in v2))
        if n1 == 0 or n2 == 0:
            return 0.0
        return dot / (n1 * n2)

    def _get_last_two_runs(self, topic: str) -> List[Dict[str, Any]]:
        """
        默认实现：从 IntelStore 取最近两次 run 的叙事 embedding。
        测试中会 monkeypatch 这个方法，所以这里可以安全依赖 store。
        """
        if not self.store:
            return []

        bundles = self.store.load_latest(topic, limit=2)
        runs: List[Dict[str, Any]] = []
        for b in bundles:
            emb = getattr(b, "narrative_embedding", None)
            if emb:
                runs.append({"embedding": emb, "bundle": b})
        return runs

    # ====== 对外主方法 ======

    def detect_narrative_shift(self, topic: str) -> Dict[str, Any]:
        """
        返回：
        {
          "topic": str,
          "shift_score": float,
          "shift_detected": bool,
          "new_themes": [...],
          "lost_themes": [...]
        }

        测试要求：
        - 返回 dict
        - 必须包含 "shift_score" key
        """
        runs = self._get_last_two_runs(topic)
        if len(runs) < 2:
            return {
                "topic": topic,
                "shift_score": 0.0,
                "shift_detected": False,
                "new_themes": [],
                "lost_themes": [],
            }

        v1 = runs[0]["embedding"]
        v2 = runs[1]["embedding"]

        cosine_sim = self._cosine(v1, v2)
        shift_score = 1.0 - cosine_sim  # 越大表示变化越大

        # 主题变化（如果 narrative_summary 存在）
        b1 = runs[0].get("bundle")
        b2 = runs[1].get("bundle")
        themes1 = set((b1.narrative_summary or {}).keys()) if b1 else set()
        themes2 = set((b2.narrative_summary or {}).keys()) if b2 else set()

        new_themes = sorted(list(themes2 - themes1))
        lost_themes = sorted(list(themes1 - themes2))

        return {
            "topic": topic,
            "shift_score": shift_score,
            "shift_detected": shift_score > 0.3,
            "new_themes": new_themes,
            "lost_themes": lost_themes,
        }
