# fzq_ai/pipelines/refinement_pipeline.py
# Multi‑Model Refinement Pipeline v2（终极版）

import asyncio
from typing import Dict, List
from fzq_ai.llm.router import LLMRouter
from fzq_ai.llm.cache_redis import redis_llm_cache
from fzq_ai.llm.cache import llm_cache


class MultiModelRefinementPipeline:
    """
    多模型协同完善管线（终极版）：
    1. 多模型并行生成候选版本
    2. DeepSeek 裁判模型综合
    3. Redis + 内存双缓存
    """

    def __init__(self):
        self.router = LLMRouter()
        # 参与协同的模型（可扩展）
        self.models = ["deepseek", "qwen", "glm", "openai"]

    # ------------------------------------------------------------
    # 强制指定模型调用（绕过智能调度）
    # ------------------------------------------------------------
    async def _call_single_model(self, task_type: str, prompt: str, model: str) -> str:
        provider = self.router.provider_registry.get_provider(model)
        req = {
            "task_type": task_type,
            "prompt": prompt,
            "provider": model,
        }
        return await provider.run(req)

    # ------------------------------------------------------------
    # 多模型并行生成候选版本
    # ------------------------------------------------------------
    async def generate_candidates(self, task_type: str, prompt: str) -> Dict[str, str]:
        tasks = [
            self._call_single_model(task_type, prompt, m)
            for m in self.models
        ]
        results_raw = await asyncio.gather(*tasks, return_exceptions=True)

        results = {}
        for model_name, content in zip(self.models, results_raw):
            if isinstance(content, Exception):
                results[model_name] = f"[ERROR from {model_name}] {content}"
            else:
                results[model_name] = content

        return results

    # ------------------------------------------------------------
    # 构造裁判模型 meta‑prompt
    # ------------------------------------------------------------
    def _build_judge_prompt(self, task_type: str, original_prompt: str, candidates: Dict[str, str]) -> str:
        parts: List[str] = []
        parts.append(f"任务类型: {task_type}")
        parts.append(f"原始指令:\n{original_prompt}\n")
        parts.append("以下是不同模型的候选版本：\n")

        for model_name, content in candidates.items():
            parts.append(f"【模型: {model_name}】\n{content}\n")

        parts.append(
            "请你作为裁判模型，执行以下步骤：\n"
            "1. 找出所有版本的共同点（共识）\n"
            "2. 找出明显冲突点（冲突）\n"
            "3. 找出事实不一致的地方（事实差异）\n"
            "4. 找出逻辑链差异（推理差异）\n"
            "5. 综合所有版本，生成一个最终版本（综合版）\n"
            "6. 如果存在不确定点，请在结尾用“【不确定点】”列出\n"
            "请输出最终综合版。"
        )

        return "\n".join(parts)

    # ------------------------------------------------------------
    # 裁判模型（DeepSeek）综合
    # ------------------------------------------------------------
    async def refine(self, task_type: str, prompt: str, candidates: Dict[str, str]) -> str:
        judge_prompt = self._build_judge_prompt(task_type, prompt, candidates)
        final = await self.router.route("refinement_judge", judge_prompt)
        return final

    # ------------------------------------------------------------
    # 对外统一入口（带缓存）
    # ------------------------------------------------------------
    async def run(self, task_type: str, prompt: str) -> str:
        cache_key = f"refine::{task_type}::{hash(prompt)}"

        # Redis 缓存
        cached = redis_llm_cache.get(cache_key)
        if cached:
            return cached

        # 内存缓存
        mem = llm_cache.get(cache_key)
        if mem:
            return mem

        # 多模型生成
        candidates = await self.generate_candidates(task_type, prompt)

        # DeepSeek 裁判综合
        final = await self.refine(task_type, prompt, candidates)

        # 写入缓存
        redis_llm_cache.set(cache_key, final, "refinement")
        llm_cache.set(cache_key, final, "refinement")

        return final
