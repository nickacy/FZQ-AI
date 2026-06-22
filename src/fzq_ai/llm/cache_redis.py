# fzq_ai/llm/cache_redis.py
# FZQ‑AI v10 LLM Cache v3（Redis 分布式缓存）

import json
import hashlib
import time
import redis


class RedisLLMCache:

    def __init__(self, host="localhost", port=6379, ttl_hours=24):
        self.ttl = ttl_hours * 3600
        self.client = redis.Redis(host=host, port=port, decode_responses=True)

    def make_key(self, task_type: str, prompt: str, model: str) -> str:
        raw = f"{task_type}::{model}::{prompt}"
        h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"fzqai:cache:{h}"

    def get(self, key: str):
        data = self.client.get(key)
        if not data:
            return None
        return json.loads(data)["content"]

    def set(self, key: str, value: str, model: str):
        payload = {
            "content": value,
            "model": model,
            "timestamp": time.time(),
        }
        self.client.setex(key, self.ttl, json.dumps(payload))


redis_llm_cache = RedisLLMCache()
