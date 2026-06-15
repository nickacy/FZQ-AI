from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any


# ============================
# Article
# ============================

@dataclass
class Article:
    """
    通用新闻文章结构（所有 pipelines / tests 依赖）
    """

    # ---- 必填字段（tests 会用） ----
    title_original: str
    content_original: str = ""  # tests 允许不传 content_original
    region: str = ""

    # ---- 可选字段（tests 会用） ----
    url: str = ""
    source_name: str = ""
    source: str = ""
    fetched_at: datetime = field(default_factory=datetime.utcnow)

    # ---- 风险字段（risk pipeline / alert agent） ----
    risk_level: Optional[int] = None
    risk_type: Optional[str] = None

    # ---- 其他字段（sentiment / narrative） ----
    id: str = ""


# ============================
# IntelMeta
# ============================

@dataclass
class IntelMeta:
    topics: List[str]
    regions: List[str]
    depth: str = "normal"


# ============================
# IntelBundle
# ============================

@dataclass
class IntelBundle:
    """
    单次情报运行的完整结果
    """

    meta: IntelMeta
    articles: List[Article] = field(default_factory=list)

    # ---- tests 需要这些字段 ----
    events: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    risk_summary: Dict[str, Any] = field(default_factory=dict)
    narrative_summary: Dict[str, Any] = field(default_factory=dict)
    sentiment_summary: Dict[str, Any] = field(default_factory=dict)

    fetched_at: datetime = field(default_factory=datetime.utcnow)
