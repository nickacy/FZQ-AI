# fzq_ai/pipelines/refinement_pipeline.py
# Multi‑Model Refinement Pipeline v1

from typing import Dict, List
from fzq_ai.llm.router import LLMRouter

class MultiModelRefinementPipeline:
    """
    多模型协同完善管线：
    1. 多模型并行生成
    2. 汇总所有版本
    3. 由裁判模型生成最终综合版
    """

    def __init__(self):
        self.router = LLMRouter()
        # 参与协同的模型（按你当前账户情况）
        self.models = ["deepseek", "qwen", "glm", "openai"]

    async def _call_single_model(self, task_type: str, prompt: str, model: str) -> str:
        # 这里直接用 router.route，但强制指定 primary_model
        # 简化起见，先用 task_type + prompt，后续可以扩展 extra 参数
        return await self.router.route(task_type, prompt)

    async def generate_candidates(self, task_type: str, prompt: str) -> Dict[str, str]:
        """
        并行调用多个模型，生成候选版本
        """
        results: Dict[str, str] = {}

        # 简化版：串行；你可以改成 asyncio.gather 并行
        for m in self.models:
            # 这里后续可以改成：显式指定 provider，而不是走智能调度
            content = await self._call_single_model(task_type, prompt)
            results[m] = content

        return results

    async def refine(self, task_type: str, prompt: str, candidates: Dict[str, str]) -> str:
        """
        由裁判模型（如 DeepSeek）读取所有候选版本，生成最终综合版
        """
        judge_prompt = self._build_judge_prompt(task_type, prompt, candidates)
        # 裁判模型：DeepSeek
        final = await self.router.route("refinement_judge", judge_prompt)
        return final

    def _build_judge_prompt(self, task_type: str, original_prompt: str, candidates: Dict[str, str]) -> str:
        """
        构造裁判模型的 meta‑prompt，把所有候选版本塞进去
        """
        parts: List[str] = []
        parts.append(f"原始任务类型: {task_type}")
        parts.append(f"原始指令:\n{original_prompt}\n")
        parts.append("以下是不同模型给出的候选版本：\n")

        for model_name, content in candidates.items():
            parts.append(f"【模型: {model_name}】\n{content}\n")

        parts.append(
            "请你作为裁判模型，综合以上所有版本，输出一个：\n"
            "1. 逻辑最清晰\n"
            "2. 事实尽量一致\n"
            "3. 风险点明确\n"
            "4. 语言风格稳定\n"
            "的最终版本。\n"
            "如果存在明显冲突或不确定之处，请在结尾用“【不确定点】”列出。"
        )

        return "\n".join(parts)

    async def run(self, task_type: str, prompt: str) -> str:
        """
        对外统一入口：
        1. 多模型生成候选
        2. 裁判模型综合
        3. 返回最终版本
        """
        candidates = await self.generate_candidates(task_type, prompt)
        final = await self.refine(task_type, prompt, candidates)
        return final
