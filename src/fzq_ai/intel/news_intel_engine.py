# fzq_ai/intel/news_intel_engine.py

import asyncio
import json
import re
import warnings
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

    async def search_structured(self, query: str, articles: List[Article]) -> Dict[str, Any]:
        """
        异步版本：结构化新闻情报搜索。

        注意：旧同步接口 `search_structured` 已被替换为 async 版本。
        调用方（如 FastAPI 端点）可直接 await；传统同步代码应使用：
            asyncio.run(engine.search_structured(...))
        或升级为 async 调用链。
        """
        context_lines = [
            f"{i+1}. [{a.source_name}] {a.title_original}"
            for i, a in enumerate(articles[:20])
        ]
        context = "\n".join(context_lines)

        # 使用模板
        prompt = NEWS_INTEL_TEMPLATE.render(query=query, context=context)

        raw = await self.llm_router.route("news_intel", prompt)

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

    # 兼容旧同步接口（已废弃，将在 v5.0 移除）
    def search_structured_sync(self, query: str, articles: List[Article]) -> Dict[str, Any]:
        """
        ⚠️ 已废弃：请使用 `await search_structured()` 异步版本。
        在已运行的事件循环中调用 asyncio.run() 会引发 RuntimeError。
        """
        warnings.warn(
            "search_structured_sync is deprecated. Use `await search_structured()` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return asyncio.run(self.search_structured(query, articles))
