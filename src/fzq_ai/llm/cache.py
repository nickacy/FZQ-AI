# fzq_ai/llm/cache.py
# FZQ‑AI v10 LLM Cache v1（内存缓存）

import time
import hashlib
from typing import Dict, Any


class LLMCache:
    """简单高效的内存缓存（支持 TTL）"""

    def __init__(self, ttl_hours: int = 24):
        self.ttl = ttl_hours * 3600
        self.store: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------
    # 生成缓存键
    # ------------------------------------------------------------
    def make_key(self, task_type: str, prompt: str, model: str) -> str:
        raw = f"{task_type}::{model}::{prompt}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------
    # 写入缓存
    # ------------------------------------------------------------
    def set(self, key: str, value: str, model: str):
        self.store[key] = {
            "content": value,
            "model": model,
            "timestamp": time.time(),
        }

    # ------------------------------------------------------------
    # 读取缓存
    # ------------------------------------------------------------
    def get(self, key: str):
        item = self.store.get(key)
        if not item:
            return None

        # TTL 检查
        if time.time() - item["timestamp"] > self.ttl:
            del self.store[key]
            return None

        return item["content"]


# 全局缓存实例
llm_cache = LLMCache()
