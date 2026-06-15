"""
fzq_ai.cache.news_cache

轻量级新闻缓存层：
- 内存缓存
- TTL 过期机制
- 可未来替换为 Redis
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, Optional

class NewsCache:
    """
    """

    def __init__(self, ttl_seconds: int = 1800) -> None:
        self.ttl = ttl_seconds
        self._store: Dict[str, Dict[str, Any]] = {}

    def _make_key(self, source: str, query: str) -> str:
        raw = f"{source}:{query}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def get(self, source: str, query: str) -> Optional[Any]:
        key = self._make_key(source, query)
        entry = self._store.get(key)

        if not entry:
            return None

        if time.time() - entry["timestamp"] > self.ttl:
            # 过期
            del self._store[key]
            return None

        return entry["data"]

    def set(self, source: str, query: str, data: Any) -> None:
        key = self._make_key(source, query)
        self._store[key] = {
            "timestamp": time.time(),
            "data": data,

# 全局单例
news_cache = NewsCache()
