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
    id: str
    url: str
    source_id: str
    source_name: str
    region: str
    language: str
    fetched_at: datetime

    title_original: str
    content_original: Optional[str]

    content_translated: Optional[str]
    content_snippet_en: Optional[str]

    credibility: float
    bias: float
    propaganda_tags: List[str]


# ============================================================
# IntelMeta —— 元数据（主题、地区等）
# ============================================================

@dataclass
class IntelMeta:
    topics: List[str]
    regions: List[str]
    depth: str


# ============================================================
# IntelBundle —— 新闻 + 元数据
# ============================================================

@dataclass
class IntelBundle:
    meta: IntelMeta
    articles: List[Article]
    events: List[Any]
