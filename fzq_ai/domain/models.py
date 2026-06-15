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
    title_original: str
    content_original: str
    source: str = ""
    region: str = ""
    risk_level: int | None = None
    risk_type: str | None = None


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
