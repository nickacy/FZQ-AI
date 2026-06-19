"""
FZQ-AI Utils — 通用辅助函数
"""
import hashlib
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def generate_id(prefix: str = "fzq") -> str:
    """生成唯一 ID"""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    rand = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
    return f"{prefix}_{ts}_{rand}"


def utc_now() -> datetime:
    """返回 UTC 当前时间"""
    return datetime.now(timezone.utc)


def safe_get(d: Dict[str, Any], key: str, default: Any = None) -> Any:
    """安全获取字典值"""
    if not isinstance(d, dict):
        return default
    return d.get(key, default)


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + suffix


def flatten_nested(data: Any, sep: str = ".") -> Dict[str, Any]:
    """扁平化嵌套字典"""
    items: Dict[str, Any] = {}
    if isinstance(data, dict):
        for k, v in data.items():
            new_key = f"{sep}{k}" if sep else k
            if isinstance(v, dict):
                items.update(flatten_nested(v, new_key))
            else:
                items[new_key.lstrip(sep)] = v
    return items


def format_latency_ms(start: float, end: Optional[float] = None) -> int:
    """计算并格式化延迟（毫秒）"""
    end = end or time.time()
    return int((end - start) * 1000)
