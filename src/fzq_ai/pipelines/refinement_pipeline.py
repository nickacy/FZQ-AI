# fzq_ai/pipelines/refinement_pipeline.py
# Multi‑Model Refinement Pipeline v3（评分 + 权重 + 可信度 · 终极版）

import asyncio
from typing import Dict, List
from fzq_ai.llm.router import LLMRouter
from fzq_ai.llm.cache_redis import redis_llm_cache
from fzq_ai.llm.cache import llm_cache


class MultiModelRefinementPipeline:
    """
    多模型协同完善管线（v3 终极版）：
    - 多模型并行生成候选版本
    - 模型评分（score）
    - 模型权重（weight）
    - 综合得分（final score）
    - DeepSeek 裁判模型综合（带可信度）
    - Redis + 内存双缓存
    """

    def __init__(self):
        self.router = LLMRouter()

        # 参与协同的模型（可扩展）
        self.models = ["deepseek", "qwen", "glm", "openai"]

        # 预设模型权重（后续可自适应）
        self.model_weights = {
            "deepseek": 1.3,   # 推理强
            "qwen": 1.2,       # 中文表达强
            "glm": 1.0,        # 事实核查
            "openai": 1.0,     # 语言稳定
        }

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
    # 模型评分逻辑（v1 简单版）
    # ------------------------------------------------------------
    def _score_candidate(self, model: str, content: str) -> float:
        score = 1.0

        if "[ERROR" in content:
            score -= 0.5

        if len(content) < 200:
            score -= 0.2

        return max(score, 0.1)

    # ------------------------------------------------------------
    # 计算模型评分 + 权重 + 综合得分
    # ------------------------------------------------------------
    def _compute_model_scores(self, candidates: Dict[str, str]) -> Dict[str, Dict[str, float]]:
        result = {}
        for model, content in candidates.items():
            base_score = self._score_candidate(model, content)
            weight = self.model_weights.get(model, 1.0)
            final = base_score * weight
            result[model] = {
                "score": base_score,
                "weight": weight,
                "final": final,
            }
        return result

    # ------------------------------------------------------------
    # 构造裁判模型 meta‑prompt（带评分信息）
    # ------------------------------------------------------------
    def _build_judge_prompt(
        self,
        task_type: str,
        original_prompt: str,
        candidates: Dict[str, str],
        model_scores: Dict[str, Dict[str, float]],
    ) -> str:

        parts: List[str] = []
        parts.append(f"任务类型: {task_type}")
        parts.append(f"原始指令:\n{original_prompt}\n")

        parts.append("以下是不同模型的候选版本及其评分：\n")
        for model_name, content in candidates.items():
            ms = model_scores.get(model_name, {})
            parts.append(
                f"【模型: {model_name}】\n"
                f"- 基础评分: {ms.get('score', 1.0):.2f}\n"
                f"- 权重: {ms.get('weight', 1.0):.2f}\n"
                f"- 综合得分: {ms.get('final', 1.0):.2f}\n"
                f"内容:\n{content}\n"
            )

        parts.append(
            "请你作为裁判模型，执行以下步骤：\n"
            "1. 优先参考综合得分较高的模型输出\n"
            "2. 找出所有版本的共同点（共识）\n"
            "3. 找出明显冲突点（冲突）\n"
            "4. 找出事实不一致的地方（事实差异）\n"
            "5. 找出逻辑链差异（推理差异）\n"
            "6. 综合所有版本，生成一个最终版本（综合版），并在开头给出一个 0–1 的“整体可信度”评分\n"
            "7. 如果存在不确定点，请在结尾用“【不确定点】”列出\n"
            "请输出最终综合版。"
        )

        return "\n".join(parts)

    # ------------------------------------------------------------
    # DeepSeek 裁判综合
    # ------------------------------------------------------------
    async def refine(self, task_type: str, prompt: str, candidates: Dict[str, str]) -> str:
        model_scores = self._compute_model_scores(candidates)
        judge_prompt = self._build_judge_prompt(task_type, prompt, candidates, model_scores)
        final = await self.router.route("refinement_judge", judge_prompt)
        return final

    # ------------------------------------------------------------
    # 对外统一入口（带缓存）
    # ------------------------------------------------------------
    async def run(self, task_type: str, prompt: str) -> str:
        cache_key = f"refine::{task_type}::{hash(prompt)}"

        cached = redis_llm_cache.get(cache_key)
        if cached:
            return cached

        mem = llm_cache.get(cache_key)
        if mem:
            return mem

        candidates = await self.generate_candidates(task_type, prompt)
        final = await self.refine(task_type, prompt, candidates)

        redis_llm_cache.set(cache_key, final, "refinement")
        llm_cache.set(cache_key, final, "refinement")

        return final
