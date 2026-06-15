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
    # ── 新闻情报 (CN/EN/JP) ──
    "新闻": "news-intel", "news": "news-intel", "新闻情报": "news-intel",
    "情报": "news-intel", "news intel": "news-intel", "news-intel": "news-intel",
    "news_intel": "news-intel", "intelligence": "news-intel",
    "rss": "news-intel", "报道": "news-intel", "headlines": "news-intel",
    "latest": "news-intel", "breaking": "news-intel",
    # ── 叙事分析 ──
    "叙事": "narrative", "narrative": "narrative", "叙事分析": "narrative",
    "多阵营": "narrative", "话语": "narrative", "discourse": "narrative",
    "propaganda": "narrative", "故事": "narrative", "故事线": "narrative",
    "framing": "narrative", "media bias": "narrative", "coverage": "narrative",
    # ── 风险 ──
    "风险": "risk", "risk": "risk", "风险分析": "risk", "风险扫描": "risk",
    "威胁": "risk", "threat": "risk", "危机": "risk", "crisis": "risk",
    "danger": "risk", "安全": "risk", "security": "risk",
    "conflict": "risk", "war": "risk", "tension": "risk",
    "sanctions": "risk", "alert": "risk", "warning": "risk",
    # ── 日报 ──
    "日报": "daily-report", "daily": "daily-report",
    "daily report": "daily-report", "每日": "daily-report",
    "报告": "daily-report", "report": "daily-report",
    "每日报告": "daily-report", "daily-report": "daily-report",
    "简报": "daily-report", "briefing": "daily-report",
    "summary": "daily-report", "digest": "daily-report",
    # ── 情感分析 ──
    "情感": "sentiment", "sentiment": "sentiment",
    "情感分析": "sentiment", "态度": "sentiment",
    "情绪": "sentiment", "mood": "sentiment",
    "正面": "sentiment", "负面": "sentiment",
    "positive": "sentiment", "negative": "sentiment",
    "立场": "sentiment", "opinion": "sentiment",
    "bias": "sentiment", "tone": "sentiment",
    # ── 自媒体/社交媒体 (v2.6) ──
    "weibo": "news-intel", "微博": "news-intel",
    "twitter": "news-intel", "x": "news-intel",
    "tiktok": "news-intel", "抖音": "news-intel",
    "youtube": "news-intel", "zhihu": "news-intel", "知乎": "news-intel",
    "reddit": "news-intel", "trending": "news-intel",
    "viral": "news-intel", "social media": "news-intel",
    # ── 地缘政治 (v2.6) ──
    "地缘": "news-intel", "geopolitics": "news-intel",
    "diplomacy": "news-intel", "election": "news-intel",
    "选举": "news-intel", "sanctions": "risk",
    "nato": "news-intel", "eu": "news-intel",
    "brics": "news-intel", "taiwan": "news-intel",
    "ukraine": "news-intel", "gaza": "news-intel",
    "middle east": "news-intel", "中东": "news-intel",
    "africa": "news-intel", "非洲": "news-intel",
    "latin america": "news-intel", "asean": "news-intel",
    # ── 经济/科技 (v2.6) ──
    "经济": "news-intel", "economy": "news-intel",
    "market": "news-intel", "stock": "news-intel",
    "crypto": "news-intel", "bitcoin": "news-intel",
    "ai": "news-intel", "tech": "news-intel",
    "能源": "news-intel", "energy": "news-intel",
    "trade": "news-intel", "贸易": "news-intel",
    "tariff": "risk", "inflation": "risk",
    "recession": "risk", "gdp": "news-intel",
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


# ── 自动 Pipeline 组合规则 (v2.6) ──────────────────────────────

