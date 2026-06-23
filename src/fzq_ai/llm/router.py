# fzq_ai/llm/router.py
# FZQ‑AI v13 LLMRouter（Redis + 内存缓存 + TokenMonitor + ModelSelector v3）

from typing import Any, List

from fzq_ai.llm.providers import ProviderRegistry
from fzq_ai.llm.task_registry import TaskRegistry
from fzq_ai.llm.model_selector import model_selector
from fzq_ai.llm.cache import llm_cache
from fzq_ai.llm.cache_redis import redis_llm_cache
from fzq_ai.schemas.llm import LLMRequestSchema, LLMResponseSchema
from fzq_ai.monitor.token_monitor import token_monitor
from fzq_ai.config.global_settings import settings


class LLMRouter:

    def __init__(self) -> None:
        self.task_registry = TaskRegistry()
        self.provider_registry = ProviderRegistry()

    # ------------------------------------------------------------
    # 核心 LLM 调用（带缓存 + fallback + token 记录 + 智能选模）
    # ------------------------------------------------------------
    async def _route_llm_call(self, task_type: str, req: LLMRequestSchema) -> LLMResponseSchema:

        # --------------------------------------------------------
        # Step 0：预算强制保护（优先级最高）
        # --------------------------------------------------------
        alerts = token_monitor.check_budget()
        if any("CRITICAL" in a for a in alerts):
            print("[Budget] CRITICAL: Budget exceeded. Forcing low-cost models.")
            primary = "qwen"
            fallback: List[str] = ["glm", "deepseek"]
        else:
            # 使用 v13 model_selector v3（基于 metrics 的智能选择）
            primary = model_selector.select(task_type)
            # fallback 从全局配置中来，排除 primary
            fallback = [m for m in settings.model_priority.fallback if m != primary]

        # --------------------------------------------------------
        # Step 1：缓存 key
        # --------------------------------------------------------
        cache_key = llm_cache.make_key(task_type, req.prompt, primary)

        # Redis 缓存
        redis_cached = redis_llm_cache.get(cache_key)
        if redis_cached:
            return LLMResponseSchema(content=redis_cached)

        # 内存缓存
        mem_cached = llm_cache.get(cache_key)
        if mem_cached:
            return LLMResponseSchema(content=mem_cached)

        # --------------------------------------------------------
        # Step 2：primary 调用
        # --------------------------------------------------------
        try:
            provider = self.provider_registry.get_provider(primary)
            result = await provider.run(req)

            # 写入缓存
            redis_llm_cache.set(cache_key, result, primary)
            llm_cache.set(cache_key, result, primary)

            # 记录 token
            try:
                token_monitor.record(
                    model=primary,
                    prompt_tokens=result.prompt_tokens,
                    completion_tokens=result.completion_tokens,
                    task_type=task_type,
                )
            except Exception as e:
                print("[TokenMonitor] Failed to record tokens:", e)

            return LLMResponseSchema(content=result)

        except Exception:
            pass

        # --------------------------------------------------------
        # Step 3：fallback 调用
        # --------------------------------------------------------
        for model in fallback:
            try:
                provider = self.provider_registry.get_provider(model)
                result = await provider.run(req)

                # 记录 token
                try:
                    token_monitor.record(
                        model=model,
                        prompt_tokens=result.prompt_tokens,
                        completion_tokens=result.completion_tokens,
                        task_type=task_type,
                    )
                except Exception as e:
                    print("[TokenMonitor] Failed to record tokens:", e)

                return LLMResponseSchema(content=result)

            except Exception:
                continue

        raise RuntimeError(f"All providers failed for task: {task_type}")

    # ------------------------------------------------------------
    # 对外 API（保持不变）
    # ------------------------------------------------------------
    async def route(self, task_type: str, prompt: str, **extra: Any) -> str:
        req = LLMRequestSchema(
            task_type=task_type,
            prompt=prompt,
            **extra,
        )
        resp = await self._route_llm_call(task_type, req)
        return resp.content
