from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any


# ============================
# ServiceResult
# ============================

@dataclass
class ServiceResult:
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

    @staticmethod
    def ok(data: Any) -> "ServiceResult":
        return ServiceResult(success=True, data=data)

    @staticmethod
    def fail(error: str) -> "ServiceResult":
        return ServiceResult(success=False, error=error)

    def to_dict(self):
        return {"success": self.success, "data": self.data, "error": self.error}

    def __bool__(self):
        return self.success


# ============================
# Article
# ============================

@dataclass
class Article:
    """
    通用新闻文章结构（tests + pipelines + intel_store 全部依赖）
    """

    # ---- tests 必填 ----
    title_original: str
    content_original: str = ""

    # ---- tests + pipelines ----
    region: str = ""
    url: str = ""
    source_name: str = ""
    source: str = ""
    language: str = ""  # intel_store 反序列化需要
    credibility: float = 0.0  # tests 要求默认 0.0

    # ---- propaganda tags（tests 要求） ----
    propaganda_tags: List[str] = field(default_factory=list)

    # ---- 时间字段 ----
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # ---- 风险字段 ----
    risk_level: Optional[int] = None
    risk_type: Optional[str] = None

    # ---- 其他字段 ----
    id: str = ""



# ============================
# IntelMeta
# ============================

@dataclass
class IntelMeta:
    topics: List[str] = field(default_factory=list)
    regions: List[str] = field(default_factory=list)
    depth: str = "normal"


# ============================
# IntelBundle
# ============================

@dataclass
class IntelBundle:
    """
    单次情报运行的完整结果（tests + pipelines + intel_store 全部依赖）
    """

    meta: IntelMeta = field(default_factory=IntelMeta)
    articles: List[Article] = field(default_factory=list)

    # ---- tests 需要这些字段 ----
    events: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    risk_summary: Dict[str, Any] = field(default_factory=dict)
    narrative_summary: Dict[str, Any] = field(default_factory=dict)
    sentiment_summary: Dict[str, Any] = field(default_factory=dict)

    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
