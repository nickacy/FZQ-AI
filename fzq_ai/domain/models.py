# fzq_ai/domain/models.py

from __future__ import annotations
from typing import List, Optional, Any, Dict
from dataclasses import dataclass
from datetime import datetime

# ============================================================
# ServiceResult —— 所有 Pipeline 的统一返回结构
# ============================================================


@dataclass
class ServiceResult:
    success: bool
    data: Any
    error: Optional[str] = None

    @staticmethod
    def ok(data: Any) -> "ServiceResult":
        return ServiceResult(success=True, data=data)

    @staticmethod
    def fail(error: str) -> "ServiceResult":
        return ServiceResult(success=False, data=None, error=error)


# ============================================================
# Article —— 新闻的标准结构
# ============================================================


@dataclass
class Article:
    id: str = ""
    url: str = ""
    source_id: str = ""
    source_name: str = ""
    region: str = ""
    language: str = ""
    fetched_at: datetime = None  # type: ignore

    title_original: str = ""
    content_original: Optional[str] = None

    content_translated: Optional[str] = None
    content_snippet_en: Optional[str] = None

    credibility: float = 0.0
    bias: float = 0.0
    propaganda_tags: List[str] = None  # type: ignore

    def __post_init__(self):
        if self.fetched_at is None:
            self.fetched_at = datetime.now()
        if self.propaganda_tags is None:
            self.propaganda_tags = []


# ============================================================
# IntelMeta —— 元数据（主题、地区等）
# ============================================================


@dataclass
class IntelMeta:
    topics: List[str] = None  # type: ignore
    regions: List[str] = None  # type: ignore
    depth: str = "normal"

    def __post_init__(self):
        if self.topics is None:
            self.topics = []
        if self.regions is None:
            self.regions = []


# ============================================================
# IntelBundle —— 新闻 + 元数据
# ============================================================


@dataclass
class IntelBundle:
    meta: IntelMeta = None  # type: ignore
    articles: List[Article] = None  # type: ignore
    events: List[Any] = None  # type: ignore

    def __post_init__(self):
        if self.meta is None:
            self.meta = IntelMeta()
        if self.articles is None:
            self.articles = []
        if self.events is None:
            self.events = []
