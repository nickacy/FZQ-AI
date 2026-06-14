# fzq_ai/agent_hub.py
"""
AgentHub —— 统一 Agent 调度中心
- 管理 LLM 路由和所有 Pipeline
- 对外提供统一的 run_* 入口
"""

from typing import List, Dict, Any, Optional

from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
from fzq_ai.pipelines.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline


class AgentHub:
    """
    统一调度所有 Pipeline 的 Hub。
    - config 保留参数，用于未来扩展
    - Pipeline 全部通过 llm_router 注入
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # 初始化 LLM 路由器（自动 Key Routing）
        self.router = LLMRouter()

        # 初始化所有 Pipeline，注入 LLM 路由
        self.news_pipeline = NewsPipeline(llm_router=self.router)
        self.narrative_pipeline = NarrativePipeline(llm_router=self.router)
        self.risk_pipeline = RiskPipeline(llm_router=self.router)
        self.daily_report_pipeline = DailyReportPipeline(llm_router=self.router)

    # ---------------- 任务入口（同步调用） ----------------

    def run_news(self, topic: str = "") -> Dict[str, Any]:
        """新闻抓取：同步调用"""
        result = self.news_pipeline.run(topic)
        return {"success": result.success, "data": result.data, "error": result.error}

    def run_narrative(self, items: List[str]) -> Dict[str, Any]:
        """叙事分析：将字符串列表转为文章列表后分析"""
        from fzq_ai.domain.models import Article

        articles = [
            Article(title_original=item, content_original=item) for item in items
        ]
        # NarrativePipeline.run 是 async，这里用同步包装
        import asyncio

        result = asyncio.run(self.narrative_pipeline.run(articles=articles))
        return {"success": result.success, "data": result.data, "error": result.error}

    def run_risk(self, items: List[str]) -> Dict[str, Any]:
        """风险分析：将字符串列表转为文章列表后分析"""
        from fzq_ai.domain.models import Article

        articles = [Article(title_original=item) for item in items]
        import asyncio

        result = asyncio.run(self.risk_pipeline.run(articles=articles))
        return {"success": result.success, "data": result.data, "error": result.error}

    def run_daily_report(self, items: List[str]) -> Dict[str, Any]:
        """每日报告：将字符串列表转为文章列表后生成报告"""
        from fzq_ai.domain.models import Article

        articles = [Article(title_original=item) for item in items]
        import asyncio

        result = asyncio.run(self.daily_report_pipeline.run(articles=articles))
        return {"success": result.success, "data": result.data, "error": result.error}

    # ---------------- Metrics 输出 ----------------

    def get_metrics(self) -> Dict[str, Any]:
        """返回调用统计（兼容不同 LLMRouter 实现）"""
        return {
            "llm_router": str(type(self.router).__name__),
            "pipelines": [
                "news_pipeline",
                "narrative_pipeline",
                "risk_pipeline",
                "daily_report_pipeline",
            ],
        }
