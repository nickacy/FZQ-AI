# fzq_ai/orchestrator/task_orchestrator.py
# FZQ‑AI v12 TaskOrchestrator（升级版：集成 LLMRouter + TokenMonitor）

import asyncio
from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.pipelines.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.sentiment_pipeline import SentimentPipeline

# ★ 新增：引入 LLMRouter（触发 token_monitor）
from fzq_ai.llm.router import LLMRouter


class TaskOrchestrator:
    """
    Pipeline Orchestrator（增强版）
    - 支持并发执行多个 Pipeline
    - 集成 LLMRouter（触发 token_monitor）
    - 保留旧行为（同步 run()）
    """

    def __init__(self):
        self.news = NewsPipeline()
        self.risk = RiskPipeline()
        self.sentiment = SentimentPipeline()

        # ★ 新增：Router 实例
        self.router = LLMRouter()

    # ---------------------------------------------------------
    # 同步入口（保持旧行为）
    # ---------------------------------------------------------
    def run(self, query: str):
        return asyncio.run(self.run_async(query))

    # ---------------------------------------------------------
    # 异步并发执行（新增 Router 调用）
    # ---------------------------------------------------------
    async def run_async(self, query: str):
        """
        新行为：并发执行多个 Pipeline + LLMRouter
        """

        tasks = [
            self.news.run_async(query=query),
            self.risk.run_async(query=query),
            self.sentiment.run_async(query=query),

            # ★ 新增：触发 LLMRouter（会触发 token_monitor）
            self.router.route(task_type="risk_summary", prompt=query),
        ]

        news, risk, sentiment, llm_output = await asyncio.gather(*tasks)

        return {
            "news": news,
            "risk": risk,
            "sentiment": sentiment,
            "llm_output": llm_output,  # ★ 新增：LLM 输出
        }


# CLI 入口（可选）
if __name__ == "__main__":
    orch = TaskOrchestrator()
    result = orch.run("测试")
    print(result)