PIPELINE_COMPOSITIONS: Dict[str, List[str]] = {
    "sentiment risk": ["news-intel", "sentiment", "risk"],
    "risk sentiment": ["news-intel", "risk", "sentiment"],
    "sentiment analysis": ["news-intel", "sentiment"],
    "risk analysis": ["news-intel", "risk"],
    "narrative risk": ["news-intel", "narrative", "risk"],
    "full analysis": ["news-intel", "sentiment", "narrative", "risk"],
    "comprehensive": ["news-intel", "sentiment", "narrative", "risk", "daily-report"],
    "舆情风险": ["news-intel", "sentiment", "risk"],
    "全面分析": ["news-intel", "sentiment", "narrative", "risk"],
    "综合分析": ["news-intel", "sentiment", "narrative", "risk", "daily-report"],
    "情感风险": ["news-intel", "sentiment", "risk"],
    "叙事风险": ["news-intel", "narrative", "risk"],
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

    # ── 自然语言路由 (v2.6: 自动组合) ──────────────────────────

    def run_nl(self, user_query: str, **kwargs: Any) -> Dict[str, Any]:
        """
        根据自然语言查询自动选择 Pipeline（支持多 Pipeline 自动组合）。

        Args:
            user_query: 用户自然语言查询
            **kwargs: items, topic, articles, region 等参数

        Returns:
            {task, pipelines_used, results, diagnostics}
        """
        query_lower: str = user_query.lower().strip()

        # —— 1. 检测组合关键词 ——
        pipelines_to_run: List[str] = []
        for comp_key, comp_pipes in PIPELINE_COMPOSITIONS.items():
            if comp_key in query_lower:
                pipelines_to_run = list(comp_pipes)
                break

        # —— 2. 单 Pipeline 关键词匹配 ——
        if not pipelines_to_run:
            for keyword, key in KEYWORD_TASK_MAP.items():
                if keyword.lower() in query_lower:
                    pipelines_to_run = [key]
                    break

        # —— 3. diagnostics ——
        diagnostics: Dict[str, Any] = {
            "topic_queried": user_query,
            "pipelines_selected": pipelines_to_run if pipelines_to_run else None,
            "timestamp": time.time(),
            "language_detected": "zh" if any(
                "\u4e00" <= c <= "\u9fff" for c in user_query
            ) else "en",
        }

        # —— 4. 未知任务 ——
        if not pipelines_to_run:
            diagnostics["available_pipelines"] = list(self.pipelines.keys())
            return {
                "task": user_query,
                "pipelines_used": [],
                "results": {},
                "diagnostics": diagnostics,
                "success": False,
                "error": f"Cannot identify task: '{user_query}'. "
                         f"Available: {list(self.pipelines.keys())}",
                "data": None,
            }

        # —— 5. 执行 Pipeline(s) ——
        results: Dict[str, Any] = {}
        pipeline_results: Dict[str, Any] = {}
        shared_articles: List[Article] = list(kwargs.get("articles", []))

        for pipe_key in pipelines_to_run:
            if pipe_key not in self.pipelines:
                continue

            pipeline = self.pipelines[pipe_key]
            result: ServiceResult

            try:
                if pipe_key == "news-intel":
                    topic = kwargs.get("topic", user_query)
                    result = _to_service_result(pipeline.run(topic=topic))
                    if result.success and result.data:
                        if isinstance(result.data, dict):
                            bundle = result.data.get("intel_bundle", result.data)
                            shared_articles = list(getattr(bundle, "articles", []))
                        else:
                            shared_articles = []
                        diagnostics["articles_found"] = len(shared_articles)
                        diagnostics["rss_sources_checked"] = len(
                            getattr(self, "sources", [])
                        ) or "unknown"

                elif pipe_key == "sentiment":
                    result = _to_service_result(_run_async_safely(
                        pipeline.run(articles=shared_articles)
                    ))
                elif pipe_key == "risk":
                    result = _to_service_result(_run_async_safely(
                        pipeline.run(articles=shared_articles)
                    ))
                elif pipe_key == "narrative":
                    result = _to_service_result(_run_async_safely(
                        pipeline.run(articles=shared_articles)
                    ))
                elif pipe_key == "daily-report":
                    result = _to_service_result(_run_async_safely(
                        pipeline.run(articles=shared_articles)
                    ))
                else:
                    result = ServiceResult.fail(f"Unknown pipeline: {pipe_key}")

                pipeline_results[pipe_key] = {
                    "success": result.success,
                    "data": result.data,
                    "error": result.error,
                }

            except Exception as e:
                pipeline_results[pipe_key] = {
                    "success": False,
                    "error": str(e),
                }

        # —— 6. 构建统一输出 ——
        all_success = all(
            r.get("success", False) for r in pipeline_results.values()
        )
        errors = [
            f"{k}: {v['error']}"
            for k, v in pipeline_results.items()
            if not v.get("success")
        ]

        diagnostics["fallback_used"] = bool(errors)
        diagnostics["errors"] = errors if errors else None

        return {
            "task": user_query,
            "pipelines_used": list(pipeline_results.keys()),
            "results": pipeline_results,
            "diagnostics": diagnostics,
            "success": all_success,
            "data": pipeline_results,
            "error": "; ".join(errors) if errors else None,
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
                result = _to_service_result(pipeline.run(topic=topic))
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

def _to_service_result(raw: Any) -> ServiceResult:
    """Wrap sync str/ServiceResult returns uniformly."""
    if isinstance(raw, ServiceResult):
        return raw
    if isinstance(raw, str):
        return ServiceResult.ok(raw)
    return ServiceResult.ok(str(raw))


def _run_async_safely(maybe_coro: Any) -> Any:
    """
    安全执行异步协程，兼容同步返回值。
    v2.6: 如果传入的是同步值（如 str），直接返回。
    """
    import inspect
    if not inspect.iscoroutine(maybe_coro):
        return maybe_coro  # already a sync result

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(maybe_coro)

    import concurrent.futures

    def _run_in_thread() -> Any:
        new_loop = asyncio.new_event_loop()
        try:
            return new_loop.run_until_complete(maybe_coro)
        finally:
            new_loop.close()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run_in_thread)
        return future.result()
