"""
Task Orchestrator — unified pipeline scheduler with NL routing.

v2.5 增强：
- run_nl(): 自然语言任务路由（中英文关键词映射）
- KEYWORD_TASK_MAP: 集中管理的中英文关键词→Pipeline 映射
- list_pipelines(): 列出所有可用 Pipeline
- diagnostics: 路由失败/Pipeline 空结果时附带诊断信息
- 对未知任务类型返回结构化错误
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional

from fzq_ai.domain.models import Article, ServiceResult
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.pipelines.news_pipeline import NewsPipeline
from fzq_ai.pipelines.narrative_pipeline import NarrativePipeline
from fzq_ai.pipelines.risk_pipeline import RiskPipeline
from fzq_ai.pipelines.daily_report_pipeline import DailyReportPipeline
from fzq_ai.pipelines.sentiment_pipeline import SentimentPipeline

# ============================================================
# 关键词 → Pipeline 映射表（中英文统一）
# ============================================================

KEYWORD_TASK_MAP: Dict[str, str] = {
    # ── 新闻情报 ──
    "新闻": "news-intel",
    "news": "news-intel",
    "新闻情报": "news-intel",
    "情报": "news-intel",
    "news intel": "news-intel",
    "news-intel": "news-intel",
    "news_intel": "news-intel",
    "intelligence": "news-intel",
    "rss": "news-intel",
    "报道": "news-intel",
    "headlines": "news-intel",
    "latest": "news-intel",
    # ── 叙事分析 ──
    "叙事": "narrative",
    "narrative": "narrative",
    "叙事分析": "narrative",
    "多阵营": "narrative",
    "话语": "narrative",
    "discourse": "narrative",
    "propaganda": "narrative",
    "故事": "narrative",
    "故事线": "narrative",
    # ── 风险 ──
    "风险": "risk",
    "risk": "risk",
    "风险分析": "risk",
    "风险扫描": "risk",
    "威胁": "risk",
    "threat": "risk",
    "危机": "risk",
    "crisis": "risk",
    "danger": "risk",
    "安全": "risk",
    "security": "risk",
    # ── 日报 ──
    "日报": "daily-report",
    "daily": "daily-report",
    "daily report": "daily-report",
    "每日": "daily-report",
    "报告": "daily-report",
    "report": "daily-report",
    "每日报告": "daily-report",
    "daily-report": "daily-report",
    "简报": "daily-report",
    "briefing": "daily-report",
    # ── 情感分析 ──
    "情感": "sentiment",
    "sentiment": "sentiment",
    "情感分析": "sentiment",
    "态度": "sentiment",
    "情绪": "sentiment",
    "mood": "sentiment",
    "正面": "sentiment",
    "负面": "sentiment",
    "positive": "sentiment",
    "negative": "sentiment",
    "立场": "sentiment",
}

# ── Pipeline 元数据 ───────────────────────────────────────────

PIPELINE_META: Dict[str, Dict[str, str]] = {
    "news-intel": {
        "name": "News Intel Pipeline",
        "description": "RSS/NewsAPI/GDELT 多源新闻抓取 + LLM 摘要 + 风险评分",
        "inputs": "topic (str) — 新闻主题关键词",
        "outputs": "IntelBundle (meta + articles + events)",
    },
    "narrative": {
        "name": "Narrative Pipeline",
        "description": "多阵营叙事分析：按 region 分组 + 提取核心主题关键词",
        "inputs": "articles (List[Article])",
        "outputs": "Dict[region → {themes, articles}]",
    },
    "risk": {
        "name": "Risk Pipeline",
        "description": "多维风险分析：政治/经济/军事/社会/科技关键词扫描 + 评分",
        "inputs": "articles (List[Article])",
        "outputs": "{overall_risk_score, category_intensity, items}",
    },
    "daily-report": {
        "name": "Daily Report Pipeline",
        "description": "每日情报报告生成：结构化 Markdown + 关键事件 + 风险扫描",
        "inputs": "articles (List[Article]), summary (str, optional)",
        "outputs": "Markdown 文本",
    },
    "sentiment": {
        "name": "Sentiment Pipeline",
        "description": "情感/态度分析：中英文关键词匹配 + 整体分布",
        "inputs": "articles (List[Article])",
        "outputs": "{items, distribution, overall_sentiment}",
    },
}


class TaskOrchestrator:
    """统一 Pipeline 调度器，支持 NL 任务路由。"""

    def __init__(self, agent_hub: Any = None) -> None:
        if agent_hub is not None:
            self.router: LLMRouter = agent_hub.router
        else:
            self.router = LLMRouter()

        self.pipelines: Dict[str, Any] = {
            "news-intel": NewsPipeline(llm_router=self.router),
            "narrative": NarrativePipeline(llm_router=self.router),
            "risk": RiskPipeline(llm_router=self.router),
            "daily-report": DailyReportPipeline(llm_router=self.router),
            "sentiment": SentimentPipeline(llm_router=self.router),
        }

    # ── 自然语言路由 ──────────────────────────────────────────

    def run_nl(self, user_query: str, **kwargs: Any) -> Dict[str, Any]:
        """
        根据自然语言查询自动选择 Pipeline 并执行。

        支持中英文关键词匹配，见 KEYWORD_TASK_MAP。

        Args:
            user_query: 用户自然语言查询（如 "分析今天的地缘政治新闻"）
            **kwargs: 传递给 Pipeline 的额外参数

        Returns:
            {
                "success": bool,
                "data": Any,
                "error": Optional[str],
                "diagnostics": {...}
            }
        """
        query_lower: str = user_query.lower().strip()

        # 关键词匹配
        pipeline_key: Optional[str] = None
        for keyword, key in KEYWORD_TASK_MAP.items():
            if keyword.lower() in query_lower:
                pipeline_key = key
                break

        diagnostics: Dict[str, Any] = {
            "topic_queried": user_query,
            "pipeline_selected": pipeline_key,
            "timestamp": time.time(),
        }

        # 未知任务 → 返回结构化错误
        if pipeline_key is None or pipeline_key not in self.pipelines:
            diagnostics["available_pipelines"] = list(self.pipelines.keys())
            diagnostics["suggestion"] = (
                "请使用以下关键词之一：新闻、叙事、风险、日报、情感"
            )
            return {
                "success": False,
                "error": f"无法识别任务类型: '{user_query}'。"
                         f"可用 Pipeline: {list(self.pipelines.keys())}",
                "data": None,
                "diagnostics": diagnostics,
            }

        # 执行 Pipeline
        try:
            pipeline = self.pipelines[pipeline_key]
            result: ServiceResult

            if pipeline_key == "news-intel":
                topic: str = kwargs.get("topic", user_query)
                result = pipeline.run(topic=topic)
            elif pipeline_key == "sentiment":
                articles: List = kwargs.get("articles", [])
                result = _run_async_safely(pipeline.run(articles=articles, **kwargs))
            else:
                articles = kwargs.get("articles", [])
                result = _run_async_safely(
                    pipeline.run(articles=articles, **kwargs)
                )

            diagnostics["result_success"] = result.success

            # 检查空结果
            if result.success and result.data is not None:
                # 对 news-intel 检查 articles 数量
                if pipeline_key == "news-intel":
                    bundle = result.data.get("intel_bundle", result.data)
                    articles_count = len(getattr(bundle, "articles", []))
                    diagnostics["articles_found"] = articles_count
                    if articles_count == 0:
                        diagnostics["warning"] = (
                            f"未找到与 '{user_query}' 匹配的新闻"
                        )

            return {
                "success": result.success,
                "data": result.data,
                "error": result.error,
                "diagnostics": diagnostics,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None,
                "diagnostics": diagnostics,
            }

    # ── 原有调度入口 ──────────────────────────────────────────

    def run(
        self,
        agent_name: str,
        items: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """同步入口（向后兼容）。自动检测为 agent_name 或 NL 查询。"""
        if items is None:
            items = []

        # 先尝试 agent 映射
        agent_map: Dict[str, str] = {
            "daily_report": "daily-report",
            "daily-report": "daily-report",
            "narrative": "narrative",
            "risk": "risk",
            "news-intel": "news-intel",
            "news_intel": "news-intel",
            "sentiment": "sentiment",
        }

        pipeline_key: str = agent_map.get(agent_name) or agent_name

        # 如果不是已知 pipeline，尝试 NL 路由
        if pipeline_key not in self.pipelines:
            return self.run_nl(agent_name, **kwargs)

        pipeline = self.pipelines[pipeline_key]
        articles: List[Article] = (
            kwargs.get("articles")
            or [Article(title_original=str(i)) for i in items]
        )

        try:
            result: ServiceResult
            if pipeline_key == "news-intel":
                topic = " ".join(items) if items else kwargs.get("topic", "")
                result = pipeline.run(topic=topic)
            elif pipeline_key == "sentiment":
                result = _run_async_safely(
                    pipeline.run(articles=articles, **kwargs)
                )
            else:
                result = _run_async_safely(
                    pipeline.run(articles=articles, **kwargs)
                )

            return {
                "success": result.success,
                "data": result.data,
                "error": result.error,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_agent(
        self,
        agent_name: str,
        articles: Optional[List[Article]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """向后兼容包装。"""
        return self.run(agent_name, items=None, articles=articles, **kwargs)

    # ── 信息查询 ──────────────────────────────────────────────

    @staticmethod
    def list_pipelines() -> List[Dict[str, str]]:
        """
        返回所有可用 Pipeline 的名称和简要说明。

        Returns:
            [{"name": "...", "description": "...", "inputs": "...", "outputs": "..."}, ...]
        """
        return [
            {
                "key": key,
                "name": meta["name"],
                "description": meta["description"],
                "inputs": meta["inputs"],
                "outputs": meta["outputs"],
            }
            for key, meta in PIPELINE_META.items()
        ]

    @property
    def router_metrics(self) -> Dict[str, Any]:
        """暴露 LLM Router 指标。"""
        return self.router.metrics


# ============================================================
# 辅助函数
# ============================================================

def _run_async_safely(coro: Any) -> Any:
    """
    安全执行异步协程 — 兼容已有事件循环的情况。
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    import concurrent.futures

    def _run_in_thread() -> Any:
        new_loop = asyncio.new_event_loop()
        try:
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run_in_thread)
        return future.result()
