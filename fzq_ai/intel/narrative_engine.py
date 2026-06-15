# fzq_ai/intel/narrative_engine.py

from __future__ import annotations
from typing import List, Dict
from textwrap import dedent

from fzq_ai.intel.models import Article, Narrative
from fzq_ai.llm.llm_router import LLMRouter

class NarrativeEngine:
    """
    """

    def __init__(self) -> None:
        self.router = LLMRouter()

    async def generate_async(self, articles: List[Article], event_id: str) -> Narrative:
        """
        """

        corpus = self._build_corpus(articles)

        prompt = self._build_prompt(corpus)

        # 用 DeepSeek 优先，失败再 fallback
        text = await self._run_with_fallback(prompt)

        parsed = self._parse_llm_output(text)

        return Narrative(
            event_id=event_id,

    # 兼容旧同步接口（news_intel_service 目前是同步风格）
    def generate(self, articles: List[Article], event_id: str) -> Narrative:
        import asyncio

        return asyncio.run(self.generate_async(articles, event_id))

    # ---------------------------------------------------------
    # 构造语料
    # ---------------------------------------------------------
    def _build_corpus(self, articles: List[Article]) -> str:
        chunks = []
        for a in articles:
        return "\n\n".join(chunks)

    # ---------------------------------------------------------
    # 构造 Prompt
    # ---------------------------------------------------------
    def _build_prompt(self, corpus: str) -> str:
        return dedent(f"""
            你是一名地缘政治情报分析员，任务是从多来源新闻中提炼多阵营叙事。

              "narratives": {{
                "western": "...",
                "china": "...",
                "russia": "...",
                "global_south": "..."
              "consensus_facts": [
                "fact 1",
                "fact 2"
              "contested_claims": [
                "claim 1",
                "claim 2"
              "missing_perspectives": [
                "missing 1",
                "missing 2"
            """)

    # ---------------------------------------------------------
    # LLM 调用（带 fallback）
    # ---------------------------------------------------------
    async def _run_with_fallback(self, prompt: str) -> str:
        for provider in ["deepseek", "openai", "gemini"]:
            try:
                return await self.router.run(prompt, model=provider)
            except Exception:
        # 最终兜底
        return """
          "narratives": {
            "western": "LLM 调用失败，使用兜底叙事。",
            "china": "LLM 调用失败，使用兜底叙事。",
            "russia": "LLM 调用失败，使用兜底叙事。",
            "global_south": "LLM 调用失败，使用兜底叙事。"
          "consensus_facts": [],
          "contested_claims": [],
          "missing_perspectives": []
        """

    # ---------------------------------------------------------
    # 解析 LLM 输出
    # ---------------------------------------------------------
    def _parse_llm_output(self, text: str) -> Dict[str, object]:
        import json

        try:
        except Exception:
            # 如果 LLM 没按 JSON 来，做个粗糙兜底
            return {
                "narratives": {
                    "western": text,
                    "china": "解析失败。",
                    "russia": "解析失败。",
                    "global_south": "解析失败。",
                "consensus": [],
                "contested": [],
                "missing": [],

        # 保证四个阵营都有键
        for b in self.BLOCS:

        return {
            "narratives": narratives,
            "consensus": consensus,
            "contested": contested,
            "missing": missing,
