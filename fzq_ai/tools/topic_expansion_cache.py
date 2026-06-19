"""
FZQ-AI Tools — Topic Expansion Cache v10
使用 SHA-256 缓存议题扩展结果，TTL 24 小时
"""
import hashlib
import time
from typing import Dict, Any, Optional, List


class TopicExpansionCache:
    """v10 议题扩展缓存：
    - key = SHA256(topic + language)
    - TTL = 24 小时（86400 秒）
    - 内存存储（v10 基础版，未来可扩展为 Redis）
    """

    def __init__(self, ttl_seconds: int = 86400):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl_seconds

    def _make_key(self, topic: str, language: str = "en") -> str:
        """生成缓存 key：SHA256(topic + ':' + language) 前 16 位。"""
        raw = f"{topic}:{language}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def get(self, topic: str, language: str = "en") -> Optional[List[str]]:
        """获取缓存的扩展关键词。过期返回 None。"""
        key = self._make_key(topic, language)
        entry = self._cache.get(key)
        if not entry:
            return None
        if time.time() - entry["timestamp"] > self._ttl:
            del self._cache[key]
            return None
        return entry["keywords"]

    def set(self, topic: str, keywords: List[str], language: str = "en") -> None:
        """写入缓存。"""
        key = self._make_key(topic, language)
        self._cache[key] = {
            "keywords": keywords,
            "timestamp": time.time(),
        }

    def clear(self) -> None:
        """清空缓存。"""
        self._cache.clear()

    def stats(self) -> Dict[str, int]:
        """返回缓存统计。"""
        now = time.time()
        valid = sum(1 for e in self._cache.values() if now - e["timestamp"] <= self._ttl)
        expired = len(self._cache) - valid
        return {
            "total": len(self._cache),
            "valid": valid,
            "expired": expired,
        }
