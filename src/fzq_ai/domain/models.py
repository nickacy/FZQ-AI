from __future__ import annotations
from pydantic import BaseModel, Field
from dataclasses import field
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any


# ============================
# ServiceResult
# ============================

class ServiceResult(BaseModel):
    success: bool = False
    data: Optional[Any] = None
    error: Optional[str] = None

    @classmethod
    def ok(cls, data: Any) -> "ServiceResult":
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str) -> "ServiceResult":
        return cls(success=False, error=error)

    def to_dict(self):
        return self.model_dump()

    def __bool__(self):
        return self.success


# ============================
# Article
# ============================

class Article(BaseModel):
    """
    通用新闻文章结构（tests + pipelines + intel_store 全部依赖）
    """

    # ---- tests 必填 ----
    title_original: str = ""
    content_original: str = ""

    # ---- tests + pipelines ----
    region: str = ""
    url: str = ""
    source_name: str = ""
    source: str = ""
    language: str = ""  # intel_store 反序列化需要
    credibility: float = 0.0  # tests 要求默认 0.0

    # ---- propaganda tags（tests 要求） ----
    propaganda_tags: List[str] = Field(default_factory=list)

    # ---- 时间字段 ----
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # ---- 风险字段 ----
    risk_level: Optional[int] = None
    risk_type: Optional[str] = None

    # ---- 其他字段 ----
    id: str = ""



# ============================
# IntelMeta
# ============================

class IntelMeta(BaseModel):
    topics: List[str] = Field(default_factory=list)
    regions: List[str] = Field(default_factory=list)
    depth: str = "normal"


# ============================
# IntelBundle
# ============================

class IntelBundle(BaseModel):
    """
    单次情报运行的完整结果（tests + pipelines + intel_store 全部依赖）
    """

    meta: IntelMeta = Field(default_factory=IntelMeta)
    articles: List[Article] = Field(default_factory=list)

    # ---- tests 需要这些字段 ----
    events: List[Dict[str, Any]] = Field(default_factory=list)
    summary: str = ""
    risk_summary: Dict[str, Any] = Field(default_factory=dict)
    narrative_summary: Dict[str, Any] = Field(default_factory=dict)
    sentiment_summary: Dict[str, Any] = Field(default_factory=dict)

    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
