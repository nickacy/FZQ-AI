# fzq_ai/intel/models.py

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


# ---------------------------------------------------------
# SourceConfig
# ---------------------------------------------------------
@dataclass
class SourceConfig:
    id: str
    name: str
    region: str
    language: str
    url: str
    enabled: bool = True
    topic_tags: Optional[List[str]] = None


# ---------------------------------------------------------
# Article
# ---------------------------------------------------------
@dataclass
class Article:
    id: str
    url: str
    source_id: str
    source_name: str
    region: str
    language: str
    fetched_at: datetime

    title_original: str
    content_original: str

    # Phase 5.2
    content_translated: Optional[str] = None
    content_snippet_en: Optional[str] = None

    # Phase 5.3
    credibility: float = 0.0
    bias: float = 0.0
    propaganda_tags: Optional[List[str]] = None


# ---------------------------------------------------------
# EventCluster（占位）
# ---------------------------------------------------------
@dataclass
class EventCluster:
    id: str
    topic: str
    article_ids: List[str]


# ---------------------------------------------------------
# Narrative（占位）
# ---------------------------------------------------------
@dataclass
class Narrative:
    event_id: str
    narratives: List
    consensus_facts: List[str]
    contested_claims: List[str]
    missing_perspectives: List[str]


# ---------------------------------------------------------
# IntelMeta
# ---------------------------------------------------------
@dataclass
class IntelMeta:
    topics: List[str]
    regions: List[str]
    depth: str


# ---------------------------------------------------------
# IntelBundle
# ---------------------------------------------------------
@dataclass
class IntelBundle:
    meta: IntelMeta
    articles: List[Article]
    events: List[EventCluster]
    narratives: List[Narrative]
