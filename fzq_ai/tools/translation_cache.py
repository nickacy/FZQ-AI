"""
FZQ-AI Tools — Translation Cache v10
使用 SHA-256 缓存翻译结果
"""
import hashlib
from typing import Dict, Any, Optional


class TranslationCache:
    """v10 翻译缓存：
    - key = SHA256(title + content)
    - 缓存 translated text + provider + confidence
    - 内存存储（v10 基础版，未来可扩展为 Redis）
    """

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _make_key(self, text: str) -> str:
        """生成缓存 key：SHA256(text) 前 16 位。"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    def get(self, text: str) -> Optional[Dict[str, Any]]:
        """获取缓存的翻译结果。"""
        return self._cache.get(self._make_key(text))

    def set(self, text: str, result: Dict[str, Any]) -> None:
        """写入缓存。"""
        self._cache[self._make_key(text)] = result

    def clear(self) -> None:
        """清空缓存。"""
        self._cache.clear()

    def stats(self) -> Dict[str, int]:
        """返回缓存统计。"""
        return {
            "total": len(self._cache),
        }
