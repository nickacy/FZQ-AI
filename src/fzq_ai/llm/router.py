# fzq_ai/llm/router.py
# FZQ‑AI v12 LLMRouter（Redis + 内存缓存）

from typing import Any
from fzq_ai.llm.providers import ProviderRegistry
from fzq_ai.llm.task_registry import TaskRegistry
from fzq_ai.llm.model_selector import model_selector
from fzq_ai.llm.cache import llm_cache
from fzq_ai.llm.cache_redis import redis_llm_cache
from fzq_ai.schemas.llm import LLMRequestSchema, LLMResponseSchema


class LLMRouter:

    def __init__(self) -> None:
        self.task_registry = TaskRegistry()
        self.provider_registry = ProviderRegistry()

    async def _route_llm_call(self, task_type: str, req: LLMRequestSchema) -> LLMResponseSchema:

        primary, fallback = model_selector.select(task_type, req.prompt)

        cache_key = llm_cache.make_key(task_type, req.prompt, primary)

        # 1. Redis 缓存
        redis_cached = redis_llm_cache.get(cache_key)
        if redis_cached:
            return LLMResponseSchema(content=redis_cached)

        # 2. 内存缓存
        mem_cached = llm_cache.get(cache_key)
        if mem_cached:
            return LLMResponseSchema(content=mem_cached)

        # 3. primary 调用
        try:
            provider = self.provider_registry.get_provider(primary)
            result = await provider.run(req)

            # 写入 Redis + 内存缓存
            redis_llm_cache.set(cache_key, result, primary)
            llm_cache.set(cache_key, result, primary)

            return LLMResponseSchema(content=result)
        except Exception:
            pass

        # 4. fallback 调用
        for model in fallback:
            try:
                provider = self.provider_registry.get_provider(model)
                result = await provider.run(req)
                return LLMResponseSchema(content=result)
            except Exception:
                continue

        raise RuntimeError(f"All providers failed for task: {task_type}")

    async def route(self, task_type: str, prompt: str, **extra: Any) -> str:
        req = LLMRequestSchema(
            task_type=task_type,
            prompt=prompt,
            **extra,
        )
        resp = await self._route_llm_call(task_type, req)
        return resp.content
