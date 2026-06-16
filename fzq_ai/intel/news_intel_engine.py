"""fzq_ai/intel/news_intel_engine.py - v6.0 News Intelligence Engine"""
from __future__ import annotations
import asyncio, json, logging
from typing import Any, Dict, List, Optional

from fzq_ai.domain.models import Article, ServiceResult
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.pipelines.news_fetcher import fetch_all_news

logger = logging.getLogger(__name__)

# v6.0: 区域关键词推断
REGION_KEYWORDS = {
    "north_america": ["us", "america", "canada", "washington"],
    "europe": ["eu", "europe", "brussels", "nato", "france", "germany"],
    "china": ["china", "beijing", "shanghai", "taiwan"],
    "southeast_asia": ["asean", "vietnam", "indonesia", "philippines"],
    "middle_east": ["iran", "israel", "gaza", "saudi", "uae", "syria"],
    "africa": ["africa", "nigeria", "kenya", "south africa"],
    "latin_america": ["brazil", "mexico", "argentina", "venezuela"],
}


class NewsIntelEngine:
    """v6.0: Multi-language, multi-region, event-level extraction engine."""

    def __init__(self, llm_router=None):
        self.router = llm_router or LLMRouter()

    def search(self, query: str) -> ServiceResult:
        """Execute a full intelligence search with structured output."""
        if not query:
            return ServiceResult.fail("Query required")
        try:
            articles = fetch_all_news(query)
            regions = self._infer_regions(query)
            lang = self._detect_lang(query)
            events = self._extract_events(query, articles)
            result = {
                "query": query,
                "language": lang,
                "articles_count": len(articles),
                "regions": regions,
                "events": events[:20],
                "stats": {
                    "count": len(articles),
                    "languages": self._count_langs(articles),
                    "regions": self._count_regions(articles),
                }
            }
            return ServiceResult.ok(result)
        except Exception as e:
            logger.warning("NewsIntelEngine.search failed: %s", e)
            return ServiceResult.fail(str(e))

    def _detect_lang(self, text: str) -> str:
        """Detect language from Unicode range."""
        for ch in text:
            cp = ord(ch)
            if 0x4e00 <= cp <= 0x9fff:
                return "zh"
            if 0x3040 <= cp <= 0x30ff:
                return "ja"
            if 0xac00 <= cp <= 0xd7af:
                return "ko"
            if 0x0600 <= cp <= 0x06ff:
                return "ar"
            if 0x0400 <= cp <= 0x04ff:
                return "ru"
        return "en"

    def _infer_regions(self, query: str) -> list:
        """Infer target regions from query keywords."""
        q = query.lower()
        regions = []
        for region, keywords in REGION_KEYWORDS.items():
            if any(k in q for k in keywords):
                regions.append(region)
        return regions or ["global"]

    def _extract_events(self, query: str, articles: list) -> list:
        """Extract structured events using v6.0 LLM routing."""
        if not articles:
            return []
        headlines = []
        for i, a in enumerate(articles[:30]):
            t = a.title_original or ""
            s = a.source_name or ""
            r = a.region or "unknown"
            headlines.append("[%d] %s | %s | %s" % (i+1, t[:100], s, r))
        text_block = "\n".join(headlines)
        prompt = (
            "Extract key EVENTS from these news headlines. "
            "Return JSON array with keys: title, region, source, action, date. "
            "Only return the JSON array.\n\n"
            "Headlines:\n" + text_block
        )
        try:
            raw = asyncio.run(self.router.route("event_extraction", prompt))
            text = raw.strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text)
        except Exception:
            return [{
                "title": (a.title_original or "")[:100],
                "region": a.region or "unknown",
                "source": a.source_name or "",
                "action": "reported",
                "date": str(getattr(a, "fetched_at", ""))
            } for a in articles[:10]]

    def _count_langs(self, articles: list) -> dict:
        counts = {}
        for a in articles:
            lang = a.language or "unknown"
            counts[lang] = counts.get(lang, 0) + 1
        return counts

    def _count_regions(self, articles: list) -> dict:
        counts = {}
        for a in articles:
            r = a.region or "unknown"
            counts[r] = counts.get(r, 0) + 1
        return counts
