# fzq_ai/llm/llm_router.py

import asyncio
import time

from fzq_ai.llm.providers.openai_provider import OpenAIProvider
from fzq_ai.llm.providers.deepseek_provider import DeepSeekProvider
from fzq_ai.llm.providers.gemini_provider import GeminiProvider
from fzq_ai.llm.providers.minimax_client import MiniMaxClient

from fzq_ai.llm.task_registry import TaskRegistry
from fzq_ai.llm.provider_registry import ProviderRegistry
from fzq_ai.logging.llm_logger import LLMLogger


class LLMRouter:
    """
    LLM 路由器（最终架构版）
    - Task Registry（任务能力）
    - Provider Registry（模型能力）
    - JSON mode
    - Provider fallback
    - 自动匹配最优 provider
    - 统一日志（prompt / provider / fallback / latency / errors）
    """

    def __init__(self):
        self.providers = {
            "openai": OpenAIClient(),
            "deepseek": DeepSeekClient(),
            "minimax": MiniMaxClient(),
        }

        self.task_registry = TaskRegistry()
        self.provider_registry = ProviderRegistry()
        self.logger = LLMLogger(log_prompt=False)  # 可切换 True 记录 prompt

    def _score_provider(self, task_cfg, provider_cap):
        score = 0

        if task_cfg.json_mode and provider_cap.json_mode:
            score += 3

        if task_cfg.require_reasoning:
            score += provider_cap.reasoning

        if task_cfg.require_long_context:
            score += provider_cap.long_context

        score += provider_cap.speed * 0.5
        score += (6 - provider_cap.cost) * 0.5
        score += provider_cap.reliability

        return score

    def _select_best_provider(self, task_cfg):
        best = None
        best_score = -1

        for name, cap in self.provider_registry.providers.items():
            score = self._score_provider(task_cfg, cap)
            if score > best_score:
                best_score = score
                best = name

        return best

    async def route(self, task: str, prompt: str) -> str:
        task_cfg = self.task_registry.get(task)
        response_format = {"type": "json_object"} if task_cfg.json_mode else None

        # 1) 自动选择最优 provider
        best_provider_name = self._select_best_provider(task_cfg)
        provider = self.providers[best_provider_name]

        start = time.time()
        try:
            result = await provider.run(prompt, response_format=response_format)
            latency = time.time() - start

            self.logger.log(
                task=task,
                provider=best_provider_name,
                prompt=prompt,
                response=result,
                latency=latency,
            )

            return result

        except Exception as e:
            latency = time.time() - start
            self.logger.log(
                task=task,
                provider=best_provider_name,
                prompt=prompt,
                response=None,
                latency=latency,
                error=e,
            )

        # 2) fallback 链
        for name in task_cfg.fallback_chain:
            if name == best_provider_name:
                continue

            provider = self.providers[name]
            start = time.time()

            try:
                result = await provider.run(prompt, response_format=response_format)
                latency = time.time() - start

                self.logger.log(
                    task=task,
                    provider=name,
                    prompt=prompt,
                    response=result,
                    latency=latency,
                    fallback=True,
                )

                return result

            except Exception as e:
                latency = time.time() - start
                self.logger.log(
                    task=task,
                    provider=name,
                    prompt=prompt,
                    response=None,
                    latency=latency,
                    error=e,
                    fallback=True,
                )

        # 3) 全部失败 → fallback 文本
        fallback_text = f"（⚠️ 所有模型均不可用，任务 {task} 已返回 fallback 文本。）"

        self.logger.log(
            task=task,
            provider="none",
            prompt=prompt,
            response=fallback_text,
            latency=0,
            error="all providers failed",
        )

        return fallback_text


    async def batch(self, task_prompt_list):
        """
        并发执行多个 LLM 任务
        task_prompt_list: List[(task_name, prompt)]
        返回：List[result]
        """

        coroutines = [
            self.route(task, prompt)
            for task, prompt in task_prompt_list
        ]

        # 并发执行所有任务
        results = await asyncio.gather(*coroutines, return_exceptions=True)

        # 将异常转换为 fallback 文本（保持旧行为）
        final = []
        for (task, _), r in zip(task_prompt_list, results):
            if isinstance(r, Exception):
                final.append(f"（⚠️ 任务 {task} 执行失败，已返回 fallback 文本。）")
            else:
                final.append(r)

        return final
