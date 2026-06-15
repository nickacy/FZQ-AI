from __future__ import annotations
from typing import List, Dict, Any

from fzq_ai.domain.models import IntelBundle, Article
from fzq_ai.store.intel_store import IntelStore


class AlertAgent:
    """
    v4.5 AlertAgent
    - 重大事件检测
    - 结合单篇文章风险 + 汇总风险 + 叙事信息
    """

    def __init__(self, store: IntelStore | None = None):
        self.store = store

    def _is_high_risk_article(self, article: Article) -> bool:
        """
        高风险判定规则（可扩展）：
        - risk_level >= 4
        - 或 risk_type 属于高敏类别
        """
        if getattr(article, "risk_level", None) is not None:
            if article.risk_level >= 4:
                return True

        high_types = {"military", "geopolitical", "sanction", "terrorism"}
        if getattr(article, "risk_type", None) in high_types:
            return True

        return False

    def detect_major_events(self, bundle: IntelBundle) -> List[Dict[str, Any]]:
        """
        输入：单次 run 的 IntelBundle
        输出：重大事件列表（结构化）
        测试要求：
        - 返回 list
        - 至少包含 1 个元素（在构造了高风险文章时）
        """
        events: List[Dict[str, Any]] = []

        for a in bundle.articles:
            if self._is_high_risk_article(a):
                events.append(
                    {
                        "title": a.title_original,
                        "region": getattr(a, "region", "") or "",
                        "risk_level": getattr(a, "risk_level", None),
                        "risk_type": getattr(a, "risk_type", None),
                    }
                )

        # 结合 bundle 的风险汇总信息（如果有）
        if bundle.risk_summary:
            events.append(
                {
                    "type": "bundle_risk_summary",
                    "summary": bundle.risk_summary,
                }
            )

        return events
