"""增强型缓存系统"""
from __future__ import annotations
import asyncio
import hashlib
import json
import time
from typing import Any, Dict, Optional, Generic, TypeVar
from dataclasses import dataclass
from collections import OrderedDict
import threading

T = TypeVar('T')

@dataclass
class CacheEntry:
    """缓存条目"""
    data: Any
    timestamp: float
    ttl: float
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return time.time() > (self.timestamp + self.ttl)

class EnhancedCache(Generic[T]):
    """增强型缓存系统，支持LRU、TTL和异步操作"""
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 3600.0):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()  # 线程安全
        
    def _hash_key(self, key: str) -> str:
        """生成键的哈希值"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[T]:
        """异步获取缓存值"""
        return await asyncio.get_event_loop().run_in_executor(None, self._get_sync, key)
    
    def _get_sync(self, key: str) -> Optional[T]:
        """同步获取缓存值"""
        with self._lock:
            hashed_key = self._hash_key(key)
            if hashed_key not in self._cache:
                return None
            
            entry = self._cache[hashed_key]
            if entry.is_expired():
                del self._cache[hashed_key]
                return None
            
            # 移动到末尾（LRU）
            self._cache.move_to_end(hashed_key)
            return entry.data
    
    async def set(self, key: str, value: T, ttl: Optional[float] = None) -> None:
        """异步设置缓存值"""
        await asyncio.get_event_loop().run_in_executor(None, self._set_sync, key, value, ttl)
    
    def _set_sync(self, key: str, value: T, ttl: Optional[float] = None) -> None:
        """同步设置缓存值"""
        with self._lock:
            hashed_key = self._hash_key(key)
            ttl = ttl or self.default_ttl
            
            # 检查是否需要清理过期条目
            self._cleanup_expired()
            
            # 如果达到最大大小，移除最老的条目
            if len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)
            
            self._cache[hashed_key] = CacheEntry(
                data=value,
                timestamp=time.time(),
                ttl=ttl
            )
    
    def _cleanup_expired(self) -> None:
        """清理过期条目"""
        current_time = time.time()
        expired_keys = [
            k for k, v in self._cache.items()
            if current_time > (v.timestamp + v.ttl)
        ]
        
        for key in expired_keys:
            del self._cache[key]
    
    async def delete(self, key: str) -> bool:
        """异步删除缓存项"""
        return await asyncio.get_event_loop().run_in_executor(None, self._delete_sync, key)
    
    def _delete_sync(self, key: str) -> bool:
        """同步删除缓存项"""
        with self._lock:
            hashed_key = self._hash_key(key)
            if hashed_key in self._cache:
                del self._cache[hashed_key]
                return True
            return False
    
    async def clear(self) -> None:
        """异步清空缓存"""
        await asyncio.get_event_loop().run_in_executor(None, self._clear_sync)
    
    def _clear_sync(self) -> None:
        """同步清空缓存"""
        with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        with self._lock:
            return len(self._cache)
    
    def keys(self) -> list[str]:
        """获取所有键（不包括哈希值）"""
        with self._lock:
            return list(self._cache.keys())

# 全局缓存实例
llm_response_cache = EnhancedCache(max_size=2000, default_ttl=1800.0)  # 30分钟TTL