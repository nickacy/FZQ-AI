# fzq_ai/pipelines/scenario_pipeline.py

import asyncio
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.prompts.template import PromptTemplate


SCENARIO_TEMPLATE = PromptTemplate(
    """
你是一名地缘政治情景分析专家，请根据以下主题生成 3 个未来 30 天的可能情景：

主题：$query

请输出：
1. 情景名称
2. 触发因素
3. 可能发展路径
4. 风险等级（低/中/高）
"""
)


class ScenarioPipeline:
    """
    ScenarioPipeline（新增）
    - 保留旧行为（同步 run）
    - 支持 async run_async（并发执行）
    """

    def __init__(self):
        self.llm = LLMRouter()

    # ---------------------------------------------------------
    # 同步入口（保持旧行为）
    # ---------------------------------------------------------
    def run(self, query: str):
        prompt = SCENARIO_TEMPLATE.render(query=query)
        return asyncio.run(self.llm.route("scenario", prompt))

    # ---------------------------------------------------------
    # 异步入口（支持并发）
    # ---------------------------------------------------------
    async def run_async(self, query: str):
        prompt = SCENARIO_TEMPLATE.render(query=query)
        return await self.llm.route("scenario", prompt)
