"""
pipelines/narrative_pipeline.py

FZQ‑AI v2.5 — LLM-based Narrative Analysis Pipeline.

功能：
- 对新闻列表进行叙事分析：全局摘要、叙事聚类、张力矩阵
- 返回统一的 ServiceResult

输入：articles: List[Dict[str, Any]] — 新闻列表
输出：ServiceResult(success, data={global_summary, clusters, tension_matrix}, error=...)
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fzq_ai.domain.models import ServiceResult
from fzq_ai.llm.llm_router import LLMRouter
from fzq_ai.utils.logger import get_logger

logger = get_logger(__name__)

LLM_TIMEOUT_SEC = 90

class NarrativePipeline:
    """

    """

    def __init__(self, llm: Optional[LLMRouter] = None) -> None:
        self.llm: LLMRouter = llm or LLMRouter()
        self.max_articles: int = 20

    # ── 步骤1：全局总结 ──────────────────────────────────────

    def build_global_summary(self, articles: List[Dict[str, Any]]) -> str:
        """

        """
        items: List[Dict[str, Any]] = articles[: self.max_articles]
        if not items:
            return "（无新闻数据可供分析）"

        titles: List[str] = [a.get("title", "") for a in items]
        summaries: List[str] = [a.get("summary", "") for a in items]

            "你是一名地缘政治与国际新闻分析师。下面是若干新闻标题与摘要，"
            "请你生成一段"全球局势总结"（Global Summary），要求：\n\n"
            "- 用中文撰写\n"
            "- 结构清晰，分 2–4 段\n"
            "- 覆盖主要地区（欧美、中东、亚太等）\n"
            "- 强调趋势、风险点和潜在演变方向\n\n"

        try:
            result: str = self.llm.run(prompt)
            return result.strip()
        except Exception as e:
            return f"（全局总结生成失败：{e}）"

    # ── 步骤2：叙事聚类 ───────────────────────────────────────

    def build_narrative_clusters(
        self, articles: List[Dict[str, Any]]
        """

        """
                "title": a.get("title", ""),
                "summary": a.get("summary", ""),
                "source": a.get("source_name", a.get("source", "")),
            }
            for a in articles[: self.max_articles]

        if not items:
            return []

            "你是一名叙事分析专家。请根据以下新闻（标题 + 摘要），"
            "进行"叙事聚类"（Narrative Clustering）。\n\n"
            "要求：\n"
            "1. 按叙事主题分组，例如：美中竞争、中东冲突、能源与市场、"
            "社会抗议与选举\n"
            "2. 每个聚类给出：cluster_name（简短中文标题）、"
            "items（属于该叙事的新闻标题列表）\n\n"
            "请严格输出 JSON 格式，例如：\n"
            "[\n"
            '  {"cluster_name": "中东局势升级", "items": ["标题1", "标题2", ...]},\n'
            "  ...\n"
            "]\n\n"

        try:
            text: str = self.llm.run(prompt)
            clusters: List[Dict[str, Any]] = json.loads(text)
            return clusters
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"[NarrativePipeline] 叙事聚类解析失败: {e}")
            return []

    # ── 步骤3：张力矩阵 ───────────────────────────────────────

    def build_tension_matrix(
        self, articles: List[Dict[str, Any]]
        """

        """
                "title": a.get("title", ""),
                "summary": a.get("summary", ""),
                "source": a.get("source_name", a.get("source", "")),
            }
            for a in articles[: self.max_articles]

        if not items:
            return []

            "你是一名国际关系分析师。请从以下新闻中，提取"
            ""关键行为体之间的张力关系"（Tension Matrix）。\n\n"
            "要求：\n"
            "1. 找出存在明显对立、冲突、博弈的行为体（国家、组织、阵营等）\n"
            "2. 每条关系包含：actor1、actor2、description（中文一句话描述）\n\n"
            "请严格输出 JSON 数组，例如：\n"
            "[\n"
            '  {"actor1": "以色列", "actor2": "哈马斯", '
            '"description": "加沙地带军事冲突持续升级"},\n'
            "  ...\n"
            "]\n\n"

        try:
            text: str = self.llm.run(prompt)
            matrix: List[Dict[str, Any]] = json.loads(text)
            return matrix
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"[NarrativePipeline] 张力矩阵解析失败: {e}")
            return []

    # ── 主入口 ────────────────────────────────────────────────

    def run(
        self, articles: Optional[List[Dict[str, Any]]] = None
        """

        """
        # 兼容字符串输入（旧版 UI 传入 text 而非 articles）
        if isinstance(articles, str):
            text: str = articles
                "[NarrativePipeline] 收到字符串输入，"
                "将作为主题进行简化分析"
            try:
                result: str = self.llm.run(
                    f"请对主题 '{text}' 进行简要叙事分析（中文，200字以内）"
                return ServiceResult.ok(
                    {
                        "global_summary": result.strip(),
                        "clusters": [],
                        "tension_matrix": [],
            except Exception as e:
                return ServiceResult.fail(f"叙事分析失败: {e}")

        if articles is None:

        try:
            summary: str = self.build_global_summary(articles)
            clusters: List[Dict[str, Any]] = self.build_narrative_clusters(
                articles
            tension_matrix: List[Dict[str, Any]] = self.build_tension_matrix(
                articles

            return ServiceResult.ok(
                {
                    "global_summary": summary,
                    "clusters": clusters,
                    "tension_matrix": tension_matrix,
        except Exception as e:
            return ServiceResult.fail(f"叙事分析失败: {e}")
