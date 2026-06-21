# fzq_ai/intel/news_intel_engine.py

import asyncio
import json
import re
from typing import List, Dict, Any

from fzq_ai.intel.schemas import IntelSchema
from fzq_ai.domain.models import Article
from fzq_ai.prompts.news_intel_prompt import NEWS_INTEL_TEMPLATE


class NewsIntelEngine:
    """
    新闻情报结构化引擎（增强版）
    - 使用 PromptTemplate（避免字符串拼接错误）
    - JSON mode + Pydantic Schema
    """

    def __init__(self, llm_router=None):
        self.llm_router = llm_router

    def search_structured(self, query: str, articles: List[Article]) -> Dict[str, Any]:
        context_lines = [
            f"{i+1}. [{a.source_name}] {a.title_original}"
            for i, a in enumerate(articles[:20])
        ]
        context = "\n".join(context_lines)

        # ⭐ 使用模板
        prompt = NEWS_INTEL_TEMPLATE.render(query=query, context=context)

        raw = asyncio.run(self.llm_router.route("news_intel", prompt))

        # JSON 解析（略，保持之前版本）
        try:
            data = json.loads(raw)
            return IntelSchema(**data).dict()
        except Exception:
            pass

        try:
            match = re.search(r"\{[\s\S]+\}", raw)
            if match:
                data = json.loads(match.group(0))
                return IntelSchema(**data).dict()
        except Exception:
            pass

        return {
            "language": "unknown",
            "regions": [],
            "events": [],
            "stats": {},
        }
