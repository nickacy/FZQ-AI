# fzq_ai/intel/news_intel_engine.py

import asyncio
import json
import re
from typing import List, Dict, Any

from fzq_ai.intel.schemas import IntelSchema
from fzq_ai.domain.models import Article


class NewsIntelEngine:
    """
    新闻情报结构化引擎（增强版）
    - 保留旧逻辑
    - 新增 JSON mode 支持
    - 新增 Pydantic Schema 校验
    - 新增 Markdown code block 提取
    - 新增 fallback
    """

    def __init__(self, llm_router=None):
        self.llm_router = llm_router

    def search_structured(self, query: str, articles: List[Article]) -> Dict[str, Any]:
        prompt = self._build_prompt(query, articles)

        # 调用 LLM（JSON mode）
        raw = asyncio.run(self.llm_router.route("news_intel", prompt))

        # ---------------------------------------------------------
        # 1) 尝试直接解析 JSON
        # ---------------------------------------------------------
        try:
            data = json.loads(raw)
            return IntelSchema(**data).dict()
        except Exception:
            pass

        # ---------------------------------------------------------
        # 2) 尝试从 Markdown code block 中提取 JSON
        # ---------------------------------------------------------
        try:
            match = re.search(r"\{[\s\S]+\}", raw)
            if match:
                data = json.loads(match.group(0))
                return IntelSchema(**data).dict()
        except Exception:
            pass

        # ---------------------------------------------------------
        # 3) fallback：返回空结构（不抛异常）
        # ---------------------------------------------------------
        return {
            "language": "unknown",
            "regions": [],
            "events": [],
            "stats": {},
        }

    # ---------------------------------------------------------
    # Prompt 构建（旧逻辑保留）
    # ---------------------------------------------------------
    def _build_prompt(self, query: str, articles: List[Article]) -> str:
        context_lines = []
        for i, a in enumerate(articles[:20], 1):
            context_lines.append(f"{i}. [{a.source_name}] {a.title_original}")

        context = "\n".join(context_lines)

        return (
            f"你是一名情报结构化分析专家，请根据以下新闻标题生成结构化 JSON：\n"
            f"主题：{query}\n\n"
            f"{context}\n\n"
            f"请输出 JSON，字段包括：\n"
            f"- language: str\n"
            f"- regions: List[str]\n"
            f"- events: List[{{title, date, region, summary}}]\n"
            f"- stats: Dict\n"
        )
