from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any

# ============================
# ServiceResult
# ============================

from dataclasses import dataclass
from typing import Any, Optional, Dict


@dataclass
class ServiceResult:
    """
    通用 Pipeline 返回结构
    - success: 是否成功
    - data: 成功时的数据
    - error: 失败时的错误信息
    """

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

    @staticmethod
    def ok(data: Any) -> "ServiceResult":
        return ServiceResult(success=True, data=data, error=None)

    @staticmethod
    def fail(error: str) -> "ServiceResult":
        return ServiceResult(success=False, data=None, error=error)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
        }

    def __bool__(self):
        return self.success


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
