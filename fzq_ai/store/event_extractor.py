"""
fzq_ai/store/event_extractor.py — v2.7 Event Extractor
Rule-based event extraction from Article titles/descriptions.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime

from fzq_ai.domain.models import Article


@dataclass
class Event:
    title: str
    event_time: Optional[datetime]
    location: str
    actors: List[str]
    action: str
    source_article_id: str


class EventExtractor:
    """v2.7: Extract structured events from news articles using rules."""

    ACTION_VERBS = [
        "announce", "confirm", "launch", "deploy", "sign", "agree",
        "attack", "strike", "kill", "warn", "threaten", "impose",
        "sanction", "elect", "vote", "pass", "reject", "approve",
        "declare", "condemn", "support", "withdraw", "ceasefire",
    ]

    def extract(self, article: Article) -> Optional[Event]:
        """Extract a single event from an article."""
        title = article.title_original or ""
        if not title:
            return None

        # Find action verb
        title_lower = title.lower()
        found_verb = None
        for v in self.ACTION_VERBS:
            if v in title_lower:
                found_verb = v
                break
        if not found_verb:
            return None

        return Event(
            title=title[:120],
            event_time=article.fetched_at,
            location=article.region or "",
            actors=[article.source_name or ""],
            action=found_verb,
            source_article_id=article.url or "",
        )

    def batch_extract(self, articles: List[Article]) -> List[Event]:
        """Extract events from a list of articles."""
        events = []
        for a in articles:
            e = self.extract(a)
            if e:
                events.append(e)
        return events
